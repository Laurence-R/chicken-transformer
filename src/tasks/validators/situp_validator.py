"""Situp validator implementation."""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from ...utils.geometry import calculate_angle
from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class SitupState(Enum):
    DOWN = auto()
    ASCENDING = auto()
    UP = auto()
    DESCENDING = auto()


class SitupValidator(ActionValidator):
    """Validates situp execution."""

    def __init__(self):
        super().__init__()
        self.state = SitupState.DOWN

    @property
    def exercise_name(self) -> str:
        return "仰臥起坐"

    def get_required_keypoints(self) -> List[str]:
        return [
            "left_shoulder",
            "left_hip",
            "left_knee",
            "right_shoulder",
            "right_hip",
            "right_knee",
        ]

    def validate(self, pose_data: "PoseData") -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(False, 0.0, "無法偵測到上半身")

        # Use average of both sides
        l_angle = calculate_angle(
            pose_data.get_keypoint("left_shoulder"),
            pose_data.get_keypoint("left_hip"),
            pose_data.get_keypoint("left_knee"),
        )
        r_angle = calculate_angle(
            pose_data.get_keypoint("right_shoulder"),
            pose_data.get_keypoint("right_hip"),
            pose_data.get_keypoint("right_knee"),
        )

        avg_angle = (l_angle + r_angle) / 2.0

        # Thresholds
        # Lying down: Angle is open (e.g. > 100)
        # Sitting up: Angle is closed (e.g. < 60)
        UP_THRESHOLD = 60.0
        DOWN_THRESHOLD = 100.0

        debug_info = {"avg_angle": avg_angle, "state": self.state.name}

        if self.state == SitupState.DOWN:
            if avg_angle < UP_THRESHOLD:
                self.state = SitupState.UP
                return ValidationResult(False, 0.9, "到達頂點", debug_info)
            elif avg_angle < DOWN_THRESHOLD:
                self.state = SitupState.ASCENDING
                return ValidationResult(False, 0.7, "加油! 起身", debug_info)
            else:
                return ValidationResult(False, 0.9, "準備開始", debug_info)

        elif self.state == SitupState.ASCENDING:
            if avg_angle < UP_THRESHOLD:
                self.state = SitupState.UP
                return ValidationResult(False, 0.9, "到達頂點!", debug_info)
            elif avg_angle > DOWN_THRESHOLD:
                self.state = SitupState.DOWN
                return ValidationResult(False, 0.5, "回到躺姿", debug_info)
            else:
                return ValidationResult(False, 0.7, "繼續起身", debug_info)

        elif self.state == SitupState.UP:
            if avg_angle > DOWN_THRESHOLD:
                self.state = SitupState.DOWN
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            elif avg_angle > UP_THRESHOLD:
                self.state = SitupState.DESCENDING
                return ValidationResult(False, 0.8, "慢慢躺下", debug_info)
            else:
                return ValidationResult(False, 0.9, "保持頂點", debug_info)

        elif self.state == SitupState.DESCENDING:
            if avg_angle > DOWN_THRESHOLD:
                self.state = SitupState.DOWN
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            elif avg_angle < UP_THRESHOLD:
                self.state = SitupState.UP
                return ValidationResult(False, 0.6, "回到頂點", debug_info)
            else:
                return ValidationResult(False, 0.7, "繼續躺下", debug_info)

        return ValidationResult(False, 0.0, "未知狀態")
