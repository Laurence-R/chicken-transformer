"""TensorRT Pose Detector implementation for Jetson Orin Nano.

Requires:
    - tensorrt
    - pycuda
    - numpy
"""

import os
import time
from typing import Optional, Tuple

import numpy as np

try:
    import pycuda.autoinit  # noqa: F401
    import pycuda.driver as cuda
    import tensorrt as trt
except ImportError:
    trt = None
    cuda = None
    # This is expected on WSL/Non-Jetson environments
    pass

from ..utils.data_structures import BoundingBox, Keypoint, PoseData
from .pose_detector import PoseDetector


class TensorRTPoseDetector(PoseDetector):
    """YOLOv8-Pose detector using TensorRT engine."""

    def __init__(
        self, engine_path: str, confidence_threshold: float = 0.5, nms_threshold: float = 0.45
    ):
        self.engine_path = engine_path
        self.conf_thres = confidence_threshold
        self.nms_thres = nms_threshold

        self.logger = None
        self.runtime = None
        self.engine = None
        self.context = None
        self.inputs = []
        self.outputs = []
        self.bindings = []
        self.stream = None
        self.use_v3 = False

        self.input_shape = (640, 640)  # Default YOLOv8 input
        self.initialized = False

    def initialize(self) -> bool:
        """Load TensorRT engine and allocate buffers."""
        if trt is None or cuda is None:
            print(
                "Error: TensorRT or PyCUDA not installed. Cannot initialize TensorRTPoseDetector."
            )
            return False

        if not os.path.exists(self.engine_path):
            print(f"Error: Engine file not found at {self.engine_path}")
            return False

        try:
            self.logger = trt.Logger(trt.Logger.WARNING)
            self.runtime = trt.Runtime(self.logger)

            print(f"Loading engine from {self.engine_path}...")
            with open(self.engine_path, "rb") as f:
                self.engine = self.runtime.deserialize_cuda_engine(f.read())

            self.context = self.engine.create_execution_context()
            self.stream = cuda.Stream()

            # Check for TensorRT 10+ API
            self.use_v3 = hasattr(self.context, "execute_async_v3")

            # Allocate buffers
            if hasattr(self.engine, "num_io_tensors"):
                # TensorRT 8.5+ / 10.0+ API
                for i in range(self.engine.num_io_tensors):
                    name = self.engine.get_tensor_name(i)
                    shape = self.engine.get_tensor_shape(name)
                    dtype = trt.nptype(self.engine.get_tensor_dtype(name))

                    # Handle dynamic shapes if necessary
                    if shape[0] == -1:
                        shape = (1,) + shape[1:]

                    size = trt.volume(shape) * np.dtype(dtype).itemsize

                    # Allocate host and device memory
                    try:
                        host_mem = cuda.pagelocked_empty(trt.volume(shape), dtype)
                        device_mem = cuda.mem_alloc(size)
                    except cuda.MemoryError:
                        print(
                            f"Error: GPU Out of Memory when allocating buffer for {name} (size: {size} bytes)"
                        )
                        return False

                    # For v3, we set address
                    if self.use_v3:
                        self.context.set_tensor_address(name, int(device_mem))
                    else:
                        self.bindings.append(int(device_mem))

                    if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                        self.inputs.append(
                            {"host": host_mem, "device": device_mem, "shape": shape, "name": name}
                        )
                    else:
                        self.outputs.append(
                            {"host": host_mem, "device": device_mem, "shape": shape, "name": name}
                        )
            else:
                # Legacy API
                for binding in self.engine:
                    # Get binding index and shape
                    self.engine.get_binding_index(binding)
                    shape = self.engine.get_binding_shape(binding)
                    dtype = trt.nptype(self.engine.get_binding_dtype(binding))

                    # Handle dynamic shapes if necessary (though we exported with dynamic=False)
                    if shape[0] == -1:
                        shape = (1,) + shape[1:]

                    size = trt.volume(shape) * np.dtype(dtype).itemsize

                    # Allocate host and device memory
                    host_mem = cuda.pagelocked_empty(trt.volume(shape), dtype)
                    device_mem = cuda.mem_alloc(size)

                    self.bindings.append(int(device_mem))

                    if self.engine.binding_is_input(binding):
                        self.inputs.append({"host": host_mem, "device": device_mem, "shape": shape})
                    else:
                        self.outputs.append(
                            {"host": host_mem, "device": device_mem, "shape": shape}
                        )

            self.initialized = True
            print("TensorRT Engine initialized successfully.")
            return True

        except Exception as e:
            print(f"Failed to initialize TensorRT engine: {e}")
            import traceback

            traceback.print_exc()
            return False

    def detect(self, frame: np.ndarray) -> Optional[PoseData]:
        """Perform inference on a frame."""
        if not self.initialized:
            return None

        # 1. Preprocess
        input_image, ratio, dwdh = self._preprocess(frame)

        # Copy to page-locked memory
        np.copyto(self.inputs[0]["host"], input_image.ravel())

        # 2. Inference
        # Transfer input data to the GPU
        cuda.memcpy_htod_async(self.inputs[0]["device"], self.inputs[0]["host"], self.stream)

        # Run inference
        if self.use_v3:
            self.context.execute_async_v3(stream_handle=self.stream.handle)
        else:
            self.context.execute_async_v2(bindings=self.bindings, stream_handle=self.stream.handle)

        # Transfer predictions back from the GPU
        cuda.memcpy_dtoh_async(self.outputs[0]["host"], self.outputs[0]["device"], self.stream)

        # Synchronize the stream
        self.stream.synchronize()

        # 3. Postprocess
        output = self.outputs[0]["host"].reshape(self.outputs[0]["shape"])
        # Output shape is typically (1, 56, 8400) for YOLOv8-pose

        pose_data = self._postprocess(output, ratio, dwdh, frame.shape[:2])

        # Add timing info if needed
        # inference_time = (time.time() - start_time) * 1000

        return pose_data

    def release(self) -> None:
        """Free CUDA resources."""
        if self.context:
            self.context = None
        if self.engine:
            self.engine = None
        if self.runtime:
            self.runtime = None

        # Free device memory
        # PyCUDA handles this automatically when objects go out of scope,
        # but explicit cleanup is good practice if we hold references.
        self.inputs = []
        self.outputs = []
        self.bindings = []
        self.stream = None

    def get_input_size(self) -> Tuple[int, int]:
        return self.input_shape

    def get_model_info(self) -> dict:
        return {
            "model_name": "yolov8n-pose",
            "backend": "tensorrt",
            "precision": "fp16",  # Assuming we export with fp16
        }

    def _preprocess(
        self, img: np.ndarray
    ) -> Tuple[np.ndarray, Tuple[float, float], Tuple[float, float]]:
        """Resize and pad image to model input size."""
        shape = img.shape[:2]  # current shape [height, width]
        new_shape = self.input_shape

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            import cv2

            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))

        import cv2

        img = cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )  # add border

        # HWC to CHW, BGR to RGB
        img = img.transpose((2, 0, 1))[::-1]
        img = np.ascontiguousarray(img)

        img = img.astype(np.float32)
        img /= 255.0  # 0 - 255 to 0.0 - 1.0

        return img, ratio, (dw, dh)

    def _postprocess(self, output, ratio, dwdh, orig_shape) -> Optional[PoseData]:
        """Parse YOLOv8 output to PoseData."""
        # Output shape: (1, 56, 8400)
        # 56 channels: 4 box + 1 conf + 17*3 keypoints

        predictions = np.squeeze(output).T  # (8400, 56)

        # Filter by confidence
        scores = predictions[:, 4]
        mask = scores > self.conf_thres
        predictions = predictions[mask]

        if len(predictions) == 0:
            return None

        # NMS (Non-Maximum Suppression)
        # Simple implementation or use cv2.dnn.NMSBoxes
        boxes = predictions[:, :4]
        scores = predictions[:, 4]

        # Convert xywh to xyxy
        boxes_xyxy = np.copy(boxes)
        boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2  # x1
        boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2  # y1
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2  # x2
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2  # y2

        import cv2

        indices = cv2.dnn.NMSBoxes(
            boxes_xyxy.tolist(), scores.tolist(), self.conf_thres, self.nms_thres
        )

        if len(indices) == 0:
            return None

        # Pick the best detection (closest to center)
        # indices is a list/array of indices kept by NMS

        best_idx = -1
        min_dist_sq = float("inf")

        # Model input center
        mcx, mcy = self.input_shape[1] / 2, self.input_shape[0] / 2

        for i in indices:
            # Handle different cv2 versions return types
            idx = int(i) if np.isscalar(i) else int(i[0])

            pred = predictions[idx]
            # YOLO format: cx, cy, w, h
            bcx, bcy = pred[0], pred[1]

            # Calculate squared distance to center
            dist_sq = (bcx - mcx) ** 2 + (bcy - mcy) ** 2

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_idx = idx

        best_pred = predictions[best_idx]

        # Extract data
        bbox_raw = best_pred[:4]  # xywh
        # conf = best_pred[4]
        kps_raw = best_pred[5:]  # 51 values

        # Rescale to original image
        dw, dh = dwdh
        rx, ry = ratio

        # Bbox rescaling
        cx = (bbox_raw[0] - dw) / rx
        cy = (bbox_raw[1] - dh) / ry
        w = bbox_raw[2] / rx
        h = bbox_raw[3] / ry

        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2

        bbox = BoundingBox(
            x1=max(0, x1), y1=max(0, y1), x2=min(orig_shape[1], x2), y2=min(orig_shape[0], y2)
        )

        # Keypoints rescaling
        keypoints = []
        # Map YOLO keypoint order to our Keypoint class
        # YOLOv8 Pose uses COCO 17 keypoints, same as our KEYPOINT_INDICES

        for i in range(17):
            kx = (kps_raw[i * 3] - dw) / rx
            ky = (kps_raw[i * 3 + 1] - dh) / ry
            kconf = kps_raw[i * 3 + 2]

            keypoints.append(Keypoint(x=max(0, kx), y=max(0, ky), confidence=kconf))

        return PoseData(
            keypoints=keypoints,
            bbox=bbox,
            confidence=float(best_pred[4]),
            frame_id=0,  # TODO: Pass frame ID
            timestamp=time.time(),
        )
