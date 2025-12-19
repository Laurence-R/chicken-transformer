"""Completion state implementation.

Shows success message and transitions back to start.
"""
import time
from typing import Optional, TYPE_CHECKING
from .game_state import GameState, StateTransition
from ..models.game_context import GameContext

if TYPE_CHECKING:
    from ..utils.data_structures import PoseData

class CompletionState(GameState):
    """Task completion screen."""
    
    def __init__(self):
        self.enter_time: Optional[float] = None
        self.DISPLAY_DURATION = 3.0

    @property
    def name(self) -> str:
        return "COMPLETION"

    def enter(self, context: GameContext) -> None:
        self.enter_time = time.time()
        
        # Calculate score based on task difficulty (placeholder)
        points = 10
        if context.current_task:
            # Bonus for more reps or sets
            points += context.current_task.target_reps
            
        context.score += points
        self._message = f"任務完成!\n獲得 {points} 分\n總分: {context.score}"

    def update(self, context: GameContext, pose_data: Optional['PoseData']) -> StateTransition:
        if time.time() - self.enter_time > self.DISPLAY_DURATION:
            return StateTransition(next_state_name="WAITING", context_updates={})
            
        return StateTransition(next_state_name=None, context_updates={})

    def exit(self, context: GameContext) -> None:
        pass

    def get_display_message(self) -> str:
        return self._message
