"""Game Manager implementation.

Central controller that manages the game loop, state transitions, and
coordination between the pose detector, task library, and UI.
"""

import logging
from typing import TYPE_CHECKING, Dict, Optional

from ..models.game_context import GameContext
from ..states.game_state import GameState
from ..tasks.task_library import TaskLibrary

if TYPE_CHECKING:
    from ..utils.data_structures import PoseData


class GameManager:
    """Central game controller implementing the State Pattern runner.

    Attributes:
        context: Shared game state data
        task_library: Library of available exercises
        states: Dictionary of registered game states
        current_state: Currently active game state
    """

    def __init__(self, task_library: TaskLibrary):
        """Initialize the game manager.

        Args:
            task_library: Initialized task library instance
        """
        self.context = GameContext()
        self.task_library = task_library
        self.states: Dict[str, GameState] = {}
        self.current_state: Optional[GameState] = None
        self.logger = logging.getLogger(__name__)

    def register_state(self, state: GameState) -> None:
        """Register a game state instance.

        Args:
            state: The state instance to register
        """
        self.states[state.name] = state
        self.logger.debug(f"Registered state: {state.name}")

    def set_initial_state(self, state_name: str) -> None:
        """Set the starting state of the game.

        Args:
            state_name: Name of the state to start in
        """
        if state_name not in self.states:
            raise ValueError(f"Unknown state: {state_name}")

        self.current_state = self.states[state_name]
        self.context.current_state = self.current_state  # Sync context
        self.logger.info(f"Setting initial state: {state_name}")
        self.current_state.enter(self.context)

    def update(self, pose_data: Optional["PoseData"]) -> None:
        """Update the game loop.

        Args:
            pose_data: Current frame pose data from detector
        """
        if not self.current_state:
            return

        # Update current state
        transition = self.current_state.update(self.context, pose_data)

        # Apply context updates
        for key, value in transition.context_updates.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
            else:
                self.logger.warning(f"Attempted to update unknown context key: {key}")

        # Handle state transition
        if transition.next_state_name and transition.next_state_name != self.current_state.name:
            self.transition_to(transition.next_state_name)

    def transition_to(self, state_name: str) -> None:
        """Execute transition to a new state.

        Args:
            state_name: Name of the target state
        """
        if state_name not in self.states:
            self.logger.error(f"Cannot transition to unknown state: {state_name}")
            return

        self.logger.info(f"Transitioning: {self.current_state.name} -> {state_name}")

        # Exit current state
        self.current_state.exit(self.context)

        # Enter new state
        self.current_state = self.states[state_name]
        self.context.current_state = self.current_state  # Sync context
        self.current_state.enter(self.context)

    def get_current_message(self) -> str:
        """Get the display message from the current state."""
        if self.current_state:
            return self.current_state.get_display_message()
        return ""
