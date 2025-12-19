"""Task executing state implementation.

Monitors the user's exercise execution and tracks progress.
"""

import time
from typing import TYPE_CHECKING, Optional

from ..models.game_context import GameContext
from ..tasks.validators.factory import ValidatorFactory
from ..tasks.workout_task import TaskState
from .game_state import GameState, StateTransition

if TYPE_CHECKING:
    from ..utils.data_structures import PoseData


class TaskExecutingState(GameState):
    """Executes the assigned task."""

    def __init__(self):
        self._message = "準備開始..."
        self._feedback = ""
        self.last_activity_time = 0.0
        self.TIMEOUT_DURATION = 60.0  # 60 seconds timeout

    @property
    def name(self) -> str:
        return "TASK_EXECUTING"

    def enter(self, context: GameContext) -> None:
        if context.current_task:
            context.current_task.start()
            self._feedback = ""
            self.last_activity_time = time.time()

            # Initialize validator based on exercise type
            validator_class_name = context.current_task.exercise.validator_class
            context.current_task.validator = ValidatorFactory.create_validator(validator_class_name)

            if not context.current_task.validator:
                self._feedback = f"尚未支援此運動: {context.current_task.exercise.name_zh}"

            self._update_message(context)

    def update(self, context: GameContext, pose_data: Optional["PoseData"]) -> StateTransition:
        if not context.current_task:
            return StateTransition(next_state_name="WAITING", context_updates={})

        if pose_data and pose_data.confidence > 0.5:
            # Reset timeout on valid pose detection
            self.last_activity_time = time.time()

            validator = context.current_task.validator
            if validator:
                result = validator.validate(pose_data)
                self._feedback = result.feedback

                if result.is_valid:
                    if context.current_task.state == TaskState.IN_PROGRESS:
                        context.current_task.add_rep()
            else:
                # Fallback for unsupported exercises (auto-complete for testing)
                # Or just do nothing
                pass

        # Check timeout
        if time.time() - self.last_activity_time > self.TIMEOUT_DURATION:
            self._feedback = "逾時! 任務取消"
            return StateTransition(next_state_name="WAITING", context_updates={})

        self._update_message(context)

        if context.current_task.state == TaskState.COMPLETED:
            return StateTransition(next_state_name="COMPLETION", context_updates={})

        return StateTransition(next_state_name=None, context_updates={})

    def exit(self, context: GameContext) -> None:
        pass

    def get_display_message(self) -> str:
        return f"{self._message}\n{self._feedback}"

    def _update_message(self, context: GameContext):
        if context.current_task:
            self._message = f"{context.current_task.exercise.name_zh}: {context.current_task.current_reps}/{context.current_task.target_reps}"
