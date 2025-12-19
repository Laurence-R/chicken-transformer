"""Progress tracker for workout tasks.

Manages the counting of reps and sets, and calculates progress.
"""

from dataclasses import dataclass


@dataclass
class ProgressTracker:
    """Tracks progress of a workout session."""

    total_sets: int
    reps_per_set: int
    current_set: int = 1
    current_reps: int = 0

    def increment_rep(self) -> bool:
        """Increment rep count.

        Returns:
            bool: True if a set was completed.
        """
        self.current_reps += 1
        if self.current_reps >= self.reps_per_set:
            return True
        return False

    def next_set(self) -> bool:
        """Move to next set.

        Returns:
            bool: True if all sets are completed (task finished).
        """
        self.current_set += 1
        self.current_reps = 0
        if self.current_set > self.total_sets:
            return True
        return False

    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage (0.0 to 1.0)."""
        total_reps_needed = self.reps_per_set * self.total_sets
        total_reps_done = ((self.current_set - 1) * self.reps_per_set) + self.current_reps

        if total_reps_needed == 0:
            return 0.0
        return min(1.0, total_reps_done / total_reps_needed)

    def get_display_text(self) -> str:
        """Get formatted progress string."""
        return f"Set {self.current_set}/{self.total_sets} | Reps {self.current_reps}/{self.reps_per_set}"
