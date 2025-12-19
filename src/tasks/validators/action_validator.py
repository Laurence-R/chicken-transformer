"""Abstract base class for exercise action validators.

Defines the interface for exercise-specific validation logic using Strategy Pattern.
Each exercise (squat, pushup, etc.) has its own validator implementing this ABC.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


@dataclass
class ValidationResult:
    """Result of exercise validation with feedback.

    Attributes:
        is_valid: Whether the exercise repetition is valid
        confidence: Validation confidence score (0.0-1.0)
        feedback: User-facing feedback message in Traditional Chinese
        debug_info: Optional debug data (angles, distances, etc.) for logging
    """

    is_valid: bool
    confidence: float
    feedback: str
    debug_info: Optional[dict] = None

    def __post_init__(self):
        """Validate field constraints."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1]: {self.confidence}")


class ActionValidator(ABC):
    """Abstract base class for exercise validation.

    Implements Strategy Pattern to validate different exercise types.
    Each concrete validator (SquatValidator, PushupValidator, etc.) defines
    exercise-specific angle/distance checks and provides feedback.

    Contract:
        - validate() must execute in <5ms
        - Required keypoints must have confidence >= min_confidence_threshold
        - Feedback messages must be non-empty Traditional Chinese strings
    """

    def __init__(
        self,
        tolerance_angle_degrees: float = 17.5,
        tolerance_distance_ratio: float = 0.10,
        min_confidence_threshold: float = 0.5,
    ):
        """Initialize validator with tolerance parameters.

        Args:
            tolerance_angle_degrees: Angle tolerance in degrees (±)
            tolerance_distance_ratio: Distance tolerance as ratio (±)
            min_confidence_threshold: Minimum keypoint confidence for validation

        Invariants:
            - tolerance_angle_degrees ∈ [5°, 30°]
            - tolerance_distance_ratio ∈ [0.05, 0.20]
            - min_confidence_threshold ∈ [0.3, 0.7]
        """
        if not 5.0 <= tolerance_angle_degrees <= 30.0:
            raise ValueError(f"Angle tolerance must be in [5, 30]: {tolerance_angle_degrees}")
        if not 0.05 <= tolerance_distance_ratio <= 0.20:
            raise ValueError(
                f"Distance tolerance must be in [0.05, 0.20]: {tolerance_distance_ratio}"
            )
        if not 0.3 <= min_confidence_threshold <= 0.7:
            raise ValueError(
                f"Confidence threshold must be in [0.3, 0.7]: {min_confidence_threshold}"
            )

        self.tolerance_angle = tolerance_angle_degrees
        self.tolerance_distance = tolerance_distance_ratio
        self.min_confidence = min_confidence_threshold

    @property
    @abstractmethod
    def exercise_name(self) -> str:
        """Exercise name in Traditional Chinese.

        Returns:
            Exercise name (e.g., "深蹲", "伏地挺身", "波比跳")
        """
        pass

    @abstractmethod
    def validate(self, pose_data: "PoseData") -> ValidationResult:
        """Validate single exercise repetition.

        Args:
            pose_data: Current frame pose data

        Returns:
            ValidationResult with validity, confidence, and feedback

        Requirements:
            - Execution time <5ms (99th percentile)
            - Keypoints with confidence <min_confidence treated as invalid
            - Must provide specific feedback (not just True/False)
            - Feedback must be in Traditional Chinese

        Postconditions:
            - If is_valid=True, confidence should be ≥0.7
            - feedback must be non-empty string

        Example:
            >>> result = validator.validate(pose_data)
            >>> if result.is_valid:
            ...     print(f"✓ {result.feedback}")
            ... else:
            ...     print(f"✗ {result.feedback}")
        """
        pass

    @abstractmethod
    def get_required_keypoints(self) -> list[str]:
        """Get list of required keypoint names for this exercise.

        Returns:
            List of COCO keypoint names (e.g., ["left_hip", "left_knee", "left_ankle"])

        Purpose:
            - Check if PoseData contains sufficient visible keypoints
            - Enable fast-fail before expensive validation logic

        Example:
            >>> validator = SquatValidator()
            >>> required = validator.get_required_keypoints()
            >>> # ["left_hip", "left_knee", "left_ankle", "right_hip", ...]
        """
        pass

    def can_validate(self, pose_data: "PoseData") -> bool:
        """Check if PoseData has sufficient keypoints for validation.

        Args:
            pose_data: Current frame pose data

        Returns:
            True if all required keypoints are visible with sufficient confidence

        Requirements:
            - Execution time <1ms
            - Default implementation checks required keypoints
            - Subclasses rarely need to override

        Note:
            This method has a default implementation. Subclasses typically
            do not need to override unless special checks are needed.
        """
        required = self.get_required_keypoints()
        for kp_name in required:
            try:
                kp = pose_data.get_keypoint(kp_name)
                if not kp.visible or kp.confidence < self.min_confidence:
                    return False
            except KeyError:
                return False
        return True
