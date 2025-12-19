"""Dice roll detecting state implementation.

Detects the 'Jump + Hands Up' gesture to trigger a dice roll.
"""
import time
import random
from typing import Optional, TYPE_CHECKING
from .game_state import GameState, StateTransition
from ..models.game_context import GameContext

if TYPE_CHECKING:
    from ..utils.data_structures import PoseData

class DiceRollDetectingState(GameState):
    """Detects gesture to roll the dice."""
    
    def __init__(self):
        self.hold_start_time: Optional[float] = None
        self.REQUIRED_HOLD_DURATION = 1.0 # Seconds to hold the pose

    @property
    def name(self) -> str:
        return "DICE_ROLL_DETECTING"

    def enter(self, context: GameContext) -> None:
        self.hold_start_time = None

    def update(self, context: GameContext, pose_data: Optional['PoseData']) -> StateTransition:
        if not pose_data:
            self.hold_start_time = None
            return StateTransition(
                next_state_name="WAITING", 
                context_updates={"player_detected": False}
            )

        # Check for hands up (Wrists above Shoulders)
        # Y coordinates: 0 is top. So Wrist.y < Shoulder.y
        is_hands_up = self._check_hands_up(pose_data)
        
        if is_hands_up:
            if self.hold_start_time is None:
                self.hold_start_time = time.time()
            elif time.time() - self.hold_start_time > self.REQUIRED_HOLD_DURATION:
                # Trigger Roll
                dice_roll = random.randint(1, 6)
                return StateTransition(
                    next_state_name="TASK_DISPLAY", 
                    context_updates={"last_dice_roll": dice_roll}
                )
        else:
            self.hold_start_time = None
            
        return StateTransition(next_state_name=None, context_updates={})

    def exit(self, context: GameContext) -> None:
        self.hold_start_time = None

    def get_display_message(self) -> str:
        if self.hold_start_time:
            elapsed = time.time() - self.hold_start_time
            remaining = max(0.0, self.REQUIRED_HOLD_DURATION - elapsed)
            return f"保持姿勢... {remaining:.1f}秒"
        return "請舉起雙手擲骰子"

    def _check_hands_up(self, pose_data: 'PoseData') -> bool:
        """Check if both wrists are above shoulders."""
        try:
            l_wrist = pose_data.get_keypoint('left_wrist')
            r_wrist = pose_data.get_keypoint('right_wrist')
            l_shoulder = pose_data.get_keypoint('left_shoulder')
            r_shoulder = pose_data.get_keypoint('right_shoulder')
            
            if not (l_wrist.visible and r_wrist.visible and l_shoulder.visible and r_shoulder.visible):
                return False
                
            # Y increases downwards, so smaller Y is higher
            return l_wrist.y < l_shoulder.y and r_wrist.y < r_shoulder.y
        except KeyError:
            return False
