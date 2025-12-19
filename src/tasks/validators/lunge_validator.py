"""Lunge validator implementation."""

from enum import Enum, auto
from typing import TYPE_CHECKING, List

from ...utils.geometry import calculate_angle
from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class LungeState(Enum):
    STANDING = auto()
    DESCENDING = auto()
    BOTTOM = auto()
    ASCENDING = auto()


class LungeValidator(ActionValidator):
    """Validates lunge execution."""

    def __init__(self):
        super().__init__()
        self.state = LungeState.STANDING

    @property
    def exercise_name(self) -> str:
        return "弓箭步"

    def get_required_keypoints(self) -> List[str]:
        return ["left_hip", "left_knee", "left_ankle", "right_hip", "right_knee", "right_ankle"]

    def validate(self, pose_data: "PoseData") -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(False, 0.0, "無法偵測到腿部")

        # Get keypoints
        l_hip = pose_data.get_keypoint("left_hip")
        l_knee = pose_data.get_keypoint("left_knee")
        l_ankle = pose_data.get_keypoint("left_ankle")
        r_hip = pose_data.get_keypoint("right_hip")
        r_knee = pose_data.get_keypoint("right_knee")
        r_ankle = pose_data.get_keypoint("right_ankle")

        # Calculate angles
        l_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_angle = calculate_angle(r_hip, r_knee, r_ankle)

        # Determine which leg is front (usually the one with larger knee angle is back? No, front leg bends to 90, back leg also bends)
        # Actually, in a lunge, both knees bend.
        # Front knee ~90 deg. Back knee ~90 deg (and close to ground).
        # Standing: both ~180.

        # Simple logic: Check if EITHER knee is ~90 degrees
        is_lunge_depth = (l_angle < 110) or (r_angle < 110)
        is_standing = (l_angle > 160) and (r_angle > 160)

        debug_info = {"l_angle": l_angle, "r_angle": r_angle, "state": self.state.name}

        if self.state == LungeState.STANDING:
            if is_lunge_depth:
                self.state = LungeState.BOTTOM
                return ValidationResult(False, 0.8, "保持弓箭步", debug_info)
            elif l_angle < 150 or r_angle < 150:
                self.state = LungeState.DESCENDING
                return ValidationResult(False, 0.7, "下蹲中", debug_info)
            else:
                return ValidationResult(False, 0.9, "準備開始", debug_info)

        elif self.state == LungeState.DESCENDING:
            if is_lunge_depth:
                self.state = LungeState.BOTTOM
                return ValidationResult(False, 0.9, "到達底部", debug_info)
            elif is_standing:
                self.state = LungeState.STANDING
                return ValidationResult(False, 0.5, "回到站立", debug_info)
            else:
                return ValidationResult(False, 0.7, "再低一點", debug_info)

        elif self.state == LungeState.BOTTOM:
            if is_standing:
                self.state = LungeState.STANDING
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            elif not is_lunge_depth:
                self.state = LungeState.ASCENDING
                return ValidationResult(False, 0.8, "起身中", debug_info)
            else:
                return ValidationResult(False, 0.9, "保持姿勢", debug_info)

        elif self.state == LungeState.ASCENDING:
            if is_standing:
                self.state = LungeState.STANDING
                return ValidationResult(True, 1.0, "完成一次!", debug_info)
            elif is_lunge_depth:
                self.state = LungeState.BOTTOM
                return ValidationResult(False, 0.6, "回到底部", debug_info)
            else:
                return ValidationResult(False, 0.7, "繼續起身", debug_info)

        return ValidationResult(False, 0.0, "未知狀態")
