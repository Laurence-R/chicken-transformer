import pytest
from unittest.mock import MagicMock, patch
from src.tasks.workout_task import WorkoutTask, TaskState
from src.tasks.task_library import ExerciseDefinition, TaskLibrary
from src.game.game_manager import GameManager
from src.models.game_context import GameContext
from src.states.dice_state import DiceRollDetectingState
from src.states.game_state import StateTransition

@pytest.fixture
def sample_exercise():
    return ExerciseDefinition(
        name_zh="測試運動",
        name_en="test_exercise",
        validator_class="TestValidator",
        min_reps=5,
        max_reps=10,
        min_sets=1,
        max_sets=3,
        difficulty="easy"
    )

def test_workout_task_lifecycle(sample_exercise):
    task = WorkoutTask(sample_exercise, target_reps=5, target_sets=1)
    assert task.state == TaskState.PENDING
    
    task.start()
    assert task.state == TaskState.IN_PROGRESS
    
    # Add reps
    for _ in range(4):
        assert not task.add_rep()
        assert task.state == TaskState.IN_PROGRESS
        
    # Complete set
    assert task.add_rep() # 5th rep
    assert task.state == TaskState.COMPLETED

def test_game_manager_transition():
    mock_lib = MagicMock(spec=TaskLibrary)
    manager = GameManager(mock_lib)
    
    state1 = MagicMock()
    state1.name = "STATE1"
    state1.update.return_value = StateTransition(next_state_name="STATE2", context_updates={})
    
    state2 = MagicMock()
    state2.name = "STATE2"
    state2.update.return_value = StateTransition(next_state_name=None, context_updates={})
    
    manager.register_state(state1)
    manager.register_state(state2)
    
    manager.set_initial_state("STATE1")
    assert manager.current_state == state1
    
    manager.update(None)
    assert manager.current_state == state2
    state1.exit.assert_called_once()
    state2.enter.assert_called_once()

def test_dice_roll_logic():
    state = DiceRollDetectingState()
    context = GameContext()
    
    # No pose
    transition = state.update(context, None)
    assert transition.next_state_name == "WAITING"
    
    # Pose without hands up
    mock_pose = MagicMock()
    mock_pose.get_keypoint.side_effect = lambda k: MagicMock(visible=True, y=100) # All same Y
    transition = state.update(context, mock_pose)
    assert transition.next_state_name is None
    
    # Pose with hands up (Wrist Y < Shoulder Y)
    def get_kp(name):
        kp = MagicMock(visible=True)
        if 'wrist' in name:
            kp.y = 50
        elif 'shoulder' in name:
            kp.y = 100
        return kp
    mock_pose.get_keypoint.side_effect = get_kp
    
    # First frame
    transition = state.update(context, mock_pose)
    assert transition.next_state_name is None
    assert state.hold_start_time is not None
    
    # Wait duration
    with patch('time.time', return_value=state.hold_start_time + 1.1):
        transition = state.update(context, mock_pose)
        assert transition.next_state_name == "TASK_DISPLAY"
        assert "last_dice_roll" in transition.context_updates
