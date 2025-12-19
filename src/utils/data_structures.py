"""Core data structures for pose estimation and geometry."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .constants import KEYPOINT_INDICES


@dataclass
class Keypoint:
    """Represents a single COCO keypoint with position and confidence.

    Attributes:
        x: X coordinate in pixels (0-based)
        y: Y coordinate in pixels (0-based)
        confidence: Detection confidence score (0.0-1.0)
        visible: Whether keypoint is visible (confidence > 0.5)
    """

    x: float
    y: float
    confidence: float
    visible: bool = False

    def __post_init__(self):
        """Validate and compute derived fields."""
        if self.x < 0 or self.y < 0:
            raise ValueError(f"Coordinates must be non-negative: x={self.x}, y={self.y}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1]: {self.confidence}")
        # Auto-compute visibility
        self.visible = self.confidence > 0.5


@dataclass
class BoundingBox:
    """Bounding box for detected person in frame.

    Attributes:
        x1, y1: Top-left corner coordinates
        x2, y2: Bottom-right corner coordinates
        width: Box width (auto-computed)
        height: Box height (auto-computed)
    """

    x1: float
    y1: float
    x2: float
    y2: float
    width: float = 0.0
    height: float = 0.0

    def __post_init__(self):
        """Compute width and height from corners."""
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        if self.width < 0 or self.height < 0:
            raise ValueError(
                f"Invalid bounding box: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})"
            )


@dataclass
class PoseData:
    """Complete pose estimation result for a single frame.

    Represents YOLOv8-Pose output with 17 COCO keypoints, bounding box,
    and temporal metadata. Provides utility methods for keypoint access
    and skeleton visualization.

    Attributes:
        keypoints: List of 17 COCO keypoints in standard order
        bbox: Optional bounding box around detected person
        confidence: Overall detection confidence (0.0-1.0)
        frame_id: Sequential frame identifier
        timestamp: Unix timestamp of capture time
    """

    keypoints: List[Keypoint]
    bbox: Optional[BoundingBox]
    confidence: float
    frame_id: int
    timestamp: float

    def __post_init__(self):
        """Validate pose data constraints."""
        if len(self.keypoints) != 17:
            raise ValueError(f"Expected 17 keypoints, got {len(self.keypoints)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1]: {self.confidence}")
        if self.frame_id < 0:
            raise ValueError(f"Frame ID must be non-negative: {self.frame_id}")

    def get_keypoint(self, name: str) -> Keypoint:
        """Get keypoint by COCO name (e.g., 'left_shoulder').

        Args:
            name: Keypoint name from KEYPOINT_INDICES constants

        Returns:
            Corresponding Keypoint object

        Raises:
            KeyError: If keypoint name is invalid
        """
        if name not in KEYPOINT_INDICES:
            raise KeyError(
                f"Invalid keypoint name: {name}. Valid names: {list(KEYPOINT_INDICES.keys())}"
            )
        idx = KEYPOINT_INDICES[name]
        return self.keypoints[idx]

    def is_valid(self) -> bool:
        """Check if pose data is valid for processing.

        A pose is considered valid if at least 8 keypoints are visible
        (confidence > 0.5), which is the minimum for basic pose recognition.

        Returns:
            True if pose has sufficient visible keypoints
        """
        visible_count = sum(1 for kp in self.keypoints if kp.visible)
        return visible_count >= 8

    def get_skeleton_lines(self) -> List[Tuple[Keypoint, Keypoint]]:
        """Get keypoint pairs for skeleton visualization.

        Returns list of (start_kp, end_kp) tuples representing the COCO
        skeleton structure. Used for rendering pose overlay on camera feed.

        Returns:
            List of keypoint pairs forming skeleton connections
        """
        # COCO skeleton structure (17-keypoint pose)
        skeleton_connections = [
            # Face
            ("nose", "left_eye"),
            ("nose", "right_eye"),
            ("left_eye", "left_ear"),
            ("right_eye", "right_ear"),
            # Torso
            ("left_shoulder", "right_shoulder"),
            ("left_shoulder", "left_hip"),
            ("right_shoulder", "right_hip"),
            ("left_hip", "right_hip"),
            # Arms
            ("left_shoulder", "left_elbow"),
            ("left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow"),
            ("right_elbow", "right_wrist"),
            # Legs
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
        ]

        lines = []
        for start_name, end_name in skeleton_connections:
            try:
                start_kp = self.get_keypoint(start_name)
                end_kp = self.get_keypoint(end_name)
                # Only include line if both keypoints are visible
                if start_kp.visible and end_kp.visible:
                    lines.append((start_kp, end_kp))
            except KeyError:
                # Skip invalid keypoint names (should never happen with valid data)
                continue

        return lines
