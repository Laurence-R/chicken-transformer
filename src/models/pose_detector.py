"""Abstract base class for pose detectors.

Defines the interface for pose detection implementations, supporting both
TensorRT (Jetson) and Mock (WSL) backends.
"""
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
from ..utils.data_structures import PoseData


class PoseDetector(ABC):
    """Abstract base class for pose detection.
    
    Provides unified interface for different pose detection backends:
    - TensorRTPoseDetector: YOLOv8-Pose with TensorRT acceleration (Jetson)
    - MockPoseDetector: Synthetic pose data for development (WSL)
    
    Contract:
        - initialize() must be called before detect()
        - detect() returns None if no person detected or processing failed
        - release() must be called before program termination
        - Thread-safety: Single instance not thread-safe, use locks for multi-threading
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize detector (load model, allocate resources).
        
        Returns:
            True if initialization successful, False otherwise
            
        Raises:
            RuntimeError: If model cannot be loaded or TensorRT engine init fails
            
        Postconditions:
            - TensorRT: First call takes 3-10s (engine loading), subsequent <1s
            - Mock: Returns immediately
        """
        pass
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> Optional[PoseData]:
        """Perform pose detection on single frame.
        
        Args:
            frame: BGR image (H x W x 3), dtype=uint8
                  Any resolution (automatically scaled to model input size)
                  
        Returns:
            PoseData with 17 COCO keypoints if person detected, else None
            
        Preconditions:
            - initialize() must have been called successfully
            - frame must be valid BGR numpy array
            
        Postconditions:
            - If returns non-None, PoseData.is_valid() must be True (>=8 visible keypoints)
            - Processing time <50ms (TensorRT) or <10ms (Mock) at 95th percentile
            - Keypoint coordinates in original frame coordinate space (not normalized)
            - Confidence <0.3 keypoints marked as not visible
            
        Performance:
            - TensorRT: <50ms per frame (640x640 input, FP16)
            - Mock: <10ms per frame
        """
        pass
    
    @abstractmethod
    def release(self) -> None:
        """Release detector resources (CUDA memory, TensorRT context).
        
        Requirements:
            - Idempotent: Multiple calls must not error
            - Must be called before program termination
            - After calling, detect() must not be called again
        """
        pass
    
    @abstractmethod
    def get_input_size(self) -> tuple[int, int]:
        """Get model input dimensions.
        
        Returns:
            (width, height) tuple, e.g., (640, 640)
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """Get model metadata.
        
        Returns:
            Dictionary with keys:
                - "model_name": str (e.g., "yolov8n-pose")
                - "backend": str ("tensorrt" | "mock")
                - "precision": str ("fp16" | "fp32" | "none")
                - "avg_inference_time_ms": float
        """
        pass
