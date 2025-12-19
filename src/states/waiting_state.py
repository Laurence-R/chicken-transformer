"""Waiting state implementation.

Initial state of the game, waiting for a player to be detected.
"""

from typing import TYPE_CHECKING, Optional

from ..models.game_context import GameContext
from .game_state import GameState, StateTransition

if TYPE_CHECKING:
    from ..utils.data_structures import PoseData


class WaitingState(GameState):
    """Waiting for player to enter the frame."""

    @property
    def name(self) -> str:
        return "WAITING"

    def enter(self, context: GameContext) -> None:
        """Reset game context when waiting starts."""
        context.reset_task()
        context.player_detected = False

    def update(self, context: GameContext, pose_data: Optional["PoseData"]) -> StateTransition:
        """Check if a player is detected."""
        if pose_data and pose_data.confidence > 0.5:
            return StateTransition(
                next_state_name="DICE_ROLL_DETECTING", context_updates={"player_detected": True}
            )

        return StateTransition(next_state_name=None, context_updates={})

    def exit(self, context: GameContext) -> None:
        pass

    def get_display_message(self) -> str:
        return "請站在鏡頭前\n準備舉手開始"
