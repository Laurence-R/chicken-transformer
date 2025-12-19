"""Workout task state management.

Tracks the progress of a specific assigned exercise task.
"""
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Any
from datetime import datetime
from .task_library import ExerciseDefinition

class TaskState(Enum):
    """Current state of the workout task."""
    PENDING = auto()      # Assigned but not started
    IN_PROGRESS = auto()  # Currently being performed
    COMPLETED = auto()    # Successfully finished
    FAILED = auto()       # Failed or cancelled

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
    current_reps: int = 0
    current_sets: int = 0
    state: TaskState = TaskState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    validator: Optional[Any] = None # Holds the active validator instance
    
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
        if self.state != TaskState.IN_PROGRESS:
            return False
            
        self.current_reps += 1
        if self.current_reps >= self.target_reps:
            self.complete_set()
            return True
        return False
            
    def complete_set(self) -> None:
        """Complete current set and check for task completion."""
        self.current_sets += 1
        self.current_reps = 0 # Reset reps for next set
        
        if self.current_sets >= self.target_sets:
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
            
        total_reps_needed = self.target_reps * self.target_sets
        total_reps_done = (self.current_sets * self.target_reps) + self.current_reps
        
        if total_reps_needed == 0:
            return 0.0
        return min(1.0, total_reps_done / total_reps_needed)

    @property
    def description(self) -> str:
        """Human readable description of the task."""
        return f"{self.exercise.name_zh}: {self.target_sets} 組 x {self.target_reps} 下"
