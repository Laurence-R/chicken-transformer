"""Workout task state management.

Tracks the progress of a specific assigned exercise task.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional

from .progress_tracker import ProgressTracker
from .task_library import ExerciseDefinition


class TaskState(Enum):
    """Current state of the workout task."""

    PENDING = auto()  # Assigned but not started
    IN_PROGRESS = auto()  # Currently being performed
    COMPLETED = auto()  # Successfully finished
    FAILED = auto()  # Failed or cancelled


@dataclass
class WorkoutTask:
    """Represents a specific workout assignment (e.g., '10 Squats').

    Attributes:
        exercise: The definition of the exercise to perform
        target_reps: Number of repetitions required per set
        target_sets: Number of sets required
        task_id: Unique identifier for this task instance
    """

    exercise: ExerciseDefinition
    target_reps: int
    target_sets: int
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # State tracking
    tracker: Optional[ProgressTracker] = None
    state: TaskState = TaskState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    validator: Optional[Any] = None  # Holds the active validator instance

    def __post_init__(self):
        """Initialize progress tracker."""
        self.tracker = ProgressTracker(total_sets=self.target_sets, reps_per_set=self.target_reps)

    @property
    def current_reps(self) -> int:
        return self.tracker.current_reps if self.tracker else 0

    @property
    def current_sets(self) -> int:
        return self.tracker.current_set - 1 if self.tracker else 0  # Tracker is 1-based

    def start(self) -> None:
        """Mark task as started."""
        if self.state == TaskState.PENDING:
            self.state = TaskState.IN_PROGRESS
            self.start_time = datetime.now()

    def add_rep(self) -> bool:
        """Increment rep count and check for set completion.

        Returns:
            bool: True if a set was completed, False otherwise.
        """
        if self.state != TaskState.IN_PROGRESS or not self.tracker:
            return False

        set_completed = self.tracker.increment_rep()

        if set_completed:
            self.complete_set()
            return True
        return False

    def complete_set(self) -> None:
        """Complete current set and check for task completion."""
        if not self.tracker:
            return

        task_completed = self.tracker.next_set()

        if task_completed:
            self.complete_task()

    def complete_task(self) -> None:
        """Mark task as fully completed."""
        self.state = TaskState.COMPLETED
        self.end_time = datetime.now()

    @property
    def progress_percent(self) -> float:
        """Calculate overall progress percentage (0.0 to 1.0)."""
        if self.state == TaskState.COMPLETED:
            return 1.0
        return self.tracker.get_progress_percentage() if self.tracker else 0.0

    @property
    def description(self) -> str:
        """Human readable description of the task."""
        return f"{self.exercise.name_zh}: {self.target_sets} 組 x {self.target_reps} 下"
