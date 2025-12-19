"""Game context holding shared state data.

This data structure is passed between game states and holds the current
snapshot of the game (score, current task, player status, etc.).
"""
from dataclasses import dataclass, field
from typing import Optional
from ..tasks.workout_task import WorkoutTask

@dataclass
class GameContext:
    """Shared game state data passed between states.
    
    Attributes:
        current_task: The currently assigned workout task (if any)
        score: Current player score
        player_detected: Whether a player is currently detected by the camera
        last_dice_roll: The result of the last dice roll (1-6)
        consecutive_failures: Number of consecutive failed tasks (for difficulty adjustment)
    """
    current_task: Optional[WorkoutTask] = None
    score: int = 0
    player_detected: bool = False
    last_dice_roll: int = 0
    consecutive_failures: int = 0
    
    def reset_task(self) -> None:
        """Clear the current task and temporary state."""
        self.current_task = None
        self.last_dice_roll = 0
        # Keep score and consecutive_failures for session continuity
