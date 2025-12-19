"""Game context holding shared state data.

This data structure is passed between game states and holds the current
snapshot of the game (score, current task, player status, etc.).
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ..tasks.workout_task import WorkoutTask

if TYPE_CHECKING:
    from ..states.game_state import GameState


@dataclass
class GameContext:
    """Shared game state data passed between states.

    Attributes:
        current_state: The active game state
        current_task: The currently assigned workout task (if any)
        score: Current player score
        player_detected: Whether a player is currently detected by the camera
        last_dice_roll: The result of the last dice roll (1-6)
        consecutive_failures: Number of consecutive failed tasks (for difficulty adjustment)
    """

    current_state: Optional["GameState"] = None
    current_task: Optional[WorkoutTask] = None
    score: int = 0
    player_detected: bool = False
    last_dice_roll: int = 0
    consecutive_failures: int = 0
    rolling_current_item: str = ""
    rolling_end_time: float = 0.0

    def reset_task(self) -> None:
        """Clear the current task and temporary state."""
        self.current_task = None
        self.last_dice_roll = 0
        # Keep score and consecutive_failures for session continuity

    def transition_to(self, new_state: "GameState") -> None:
        """Transition to a new state."""
        if self.current_state:
            self.current_state.exit(self)

        self.current_state = new_state
        self.current_state.enter(self)

        # Cleanup when returning to WAITING
        if new_state.name == "WAITING":
            self.reset_task()

    def get_current_message(self) -> str:
        """Get display message from current state."""
        return self.current_state.get_display_message() if self.current_state else ""
