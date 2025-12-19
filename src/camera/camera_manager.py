"""Camera manager for handling video capture."""

import time
from typing import Optional, Tuple

import cv2
import numpy as np

from .gstreamer_pipeline import gstreamer_pipeline


class CameraManager:
    """Manages video capture from CSI or USB cameras."""

    def __init__(
        self, camera_type: str = "usb", width: int = 1280, height: int = 720, fps: int = 30
    ):
        self.camera_type = camera_type
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.frame_count = 0

    def initialize(self) -> bool:
        """Initialize the camera."""
        print(f"Initializing {self.camera_type} camera...")

        if self.camera_type == "csi":
            pipeline = gstreamer_pipeline(
                capture_width=self.width,
                capture_height=self.height,
                display_width=self.width,
                display_height=self.height,
                framerate=self.fps,
                flip_method=0,
            )
            print(f"GStreamer pipeline: {pipeline}")
            self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        elif self.camera_type == "usb":
            # Try index 0, then 1
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(1)

            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        else:
            print(f"Unknown camera type: {self.camera_type}")
            return False

        if self.cap and self.cap.isOpened():
            print("Camera initialized successfully.")
            return True
        else:
            print("Failed to open camera.")
            return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera.

        Returns:
            (success, frame) tuple
        """
        if not self.cap or not self.cap.isOpened():
            # Attempt reconnection logic could go here
            return False, None

        ret, frame = self.cap.read()

        if not ret:
            # Simple retry logic for transient failures
            print("Warning: Failed to read frame, retrying...")
            for _ in range(3):
                time.sleep(0.1)
                ret, frame = self.cap.read()
                if ret:
                    break

        if ret:
            self.frame_count += 1
        return ret, frame

    def release(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
