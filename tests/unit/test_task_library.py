"""Unit tests for TaskLibrary."""
import pytest
import json
import tempfile
from pathlib import Path
from src.tasks.task_library import TaskLibrary, ExerciseDefinition


class TestExerciseDefinition:
    """Test ExerciseDefinition dataclass."""
    
    def test_create_valid_exercise(self):
        """Test creating valid exercise definition."""
        exercise = ExerciseDefinition(
            name_zh="深蹲",
            name_en="squat",
            validator_class="SquatValidator",
            min_reps=5,
            max_reps=20,
            min_sets=1,
            max_sets=3,
            difficulty="medium"
        )
        assert exercise.name_zh == "深蹲"
        assert exercise.name_en == "squat"
        assert exercise.difficulty == "medium"
    
    def test_invalid_rep_range(self):
        """Test that invalid rep range raises ValueError."""
        with pytest.raises(ValueError):
            ExerciseDefinition(
                name_zh="深蹲",
                name_en="squat",
                validator_class="SquatValidator",
                min_reps=20,  # min > max
                max_reps=10,
                min_sets=1,
                max_sets=3,
                difficulty="medium"
            )
    
    def test_invalid_difficulty(self):
        """Test that invalid difficulty raises ValueError."""
        with pytest.raises(ValueError):
            ExerciseDefinition(
                name_zh="深蹲",
                name_en="squat",
                validator_class="SquatValidator",
                min_reps=5,
                max_reps=20,
                min_sets=1,
                max_sets=3,
                difficulty="super_hard"  # Invalid
            )
    
    def test_empty_name(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError):
            ExerciseDefinition(
                name_zh="",
                name_en="squat",
                validator_class="SquatValidator",
                min_reps=5,
                max_reps=20,
                min_sets=1,
                max_sets=3,
                difficulty="medium"
            )


class TestTaskLibrary:
    """Test TaskLibrary class."""
    
    @pytest.fixture
    def sample_exercises_json(self):
        """Create temporary JSON file with sample exercises."""
        exercises = [
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
            {
                "name_zh": "伏地挺身",
                "name_en": "pushup",
                "validator_class": "PushupValidator",
                "min_reps": 5,
                "max_reps": 15,
                "min_sets": 1,
                "max_sets": 3,
                "difficulty": "hard"
            },
            {
                "name_zh": "開合跳",
                "name_en": "jumping_jack",
                "validator_class": "JumpingJackValidator",
                "min_reps": 10,
                "max_reps": 30,
                "min_sets": 1,
                "max_sets": 5,
                "difficulty": "easy"
            }
        ]
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(exercises, temp_file)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        Path(temp_file.name).unlink()
    
    def test_load_from_json(self, sample_exercises_json):
        """Test loading exercises from JSON file."""
        library = TaskLibrary()
        library.load_from_json(sample_exercises_json)
        
        assert len(library.exercises) == 3
        assert "squat" in library.exercises
        assert "pushup" in library.exercises
        assert "jumping_jack" in library.exercises
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file raises error."""
        library = TaskLibrary()
        with pytest.raises(FileNotFoundError):
            library.load_from_json("/nonexistent/path/exercises.json")
    
    def test_get_exercise(self, sample_exercises_json):
        """Test retrieving specific exercise."""
        library = TaskLibrary()
        library.load_from_json(sample_exercises_json)
        
        exercise = library.get_exercise("squat")
        assert exercise.name_zh == "深蹲"
        assert exercise.difficulty == "medium"
    
    def test_get_nonexistent_exercise(self, sample_exercises_json):
        """Test retrieving non-existent exercise raises error."""
        library = TaskLibrary()
        library.load_from_json(sample_exercises_json)
        
        with pytest.raises(KeyError):
            library.get_exercise("nonexistent_exercise")
    
    def test_get_random_task(self, sample_exercises_json):
        """Test generating random task."""
        library = TaskLibrary()
        library.load_from_json(sample_exercises_json)
        
        exercise, reps, sets = library.get_random_task()
        
        assert isinstance(exercise, ExerciseDefinition)
        assert exercise.min_reps <= reps <= exercise.max_reps
        assert exercise.min_sets <= sets <= exercise.max_sets
    
    def test_get_random_task_without_loading(self):
        """Test getting random task before loading raises error."""
        library = TaskLibrary()
        with pytest.raises(RuntimeError):
            library.get_random_task()
    
    def test_list_exercises(self, sample_exercises_json):
        """Test listing all exercises."""
        library = TaskLibrary()
        library.load_from_json(sample_exercises_json)
        
        exercises = library.list_exercises()
        assert len(exercises) == 3
        assert "squat" in exercises
        assert "pushup" in exercises
        assert "jumping_jack" in exercises
    
    def test_get_exercises_by_difficulty(self, sample_exercises_json):
        """Test filtering exercises by difficulty."""
        library = TaskLibrary()
        library.load_from_json(sample_exercises_json)
        
        easy_exercises = library.get_exercises_by_difficulty("easy")
        assert len(easy_exercises) == 1
        assert easy_exercises[0].name_en == "jumping_jack"
        
        medium_exercises = library.get_exercises_by_difficulty("medium")
        assert len(medium_exercises) == 1
        
        hard_exercises = library.get_exercises_by_difficulty("hard")
        assert len(hard_exercises) == 1
    
    def test_validate_library_insufficient_exercises(self, sample_exercises_json):
        """Test validation fails with <10 exercises."""
        library = TaskLibrary()
        library.load_from_json(sample_exercises_json)
        
        # Only 3 exercises loaded
        assert library.validate_library() is False
    
    def test_load_actual_config_file(self):
        """Test loading actual config/exercises.json file."""
        library = TaskLibrary()
        library.load_from_json("config/exercises.json")
        
        assert len(library.exercises) >= 10
        assert library.validate_library() is True
