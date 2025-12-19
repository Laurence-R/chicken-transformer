"""Burpee validator implementation."""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class BurpeeState(Enum):
    STANDING = auto()
    GROUND = auto()  # Plank position


class BurpeeValidator(ActionValidator):
    """Validates burpee execution (Simplified: Stand -> Plank -> Stand)."""

    def __init__(self):
        super().__init__()
        self.state = BurpeeState.STANDING

    @property
    def exercise_name(self) -> str:
        return "波比跳"

    def get_required_keypoints(self) -> List[str]:
        return [
            "left_shoulder",
            "left_hip",
            "left_ankle",
            "right_shoulder",
            "right_hip",
            "right_ankle",
        ]

    def validate(self, pose_data: "PoseData") -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(False, 0.0, "無法偵測到全身")

        # Check body orientation
        # Vertical: Shoulder Y < Hip Y < Ankle Y (significantly)
        # Horizontal: Shoulder Y ~ Hip Y (Ankle might be lower or same)

        l_shoulder = pose_data.get_keypoint("left_shoulder")
        l_hip = pose_data.get_keypoint("left_hip")
        l_ankle = pose_data.get_keypoint("left_ankle")

        # Vertical check
        is_vertical = (l_hip.y - l_shoulder.y > 50) and (l_ankle.y - l_hip.y > 50)

        # Horizontal check (Plank)
        # Shoulder and Hip Y difference is small
        is_horizontal = abs(l_shoulder.y - l_hip.y) < 50

        debug_info = {
            "is_vertical": is_vertical,
            "is_horizontal": is_horizontal,
            "state": self.state.name,
        }

        if self.state == BurpeeState.STANDING:
            if is_horizontal:
                self.state = BurpeeState.GROUND
                return ValidationResult(False, 0.9, "很好! 撐住", debug_info)
            elif not is_vertical:
                return ValidationResult(False, 0.7, "下蹲/趴下", debug_info)
            else:
                return ValidationResult(False, 0.9, "準備開始", debug_info)

        elif self.state == BurpeeState.GROUND:
            if is_vertical:
                self.state = BurpeeState.STANDING
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            elif not is_horizontal:
                return ValidationResult(False, 0.7, "起身跳躍", debug_info)
            else:
                return ValidationResult(False, 0.9, "準備起身", debug_info)

        return ValidationResult(False, 0.0, "未知狀態")
