"""Mountain Climber validator implementation."""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from ...utils.geometry import calculate_distance
from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class MCState(Enum):
    START = auto()
    LEFT_UP = auto()
    LEFT_DOWN = auto()
    RIGHT_UP = auto()
    RIGHT_DOWN = auto()


class MountainClimberValidator(ActionValidator):
    """Validates mountain climber execution."""

    def __init__(self):
        super().__init__()
        self.state = MCState.START

    @property
    def exercise_name(self) -> str:
        return "登山者"

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
            return ValidationResult(False, 0.0, "無法偵測到四肢")

        l_shoulder = pose_data.get_keypoint("left_shoulder")
        l_hip = pose_data.get_keypoint("left_hip")
        l_knee = pose_data.get_keypoint("left_knee")

        r_shoulder = pose_data.get_keypoint("right_shoulder")
        r_knee = pose_data.get_keypoint("right_knee")

        # Check if in plank position (horizontal)
        is_horizontal = abs(l_shoulder.y - l_hip.y) < 50
        if not is_horizontal:
            return ValidationResult(False, 0.5, "請保持平板支撐姿勢")

        # Calculate normalized distances
        torso_len = calculate_distance(l_shoulder, l_hip)
        if torso_len == 0:
            return ValidationResult(False, 0.0, "數據錯誤")

        l_knee_dist = calculate_distance(l_knee, l_shoulder) / torso_len
        r_knee_dist = calculate_distance(r_knee, r_shoulder) / torso_len

        # Threshold: Knee is "up" if distance to shoulder is small (e.g. < 1.2 * torso)
        # Normal plank: Knee to shoulder is ~ Torso + Thigh > 1.5
        UP_THRESHOLD = 1.2

        is_l_up = l_knee_dist < UP_THRESHOLD
        is_r_up = r_knee_dist < UP_THRESHOLD

        debug_info = {"l_dist": l_knee_dist, "r_dist": r_knee_dist, "state": self.state.name}

        if self.state == MCState.START:
            if is_l_up:
                self.state = MCState.LEFT_UP
                return ValidationResult(False, 0.9, "左腳收回", debug_info)
            elif is_r_up:
                self.state = MCState.RIGHT_UP
                return ValidationResult(False, 0.9, "右腳收回", debug_info)
            else:
                return ValidationResult(False, 0.9, "開始交替收腿", debug_info)

        elif self.state == MCState.LEFT_UP:
            if not is_l_up:  # Left down
                self.state = MCState.LEFT_DOWN
                return ValidationResult(False, 0.9, "換右腳", debug_info)
            else:
                return ValidationResult(False, 0.8, "左腳還原", debug_info)

        elif self.state == MCState.LEFT_DOWN:
            if is_r_up:
                self.state = MCState.RIGHT_UP
                return ValidationResult(False, 0.9, "右腳收回", debug_info)
            elif is_l_up:  # Back to left?
                self.state = MCState.LEFT_UP
                return ValidationResult(False, 0.7, "換右腳!", debug_info)
            else:
                return ValidationResult(False, 0.8, "右腳收腿", debug_info)

        elif self.state == MCState.RIGHT_UP:
            if not is_r_up:  # Right down
                self.state = MCState.RIGHT_DOWN
                return ValidationResult(
                    True, 1.0, "完成一次!", debug_info
                )  # Count 1 rep after L+R? Or just R?
            else:
                return ValidationResult(False, 0.8, "右腳還原", debug_info)

        elif self.state == MCState.RIGHT_DOWN:
            # Reset to start or directly to Left Up
            if is_l_up:
                self.state = MCState.LEFT_UP
                return ValidationResult(False, 0.9, "左腳收回", debug_info)
            else:
                self.state = MCState.START
                return ValidationResult(False, 0.9, "繼續", debug_info)

        return ValidationResult(False, 0.0, "未知狀態")
