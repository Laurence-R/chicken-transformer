"""High Knees validator implementation."""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class HKState(Enum):
    START = auto()
    LEFT_UP = auto()
    LEFT_DOWN = auto()
    RIGHT_UP = auto()
    RIGHT_DOWN = auto()


class HighKneesValidator(ActionValidator):
    """Validates high knees execution."""

    def __init__(self):
        super().__init__()
        self.state = HKState.START

    @property
    def exercise_name(self) -> str:
        return "高抬腿"

    def get_required_keypoints(self) -> List[str]:
        return ["left_hip", "left_knee", "right_hip", "right_knee"]

    def validate(self, pose_data: "PoseData") -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(False, 0.0, "無法偵測到腿部")

        l_hip = pose_data.get_keypoint("left_hip")
        l_knee = pose_data.get_keypoint("left_knee")
        r_hip = pose_data.get_keypoint("right_hip")
        r_knee = pose_data.get_keypoint("right_knee")

        # Check knee height (Y coordinate, smaller is higher)
        # Threshold: Knee should be at least at hip level or slightly below
        # Let's say Knee Y < Hip Y + 10 pixels (allow slight tolerance)
        TOLERANCE = 20
        is_l_up = l_knee.y < (l_hip.y + TOLERANCE)
        is_r_up = r_knee.y < (r_hip.y + TOLERANCE)

        debug_info = {
            "l_diff": l_knee.y - l_hip.y,
            "r_diff": r_knee.y - r_hip.y,
            "state": self.state.name,
        }

        if self.state == HKState.START:
            if is_l_up:
                self.state = HKState.LEFT_UP
                return ValidationResult(False, 0.9, "左腿抬起", debug_info)
            elif is_r_up:
                self.state = HKState.RIGHT_UP
                return ValidationResult(False, 0.9, "右腿抬起", debug_info)
            else:
                return ValidationResult(False, 0.9, "開始原地跑", debug_info)

        elif self.state == HKState.LEFT_UP:
            if not is_l_up:
                self.state = HKState.LEFT_DOWN
                return ValidationResult(False, 0.9, "換右腿", debug_info)
            else:
                return ValidationResult(False, 0.8, "左腿放下", debug_info)

        elif self.state == HKState.LEFT_DOWN:
            if is_r_up:
                self.state = HKState.RIGHT_UP
                return ValidationResult(False, 0.9, "右腿抬起", debug_info)
            elif is_l_up:
                self.state = HKState.LEFT_UP
                return ValidationResult(False, 0.7, "換右腿!", debug_info)
            else:
                return ValidationResult(False, 0.8, "右腿抬高", debug_info)

        elif self.state == HKState.RIGHT_UP:
            if not is_r_up:
                self.state = HKState.RIGHT_DOWN
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            else:
                return ValidationResult(False, 0.8, "右腿放下", debug_info)

        elif self.state == HKState.RIGHT_DOWN:
            if is_l_up:
                self.state = HKState.LEFT_UP
                return ValidationResult(False, 0.9, "左腿抬起", debug_info)
            else:
                self.state = HKState.START
                return ValidationResult(False, 0.9, "繼續", debug_info)

        return ValidationResult(False, 0.0, "未知狀態")
