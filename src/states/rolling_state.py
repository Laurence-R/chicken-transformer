"""Rolling state implementation.

Displays a lottery/gacha animation before selecting a task.
"""

import random
import time
from typing import TYPE_CHECKING, Optional

from .game_state import GameState, StateTransition

if TYPE_CHECKING:
    from ..models.game_context import GameContext
    from ..tasks.task_library import TaskLibrary
    from ..utils.data_structures import PoseData


class RollingState(GameState):
    """Displays a rolling animation for task selection."""

    def __init__(self, task_library: "TaskLibrary"):
        self.task_library = task_library
        self.start_time: float = 0.0
        self.duration: float = 2.5  # Seconds
        self.last_switch_time: float = 0.0
        self.switch_interval: float = 0.1
        self.current_display_name: str = ""
        self.final_task = None

    @property
    def name(self) -> str:
        return "ROLLING"

    def enter(self, context: "GameContext") -> None:
        self.start_time = time.time()
        self.last_switch_time = self.start_time
        self.switch_interval = 0.05
        
        # Select the final task immediately
        # get_random_task returns (exercise, reps, sets)
        exercise, reps, sets = self.task_library.get_random_task()
        
        # Create a WorkoutTask object
        from ..tasks.workout_task import WorkoutTask
        self.final_task = WorkoutTask(
            exercise=exercise,
            target_reps=reps,
            target_sets=sets
        )
        
        # Set initial display
        self.current_display_name = "Rolling..."
        context.rolling_current_item = self.current_display_name
        context.rolling_end_time = self.start_time + self.duration

    def update(self, context: "GameContext", pose_data: Optional["PoseData"]) -> StateTransition:
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            # Animation finished, transition to Task Display
            context.current_task = self.final_task
            return StateTransition(next_state_name="TASK_DISPLAY", context_updates={})
            
        # Update animation
        if current_time - self.last_switch_time > self.switch_interval:
            self.last_switch_time = current_time
            
            # Pick a random name to display
            # get_random_task returns (exercise, reps, sets) tuple
            random_task_tuple = self.task_library.get_random_task()
            if random_task_tuple:
                exercise, _, _ = random_task_tuple
                # Use Chinese name if available
                name = exercise.name_zh if hasattr(exercise, "name_zh") else exercise.name_en
                self.current_display_name = name
                context.rolling_current_item = name
            
            # Slow down effect
            self.switch_interval *= 1.1
            
        return StateTransition(next_state_name=None, context_updates={})

    def exit(self, context: "GameContext") -> None:
        context.rolling_current_item = ""
        context.rolling_end_time = 0.0

    def get_display_message(self) -> str:
        return f"抽選中...\n{self.current_display_name}"
