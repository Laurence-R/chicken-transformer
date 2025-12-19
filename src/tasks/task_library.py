"""Task library management for exercise definitions.

Loads exercise configurations from JSON and provides random task generation.
"""

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ExerciseDefinition:
    """Definition of a single exercise type.

    Attributes:
        name_zh: Traditional Chinese name (e.g., "深蹲")
        name_en: English identifier (e.g., "squat")
        validator_class: Name of validator class (e.g., "SquatValidator")
        min_reps: Minimum repetitions per set
        max_reps: Maximum repetitions per set
        min_sets: Minimum number of sets
        max_sets: Maximum number of sets
        difficulty: Difficulty level ("easy", "medium", "hard")
    """

    name_zh: str
    name_en: str
    validator_class: str
    min_reps: int
    max_reps: int
    min_sets: int
    max_sets: int
    difficulty: str

    def __post_init__(self):
        """Validate exercise definition constraints."""
        if not self.name_zh or not self.name_en:
            raise ValueError("Exercise names cannot be empty")
        if self.min_reps < 1 or self.max_reps < self.min_reps:
            raise ValueError(f"Invalid rep range: {self.min_reps}-{self.max_reps}")
        if self.min_sets < 1 or self.max_sets < self.min_sets:
            raise ValueError(f"Invalid set range: {self.min_sets}-{self.max_sets}")
        if self.difficulty not in ("easy", "medium", "hard"):
            raise ValueError(f"Invalid difficulty: {self.difficulty}")


class TaskLibrary:
    """Manages exercise definitions and generates random workout tasks.

    Loads exercise library from JSON configuration file and provides
    methods for random task selection and validation.
    """

    def __init__(self):
        """Initialize empty task library."""
        self.exercises: Dict[str, ExerciseDefinition] = {}
        self.config_path: Optional[Path] = None

    def load_from_json(self, path: str) -> None:
        """Load exercise library from JSON file.

        Args:
            path: Path to exercises.json configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If JSON format is invalid or library is incomplete

        Expected JSON format:
            [
                {
                    "name_zh": "深蹲",
                    "name_en": "squat",
                    "validator_class": "SquatValidator",
                    "min_reps": 5,
                    "max_reps": 20,
                    "min_sets": 1,
                    "max_sets": 3,
                    "difficulty": "medium"
                },
                ...
            ]
        """
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"Exercise config not found: {path}")

        self.config_path = config_file

        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Exercise config must be JSON array")

        self.exercises = {}
        for item in data:
            try:
                exercise = ExerciseDefinition(
                    name_zh=item["name_zh"],
                    name_en=item["name_en"],
                    validator_class=item["validator_class"],
                    min_reps=item["min_reps"],
                    max_reps=item["max_reps"],
                    min_sets=item["min_sets"],
                    max_sets=item["max_sets"],
                    difficulty=item["difficulty"],
                )
                self.exercises[exercise.name_en] = exercise
            except KeyError as e:
                raise ValueError(
                    f"Missing required field in exercise definition: {e}"
                ) from e

    def get_random_task(self) -> tuple[ExerciseDefinition, int, int]:
        """Generate random workout task from library.

        Returns:
            Tuple of (exercise_definition, reps_per_set, total_sets)

        Raises:
            RuntimeError: If library is empty or not loaded

        Example:
            >>> library = TaskLibrary()
            >>> library.load_from_json("config/exercises.json")
            >>> exercise, reps, sets = library.get_random_task()
            >>> print(f"{exercise.name_zh} {reps} 次 x {sets} 組")
            深蹲 15 次 x 2 組
        """
        if not self.exercises:
            raise RuntimeError("Task library is empty. Call load_from_json() first.")

        # Select random exercise
        exercise = random.choice(list(self.exercises.values()))

        # Generate random reps and sets within exercise constraints
        reps = random.randint(exercise.min_reps, exercise.max_reps)
        sets = random.randint(exercise.min_sets, exercise.max_sets)

        return exercise, reps, sets

    def get_exercise(self, exercise_type: str) -> ExerciseDefinition:
        """Get exercise definition by English name.

        Args:
            exercise_type: English exercise identifier (e.g., "squat")

        Returns:
            ExerciseDefinition for requested exercise

        Raises:
            KeyError: If exercise type not found in library
        """
        if exercise_type not in self.exercises:
            available = ", ".join(self.exercises.keys())
            raise KeyError(
                f"Exercise '{exercise_type}' not found. " f"Available exercises: {available}"
            )
        return self.exercises[exercise_type]

    def validate_library(self) -> bool:
        """Validate exercise library completeness.

        Returns:
            True if library contains at least 10 exercises
        """
        return len(self.exercises) >= 10

    def list_exercises(self) -> list[str]:
        """Get list of all available exercise names.

        Returns:
            List of exercise English identifiers
        """
        return list(self.exercises.keys())

    def get_exercises_by_difficulty(self, difficulty: str) -> list[ExerciseDefinition]:
        """Get all exercises of specified difficulty level.

        Args:
            difficulty: "easy", "medium", or "hard"

        Returns:
            List of exercises matching difficulty
        """
        return [ex for ex in self.exercises.values() if ex.difficulty == difficulty]
