"""Pushup validator implementation.

Validates pushup exercise using elbow and shoulder angles.
"""
from enum import Enum, auto
from typing import List, Optional, TYPE_CHECKING
from .action_validator import ActionValidator, ValidationResult
from ...utils.geometry import calculate_angle

if TYPE_CHECKING:
    from ...utils.data_structures import PoseData

class PushupState(Enum):
    """States for pushup repetition."""
    UP = auto()        # Plank position (arms extended)
    DESCENDING = auto() # Going down
    DOWN = auto()      # Chest near floor
    ASCENDING = auto() # Pushing up

class PushupValidator(ActionValidator):
    """Validates pushup execution.
    
    Criteria:
    - Up: Elbow angle > 160 degrees
    - Down: Elbow angle < 90 degrees
    - Sequence: Up -> Down -> Up = 1 rep
    """
    
    def __init__(self):
        super().__init__()
        self.state = PushupState.UP
        
        # Thresholds
        self.UP_THRESHOLD = 160.0
        self.DOWN_THRESHOLD = 100.0 # Easier threshold for MVP
        
    @property
    def exercise_name(self) -> str:
        return "伏地挺身"

    def get_required_keypoints(self) -> List[str]:
        return [
            'left_shoulder', 'left_elbow', 'left_wrist',
            'right_shoulder', 'right_elbow', 'right_wrist'
        ]

    def validate(self, pose_data: 'PoseData') -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                feedback="無法偵測到完整手臂關鍵點"
            )

        # Get keypoints
        l_shoulder = pose_data.get_keypoint('left_shoulder')
        l_elbow = pose_data.get_keypoint('left_elbow')
        l_wrist = pose_data.get_keypoint('left_wrist')
        
        r_shoulder = pose_data.get_keypoint('right_shoulder')
        r_elbow = pose_data.get_keypoint('right_elbow')
        r_wrist = pose_data.get_keypoint('right_wrist')

        # Calculate elbow angles (Shoulder-Elbow-Wrist)
        l_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        r_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
        
        # Use average angle
        avg_elbow_angle = (l_angle + r_angle) / 2.0
        
        debug_info = {
            "avg_elbow_angle": avg_elbow_angle,
            "state": self.state.name
        }

        # State Machine
        if self.state == PushupState.UP:
            if avg_elbow_angle < self.UP_THRESHOLD:
                self.state = PushupState.DESCENDING
                return ValidationResult(False, 0.8, "開始下降", debug_info)
            else:
                return ValidationResult(False, 0.9, "請保持撐體準備", debug_info)
                
        elif self.state == PushupState.DESCENDING:
            if avg_elbow_angle < self.DOWN_THRESHOLD:
                self.state = PushupState.DOWN
                return ValidationResult(False, 0.9, "到達底部! 準備撐起", debug_info)
            elif avg_elbow_angle > self.UP_THRESHOLD:
                # Aborted
                self.state = PushupState.UP
                return ValidationResult(False, 0.5, "下降幅度不足", debug_info)
            else:
                return ValidationResult(False, 0.8, "再低一點...", debug_info)
                
        elif self.state == PushupState.DOWN:
            if avg_elbow_angle > self.DOWN_THRESHOLD + 10:
                self.state = PushupState.ASCENDING
                return ValidationResult(False, 0.8, "正在撐起", debug_info)
            else:
                return ValidationResult(False, 0.9, "保持底部姿勢", debug_info)
                
        elif self.state == PushupState.ASCENDING:
            if avg_elbow_angle > self.UP_THRESHOLD:
                self.state = PushupState.UP
                return ValidationResult(True, 1.0, "完成一次伏地挺身!", debug_info)
            elif avg_elbow_angle < self.DOWN_THRESHOLD:
                # Went back down
                self.state = PushupState.DOWN
                return ValidationResult(False, 0.6, "回到底部", debug_info)
            else:
                return ValidationResult(False, 0.8, "加油! 撐直手臂", debug_info)
                
        return ValidationResult(False, 0.0, "未知狀態", debug_info)
