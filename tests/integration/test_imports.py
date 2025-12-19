"""Integration test to verify all modules can be imported."""
import pytest


def test_import_data_structures():
    """Test importing core data structures."""
    from src.utils.data_structures import Keypoint, BoundingBox, PoseData
    from src.utils.constants import KEYPOINT_INDICES
    assert len(KEYPOINT_INDICES) == 17


def test_import_geometry():
    """Test importing geometry utilities."""
    from src.utils.geometry import (
        calculate_angle,
        is_angle_in_range,
        calculate_distance
    )


def test_import_pose_detector():
    """Test importing pose detector classes."""
    from src.models.pose_detector import PoseDetector
    from src.models.mock_detector import MockPoseDetector


def test_import_game_state():
    """Test importing game state classes."""
    from src.states.game_state import GameState, StateTransition


def test_import_action_validator():
    """Test importing action validator classes."""
    from src.tasks.validators.action_validator import (
        ActionValidator,
        ValidationResult
    )


def test_import_task_library():
    """Test importing task library."""
    from src.tasks.task_library import TaskLibrary, ExerciseDefinition


def test_import_logger():
    """Test importing logger utilities."""
    from src.utils.logger import setup_logger, get_logger


def test_main_module_exists():
    """Test main entry point exists."""
    from src import main
    assert hasattr(main, 'parse_arguments')
    assert hasattr(main, 'main')
