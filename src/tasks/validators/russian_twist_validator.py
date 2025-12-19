"""Russian Twist validator implementation."""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class RTState(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()


class RussianTwistValidator(ActionValidator):
    """Validates Russian Twist execution."""

    def __init__(self):
        super().__init__()
        self.state = RTState.CENTER

    @property
    def exercise_name(self) -> str:
        return "俄式轉體"

    def get_required_keypoints(self) -> List[str]:
        return ["left_hip", "right_hip", "left_wrist", "right_wrist"]

    def validate(self, pose_data: "PoseData") -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(False, 0.0, "無法偵測到手部或臀部")

        l_hip = pose_data.get_keypoint("left_hip")
        r_hip = pose_data.get_keypoint("right_hip")
        l_wrist = pose_data.get_keypoint("left_wrist")
        r_wrist = pose_data.get_keypoint("right_wrist")

        # Average hip X and wrist X
        hip_center_x = (l_hip.x + r_hip.x) / 2.0
        wrist_center_x = (l_wrist.x + r_wrist.x) / 2.0

        # Hip width for normalization
        hip_width = abs(l_hip.x - r_hip.x)
        if hip_width == 0:
            hip_width = 100  # Fallback

        # Check twist
        # Left twist: Hands to the right of image (if facing camera)?
        # If user faces camera:
        # User's Left is Image Right.
        # User's Right is Image Left.
        # Let's assume "Side A" and "Side B".

        # Threshold: Hands significantly outside hip width
        dist_from_center = wrist_center_x - hip_center_x

        is_right_side = dist_from_center > (hip_width * 0.5)  # Image Right (User Left)
        is_left_side = dist_from_center < -(hip_width * 0.5)  # Image Left (User Right)
        is_center = not is_right_side and not is_left_side

        debug_info = {"dist": dist_from_center, "state": self.state.name}

        if self.state == RTState.CENTER:
            if is_left_side:
                self.state = RTState.LEFT
                return ValidationResult(False, 0.9, "轉向一側", debug_info)
            elif is_right_side:
                self.state = RTState.RIGHT
                return ValidationResult(False, 0.9, "轉向一側", debug_info)
            else:
                return ValidationResult(False, 0.9, "開始轉體", debug_info)

        elif self.state == RTState.LEFT:
            if is_right_side:
                self.state = RTState.RIGHT
                return ValidationResult(True, 1.0, "完成一次!", debug_info)  # L -> R = 1 rep
            elif is_center:
                # Passing through center
                return ValidationResult(False, 0.8, "轉向另一側", debug_info)
            else:
                return ValidationResult(False, 0.9, "保持轉體", debug_info)

        elif self.state == RTState.RIGHT:
            if is_left_side:
                self.state = RTState.LEFT
                return ValidationResult(True, 1.0, "完成一次!", debug_info)  # R -> L = 1 rep
            elif is_center:
                return ValidationResult(False, 0.8, "轉向另一側", debug_info)
            else:
                return ValidationResult(False, 0.9, "保持轉體", debug_info)

        return ValidationResult(False, 0.0, "未知狀態")
