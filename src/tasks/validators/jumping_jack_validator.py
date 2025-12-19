"""Jumping Jack validator implementation.

Validates jumping jack exercise using limb positions and distances.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from ...utils.geometry import calculate_distance
from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class JumpingJackState(Enum):
    """States for jumping jack repetition."""

    CLOSED = auto()  # Feet together, hands down
    OPENING = auto()  # Moving to open position
    OPEN = auto()  # Feet apart, hands up
    CLOSING = auto()  # Moving to closed position


class JumpingJackValidator(ActionValidator):
    """Validates jumping jack execution.

    Criteria:
    - Closed: Feet distance < Shoulder width, Hands below shoulders
    - Open: Feet distance > 1.5 * Shoulder width, Hands above shoulders
    - Sequence: Closed -> Open -> Closed = 1 rep
    """

    def __init__(self):
        super().__init__()
        self.state = JumpingJackState.CLOSED

    @property
    def exercise_name(self) -> str:
        return "開合跳"

    def get_required_keypoints(self) -> List[str]:
        return [
            "left_shoulder",
            "right_shoulder",
            "left_wrist",
            "right_wrist",
            "left_ankle",
            "right_ankle",
            "left_hip",
            "right_hip",  # For shoulder width reference
        ]

    def validate(self, pose_data: "PoseData") -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(
                is_valid=False, confidence=0.0, feedback="無法偵測到完整四肢關鍵點"
            )

        # Get keypoints
        l_shoulder = pose_data.get_keypoint("left_shoulder")
        r_shoulder = pose_data.get_keypoint("right_shoulder")
        l_wrist = pose_data.get_keypoint("left_wrist")
        r_wrist = pose_data.get_keypoint("right_wrist")
        l_ankle = pose_data.get_keypoint("left_ankle")
        r_ankle = pose_data.get_keypoint("right_ankle")

        # Calculate reference width (shoulder width)
        shoulder_width = calculate_distance(l_shoulder, r_shoulder)
        if shoulder_width == 0:
            return ValidationResult(False, 0.0, "無法計算肩寬")

        # Calculate feet distance
        feet_distance = calculate_distance(l_ankle, r_ankle)

        # Check hands position (y coordinate, smaller is higher)
        hands_up = (l_wrist.y < l_shoulder.y) and (r_wrist.y < r_shoulder.y)
        hands_down = (l_wrist.y > l_shoulder.y) and (r_wrist.y > r_shoulder.y)

        # Check feet position
        feet_open = feet_distance > (1.5 * shoulder_width)
        feet_closed = feet_distance < (1.0 * shoulder_width)

        debug_info = {
            "feet_distance": feet_distance,
            "shoulder_width": shoulder_width,
            "hands_up": hands_up,
            "state": self.state.name,
        }

        # State Machine
        if self.state == JumpingJackState.CLOSED:
            if feet_open and hands_up:
                self.state = JumpingJackState.OPEN
                return ValidationResult(False, 0.9, "很好! 保持開合", debug_info)
            elif not feet_closed or not hands_down:
                self.state = JumpingJackState.OPENING
                return ValidationResult(False, 0.7, "動作開始", debug_info)
            else:
                return ValidationResult(False, 0.8, "準備開始", debug_info)

        elif self.state == JumpingJackState.OPENING:
            if feet_open and hands_up:
                self.state = JumpingJackState.OPEN
                return ValidationResult(False, 0.9, "到達頂點!", debug_info)
            elif feet_closed and hands_down:
                self.state = JumpingJackState.CLOSED
                return ValidationResult(False, 0.5, "回到起始位置", debug_info)
            else:
                return ValidationResult(False, 0.7, "繼續張開手腳", debug_info)

        elif self.state == JumpingJackState.OPEN:
            if feet_closed and hands_down:
                self.state = JumpingJackState.CLOSED
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            elif not feet_open or not hands_up:
                self.state = JumpingJackState.CLOSING
                return ValidationResult(False, 0.8, "收回手腳", debug_info)
            else:
                return ValidationResult(False, 0.9, "保持張開", debug_info)

        elif self.state == JumpingJackState.CLOSING:
            if feet_closed and hands_down:
                self.state = JumpingJackState.CLOSED
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            elif feet_open and hands_up:
                self.state = JumpingJackState.OPEN
                return ValidationResult(False, 0.5, "回到頂點", debug_info)
            else:
                return ValidationResult(False, 0.7, "繼續收回", debug_info)

        return ValidationResult(False, 0.0, "未知狀態")

    def can_validate(self, pose_data: "PoseData") -> bool:
        """Check if all required keypoints are visible."""
        for name in self.get_required_keypoints():
            kp = pose_data.get_keypoint(name)
            if not kp or kp.confidence < self.min_confidence:
                return False
        return True
