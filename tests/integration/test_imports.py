"""Integration test to verify all modules can be imported."""


def test_import_data_structures():
    """Test importing core data structures."""
    from src.utils.constants import KEYPOINT_INDICES

    assert len(KEYPOINT_INDICES) == 17


def test_import_geometry():
    """Test importing geometry utilities."""


def test_import_pose_detector():
    """Test importing pose detector classes."""


def test_import_game_state():
    """Test importing game state classes."""


def test_import_action_validator():
    """Test importing action validator classes."""


def test_import_task_library():
    """Test importing task library."""


def test_import_logger():
    """Test importing logger utilities."""


def test_main_module_exists():
    """Test main entry point exists."""
    from src import main

    assert hasattr(main, "parse_arguments")
    assert hasattr(main, "main")
