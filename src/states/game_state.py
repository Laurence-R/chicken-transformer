"""Abstract base class for game states implementing State Pattern.

Defines the interface for all game states (WaitingState, DiceRollDetectingState,
TaskDisplayState, TaskExecutingState, CompletionState).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.data_structures import PoseData
    from ..models.game_context import GameContext


@dataclass
class StateTransition:
    """Result of state update, specifying next state and context changes.
    
    Attributes:
        next_state_name: Name of next state to transition to, or None to stay
        context_updates: Dictionary of GameContext attributes to update
    """
    next_state_name: Optional[str]
    context_updates: dict


class GameState(ABC):
    """Abstract base class for game states.
    
    Implements State Pattern to manage game flow through five states:
    - WAITING: Waiting for player to start
    - DICE_ROLL_DETECTING: Detecting jump + raise hands gesture
    - TASK_DISPLAY: Showing assigned workout task
    - TASK_EXECUTING: Validating exercise execution
    - COMPLETION: Verifying task completion
    
    Contract:
        - enter() must be called before first update()
        - update() called every frame with optional pose data
        - exit() called when transitioning to another state
        - Performance: update() <10ms, enter()/exit() <5ms
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique state identifier.
        
        Returns:
            State name constant (e.g., "WAITING", "DICE_ROLL_DETECTING")
        """
        pass
    
    @abstractmethod
    def enter(self, context: 'GameContext') -> None:
        """Initialize state-specific logic when entering state.
        
        Args:
            context: Game context with shared data and state
            
        Requirements:
            - Set state-specific timers and flags
            - Record entry timestamp for timeout detection
            - Update UI display message
            - Execution time <5ms
            
        Example:
            >>> self.enter_time = time.time()
            >>> context.ui.show_message("請跳躍並舉手擲骰子")
        """
        pass
    
    @abstractmethod
    def update(
        self,
        context: 'GameContext',
        pose_data: Optional['PoseData']
    ) -> StateTransition:
        """Process state logic and determine state transition.
        
        Called every frame by main game loop. Processes pose data,
        checks transition conditions, and returns next state.
        
        Args:
            context: Game context
            pose_data: Current frame pose data, or None if no detection
            
        Returns:
            StateTransition with next state name and context updates.
            If next_state_name is None, remain in current state.
            
        Requirements:
            - Execution time <10ms (99th percentile)
            - Transition conditions must be explicit and testable
            - Must handle pose_data=None gracefully (camera failure)
            
        Example:
            >>> if self._detect_jump(pose_data):
            >>>     return StateTransition(
            >>>         next_state_name="DICE_ROLL_DETECTING",
            >>>         context_updates={"last_action": "jump"}
            >>>     )
            >>> return StateTransition(next_state_name=None, context_updates={})
        """
        pass
    
    @abstractmethod
    def exit(self, context: 'GameContext') -> None:
        """Clean up state-specific resources when leaving state.
        
        Args:
            context: Game context
            
        Requirements:
            - Clear state-specific timers and temporary data
            - Must not raise exceptions (use try-except protection)
            - Execution time <5ms
            
        Example:
            >>> context.clear_temporary_flags()
            >>> self.enter_time = None
        """
        pass
    
    @abstractmethod
    def get_display_message(self) -> str:
        """Get UI prompt message for current state.
        
        Returns:
            Display message in Traditional Chinese for InfoPanel
            
        Requirements:
            - Pure query method (no state modification)
            - Message should be clear and actionable
            
        Examples:
            - "等待開始 - 請跳躍並舉手"
            - "正在擲骰子... (2 秒內)"
            - "任務：深蹲 15 次 x 2 組"
        """
        pass
