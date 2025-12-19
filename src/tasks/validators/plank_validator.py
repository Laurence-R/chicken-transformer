"""Plank validator implementation."""

import time
from typing import TYPE_CHECKING, List

from ...utils.geometry import calculate_angle
from .action_validator import ActionValidator, ValidationResult

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData


class PlankValidator(ActionValidator):
    """Validates plank execution (time-based)."""

    def __init__(self):
        super().__init__()
        self.hold_start_time = None
        self.last_success_time = 0.0

    @property
    def exercise_name(self) -> str:
        return "平板支撐"

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
            self.hold_start_time = None
            return ValidationResult(False, 0.0, "無法偵測到身體側面")

        # Get keypoints (use average of left/right or just one side if visible)
        # Ideally check both or the more visible side.
        # For simplicity, check left side if visible, else right.

        side = "left"
        if pose_data.get_keypoint("left_hip").confidence < 0.5:
            side = "right"

        shoulder = pose_data.get_keypoint(f"{side}_shoulder")
        hip = pose_data.get_keypoint(f"{side}_hip")
        ankle = pose_data.get_keypoint(f"{side}_ankle")

        # Calculate body line angle (Shoulder-Hip-Ankle)
        # Ideally should be 180 degrees (straight line)
        body_angle = calculate_angle(shoulder, hip, ankle)

        is_straight = body_angle > 160

        debug_info = {"body_angle": body_angle, "side": side}

        if is_straight:
            now = time.time()
            if self.hold_start_time is None:
                self.hold_start_time = now

            duration = now - self.hold_start_time

            if duration >= 1.0:
                self.hold_start_time = now  # Reset for next second
                return ValidationResult(True, 1.0, "堅持住! +1秒", debug_info)
            else:
                return ValidationResult(False, 0.9, f"保持... {duration:.1f}s", debug_info)
        else:
            self.hold_start_time = None
            return ValidationResult(False, 0.6, "臀部請放低/抬高，保持直線", debug_info)
