"""Squat validator implementation.

Validates squat exercise using hip and knee angles.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from ...utils.geometry import calculate_angle
from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class SquatState(Enum):
    """States for squat repetition."""

    STANDING = auto()  # Initial standing position
    DESCENDING = auto()  # Going down
    BOTTOM = auto()  # At the bottom of the squat
    ASCENDING = auto()  # Coming up


class SquatValidator(ActionValidator):
    """Validates squat execution.

    Criteria:
    - Standing: Knee angle > 160 degrees
    - Bottom: Knee angle < 90 degrees (approx)
    - Sequence: Standing -> Bottom -> Standing = 1 rep
    """

    def __init__(self):
        super().__init__()
        self.state = SquatState.STANDING
        self.min_knee_angle = 180.0  # Track depth

        # Thresholds
        self.STAND_THRESHOLD = 160.0
        self.SQUAT_THRESHOLD = 100.0  # Easier threshold for MVP

    @property
    def exercise_name(self) -> str:
        return "深蹲"

    def get_required_keypoints(self) -> List[str]:
        return ["left_hip", "left_knee", "left_ankle", "right_hip", "right_knee", "right_ankle"]

    def validate(self, pose_data: "PoseData") -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(
                is_valid=False, confidence=0.0, feedback="無法偵測到完整腿部關鍵點"
            )

        # Get keypoints
        l_hip = pose_data.get_keypoint("left_hip")
        l_knee = pose_data.get_keypoint("left_knee")
        l_ankle = pose_data.get_keypoint("left_ankle")

        r_hip = pose_data.get_keypoint("right_hip")
        r_knee = pose_data.get_keypoint("right_knee")
        r_ankle = pose_data.get_keypoint("right_ankle")

        # Calculate knee angles (Hip-Knee-Ankle)
        l_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_angle = calculate_angle(r_hip, r_knee, r_ankle)

        # Use average angle
        avg_knee_angle = (l_angle + r_angle) / 2.0

        debug_info = {"avg_knee_angle": avg_knee_angle, "state": self.state.name}

        # State Machine
        if self.state == SquatState.STANDING:
            if avg_knee_angle < self.STAND_THRESHOLD:
                self.state = SquatState.DESCENDING
                return ValidationResult(False, 0.8, "開始下蹲", debug_info)
            else:
                return ValidationResult(False, 0.9, "請保持站立準備", debug_info)

        elif self.state == SquatState.DESCENDING:
            if avg_knee_angle < self.SQUAT_THRESHOLD:
                self.state = SquatState.BOTTOM
                self.min_knee_angle = avg_knee_angle
                return ValidationResult(False, 0.9, "到達底部! 準備起立", debug_info)
            elif avg_knee_angle > self.STAND_THRESHOLD:
                # Aborted squat
                self.state = SquatState.STANDING
                return ValidationResult(False, 0.5, "下蹲幅度不足", debug_info)
            else:
                return ValidationResult(False, 0.8, "再蹲低一點...", debug_info)

        elif self.state == SquatState.BOTTOM:
            if avg_knee_angle > self.SQUAT_THRESHOLD + 10:  # Hysteresis
                self.state = SquatState.ASCENDING
                return ValidationResult(False, 0.8, "正在起立", debug_info)
            else:
                # Update min angle if they go lower
                self.min_knee_angle = min(self.min_knee_angle, avg_knee_angle)
                return ValidationResult(False, 0.9, "保持底部姿勢", debug_info)

        elif self.state == SquatState.ASCENDING:
            if avg_knee_angle > self.STAND_THRESHOLD:
                self.state = SquatState.STANDING
                return ValidationResult(True, 1.0, "完成一次深蹲!", debug_info)
            elif avg_knee_angle < self.SQUAT_THRESHOLD:
                # Went back down
                self.state = SquatState.BOTTOM
                return ValidationResult(False, 0.6, "回到底部", debug_info)
            else:
                return ValidationResult(False, 0.8, "加油! 站直", debug_info)

        return ValidationResult(False, 0.0, "未知狀態", debug_info)
