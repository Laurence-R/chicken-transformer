"""Task display state implementation.

Shows the assigned task after dice roll.
"""

import time
from typing import TYPE_CHECKING, Optional

from ..models.game_context import GameContext
from ..tasks.workout_task import WorkoutTask
from .game_state import GameState, StateTransition

if TYPE_CHECKING:
    from ..tasks.task_library import TaskLibrary
    from ..utils.data_structures import PoseData


class TaskDisplayState(GameState):
    """Displays the assigned task."""

    def __init__(self, task_library: "TaskLibrary"):
        self.task_library = task_library
        self.display_start_time: Optional[float] = None
        self.DISPLAY_DURATION = 3.0  # Seconds to show the task
        self._message = ""

    @property
    def name(self) -> str:
        return "TASK_DISPLAY"

    def enter(self, context: GameContext) -> None:
        self.display_start_time = time.time()

        # If task is already set (e.g. by RollingState), use it
        if context.current_task:
            task = context.current_task
            self._message = f"點數 {context.last_dice_roll}!\n任務: {task.description}"
            return

        # Otherwise generate task (fallback)
        try:
            exercise, reps, sets = self.task_library.get_random_task()

            # Create WorkoutTask
            task = WorkoutTask(exercise=exercise, target_reps=reps, target_sets=sets)
            context.current_task = task
            self._message = f"點數 {context.last_dice_roll}!\n任務: {task.description}"
        except RuntimeError:
            self._message = "錯誤: 無可用運動"

    def update(self, context: GameContext, pose_data: Optional["PoseData"]) -> StateTransition:
        if time.time() - self.display_start_time > self.DISPLAY_DURATION:
            return StateTransition(next_state_name="TASK_EXECUTING", context_updates={})

        return StateTransition(next_state_name=None, context_updates={})

    def exit(self, context: GameContext) -> None:
        pass

    def get_display_message(self) -> str:
        return self._message
