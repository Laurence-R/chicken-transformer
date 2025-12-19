"""Mock pose detector for WSL development without GPU/TensorRT.

Provides synthetic pose data for testing game logic without real camera input.
Supports different pose modes (standing, squatting, jumping) and configurable noise.
"""
import time
import numpy as np
from typing import Optional
from .pose_detector import PoseDetector
from ..utils.data_structures import PoseData, Keypoint, BoundingBox
from ..utils.constants import KEYPOINT_INDICES


class MockPoseDetector(PoseDetector):
    """Mock pose detector for development and testing.
    
    Generates synthetic pose data without requiring GPU/camera.
    Useful for WSL development, unit tests, and state machine testing.
    
    Modes:
        - "standing": Upright neutral pose
        - "squatting": Knees bent ~90°, hips lowered
        - "jumping": Elevated position with raised arms
        - "pushup_up": Plank position
        - "pushup_down": Lowered pushup position
    """
    
    def __init__(
        self,
        mode: str = "standing",
        noise_level: float = 0.0,
        confidence: float = 0.9
    ):
        """Initialize mock detector.
        
        Args:
            mode: Pose mode ("standing", "squatting", "jumping", "pushup_up", "pushup_down")
            noise_level: Random noise to add to keypoints (0.0-1.0), pixels
            confidence: Keypoint confidence score (0.0-1.0)
        """
        valid_modes = ["standing", "squatting", "jumping", "pushup_up", "pushup_down"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Valid modes: {valid_modes}")
        
        self.mode = mode
        self.noise_level = noise_level
        self.confidence = confidence
        self.frame_count = 0
        self.initialized = False
        self.start_time = time.time()
        
    def initialize(self) -> bool:
        """Initialize mock detector (no-op for mock).
        
        Returns:
            True (always succeeds)
        """
        self.initialized = True
        self.start_time = time.time()
        return True
    
    def detect(self, frame: np.ndarray) -> Optional[PoseData]:
        """Generate synthetic pose data based on current mode.
        
        Args:
            frame: Input frame (unused, for interface compatibility)
            
        Returns:
            PoseData with synthetic keypoints for current mode
        """
        if not self.initialized:
            raise RuntimeError("MockPoseDetector not initialized. Call initialize() first.")
        
        self.frame_count += 1
        timestamp = time.time()
        
        # Generate keypoints based on mode
        if self.mode == "standing":
            keypoints = self._generate_standing_pose()
        elif self.mode == "squatting":
            keypoints = self._generate_squatting_pose()
        elif self.mode == "jumping":
            keypoints = self._generate_jumping_pose()
        elif self.mode == "pushup_up":
            keypoints = self._generate_pushup_up_pose()
        elif self.mode == "pushup_down":
            keypoints = self._generate_pushup_down_pose()
        else:
            raise ValueError(f"Invalid mode: {self.mode}")
        
        # Add noise if configured
        if self.noise_level > 0:
            keypoints = self._add_noise(keypoints)
        
        # Generate bounding box from keypoints
        bbox = self._generate_bbox(keypoints)
        
        return PoseData(
            keypoints=keypoints,
            bbox=bbox,
            confidence=self.confidence,
            frame_id=self.frame_count,
            timestamp=timestamp
        )
    
    def release(self) -> None:
        """Release resources (no-op for mock)."""
        self.initialized = False
        self.frame_count = 0
    
    def get_input_size(self) -> tuple[int, int]:
        """Get mock input size.
        
        Returns:
            (640, 640) to match YOLOv8n-Pose
        """
        return (640, 640)
    
    def get_model_info(self) -> dict:
        """Get mock model metadata.
        
        Returns:
            Dictionary with mock backend info
        """
        elapsed_time = time.time() - self.start_time
        avg_inference_time = (elapsed_time / self.frame_count * 1000) if self.frame_count > 0 else 0.0
        
        return {
            "model_name": f"mock-{self.mode}",
            "backend": "mock",
            "precision": "none",
            "avg_inference_time_ms": avg_inference_time
        }
    
    def set_mode(self, mode: str) -> None:
        """Change pose mode dynamically.
        
        Args:
            mode: New pose mode
        """
        valid_modes = ["standing", "squatting", "jumping", "pushup_up", "pushup_down"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Valid modes: {valid_modes}")
        self.mode = mode
    
    def _generate_standing_pose(self) -> list[Keypoint]:
        """Generate keypoints for standing upright pose."""
        # Centered person in 640x640 frame
        keypoints_raw = {
            'nose': (320, 100, self.confidence),
            'left_eye': (310, 90, self.confidence),
            'right_eye': (330, 90, self.confidence),
            'left_ear': (300, 100, self.confidence),
            'right_ear': (340, 100, self.confidence),
            'left_shoulder': (280, 180, self.confidence),
            'right_shoulder': (360, 180, self.confidence),
            'left_elbow': (250, 280, self.confidence),
            'right_elbow': (390, 280, self.confidence),
            'left_wrist': (240, 350, self.confidence),
            'right_wrist': (400, 350, self.confidence),
            'left_hip': (290, 350, self.confidence),
            'right_hip': (350, 350, self.confidence),
            'left_knee': (285, 480, self.confidence),
            'right_knee': (355, 480, self.confidence),
            'left_ankle': (280, 600, self.confidence),
            'right_ankle': (360, 600, self.confidence),
        }
        return self._keypoints_dict_to_list(keypoints_raw)
    
    def _generate_squatting_pose(self) -> list[Keypoint]:
        """Generate keypoints for squatting pose (knees ~90°)."""
        keypoints_raw = {
            'nose': (320, 180, self.confidence),
            'left_eye': (310, 170, self.confidence),
            'right_eye': (330, 170, self.confidence),
            'left_ear': (300, 180, self.confidence),
            'right_ear': (340, 180, self.confidence),
            'left_shoulder': (280, 260, self.confidence),
            'right_shoulder': (360, 260, self.confidence),
            'left_elbow': (250, 360, self.confidence),
            'right_elbow': (390, 360, self.confidence),
            'left_wrist': (240, 430, self.confidence),
            'right_wrist': (400, 430, self.confidence),
            'left_hip': (290, 430, self.confidence),  # Hips lowered
            'right_hip': (350, 430, self.confidence),
            'left_knee': (285, 500, self.confidence),  # Knees bent
            'right_knee': (355, 500, self.confidence),
            'left_ankle': (280, 580, self.confidence),
            'right_ankle': (360, 580, self.confidence),
        }
        return self._keypoints_dict_to_list(keypoints_raw)
    
    def _generate_jumping_pose(self) -> list[Keypoint]:
        """Generate keypoints for jumping pose with raised arms."""
        keypoints_raw = {
            'nose': (320, 80, self.confidence),
            'left_eye': (310, 70, self.confidence),
            'right_eye': (330, 70, self.confidence),
            'left_ear': (300, 80, self.confidence),
            'right_ear': (340, 80, self.confidence),
            'left_shoulder': (280, 160, self.confidence),
            'right_shoulder': (360, 160, self.confidence),
            'left_elbow': (250, 100, self.confidence),  # Arms raised
            'right_elbow': (390, 100, self.confidence),
            'left_wrist': (240, 50, self.confidence),   # Hands above head
            'right_wrist': (400, 50, self.confidence),
            'left_hip': (290, 330, self.confidence),   # Body elevated
            'right_hip': (350, 330, self.confidence),
            'left_knee': (285, 430, self.confidence),
            'right_knee': (355, 430, self.confidence),
            'left_ankle': (280, 550, self.confidence),  # Feet off ground
            'right_ankle': (360, 550, self.confidence),
        }
        return self._keypoints_dict_to_list(keypoints_raw)
    
    def _generate_pushup_up_pose(self) -> list[Keypoint]:
        """Generate keypoints for pushup plank position."""
        keypoints_raw = {
            'nose': (320, 300, self.confidence),
            'left_eye': (310, 290, self.confidence),
            'right_eye': (330, 290, self.confidence),
            'left_ear': (300, 300, self.confidence),
            'right_ear': (340, 300, self.confidence),
            'left_shoulder': (280, 340, self.confidence),
            'right_shoulder': (360, 340, self.confidence),
            'left_elbow': (250, 380, self.confidence),
            'right_elbow': (390, 380, self.confidence),
            'left_wrist': (230, 420, self.confidence),
            'right_wrist': (410, 420, self.confidence),
            'left_hip': (290, 420, self.confidence),
            'right_hip': (350, 420, self.confidence),
            'left_knee': (285, 500, self.confidence),
            'right_knee': (355, 500, self.confidence),
            'left_ankle': (280, 580, self.confidence),
            'right_ankle': (360, 580, self.confidence),
        }
        return self._keypoints_dict_to_list(keypoints_raw)
    
    def _generate_pushup_down_pose(self) -> list[Keypoint]:
        """Generate keypoints for lowered pushup position."""
        keypoints_raw = {
            'nose': (320, 350, self.confidence),
            'left_eye': (310, 340, self.confidence),
            'right_eye': (330, 340, self.confidence),
            'left_ear': (300, 350, self.confidence),
            'right_ear': (340, 350, self.confidence),
            'left_shoulder': (280, 390, self.confidence),
            'right_shoulder': (360, 390, self.confidence),
            'left_elbow': (250, 410, self.confidence),  # Elbows bent
            'right_elbow': (390, 410, self.confidence),
            'left_wrist': (230, 420, self.confidence),
            'right_wrist': (410, 420, self.confidence),
            'left_hip': (290, 430, self.confidence),    # Closer to ground
            'right_hip': (350, 430, self.confidence),
            'left_knee': (285, 510, self.confidence),
            'right_knee': (355, 510, self.confidence),
            'left_ankle': (280, 590, self.confidence),
            'right_ankle': (360, 590, self.confidence),
        }
        return self._keypoints_dict_to_list(keypoints_raw)
    
    def _keypoints_dict_to_list(self, keypoints_dict: dict) -> list[Keypoint]:
        """Convert keypoint dictionary to ordered list.
        
        Args:
            keypoints_dict: Dict mapping keypoint names to (x, y, confidence)
            
        Returns:
            List of 17 Keypoint objects in COCO order
        """
        keypoints = []
        for name in sorted(KEYPOINT_INDICES.keys(), key=lambda k: KEYPOINT_INDICES[k]):
            x, y, conf = keypoints_dict[name]
            keypoints.append(Keypoint(x=x, y=y, confidence=conf))
        return keypoints
    
    def _add_noise(self, keypoints: list[Keypoint]) -> list[Keypoint]:
        """Add random noise to keypoint positions.
        
        Args:
            keypoints: Original keypoints
            
        Returns:
            Keypoints with added Gaussian noise
        """
        noisy_keypoints = []
        for kp in keypoints:
            noise_x = np.random.normal(0, self.noise_level)
            noise_y = np.random.normal(0, self.noise_level)
            noisy_keypoints.append(Keypoint(
                x=max(0, kp.x + noise_x),
                y=max(0, kp.y + noise_y),
                confidence=kp.confidence
            ))
        return noisy_keypoints
    
    def _generate_bbox(self, keypoints: list[Keypoint]) -> BoundingBox:
        """Generate bounding box from keypoints.
        
        Args:
            keypoints: List of keypoints
            
        Returns:
            BoundingBox containing all visible keypoints
        """
        visible_keypoints = [kp for kp in keypoints if kp.visible]
        if not visible_keypoints:
            # Default box if no visible keypoints
            return BoundingBox(x1=0, y1=0, x2=640, y2=640)
        
        x_coords = [kp.x for kp in visible_keypoints]
        y_coords = [kp.y for kp in visible_keypoints]
        
        x1 = max(0, min(x_coords) - 10)
        y1 = max(0, min(y_coords) - 10)
        x2 = min(640, max(x_coords) + 10)
        y2 = min(640, max(y_coords) + 10)
        
        return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
