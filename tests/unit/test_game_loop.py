import pytest
import time
from unittest.mock import MagicMock, patch
from src.states.completion_state import CompletionState
from src.states.task_executing_state import TaskExecutingState
from src.models.game_context import GameContext
from src.tasks.workout_task import WorkoutTask, TaskState

def test_completion_state_scoring():
    state = CompletionState()
    context = GameContext()
    context.score = 0
    
    # Mock a completed task
    mock_task = MagicMock(spec=WorkoutTask)
    mock_task.target_reps = 15
    context.current_task = mock_task
    
    state.enter(context)
    
    # Base score 10 + reps 15 = 25
    assert context.score == 25
    assert "25" in state.get_display_message()

def test_completion_state_transition():
    state = CompletionState()
    context = GameContext()
    state.enter(context)
    
    # Before duration
    with patch('time.time', return_value=state.enter_time + 1.0):
        transition = state.update(context, None)
        assert transition.next_state_name is None
        
    # After duration
    with patch('time.time', return_value=state.enter_time + 3.1):
        transition = state.update(context, None)
        assert transition.next_state_name == "WAITING"

def test_task_executing_timeout():
    state = TaskExecutingState()
    context = GameContext()
    
    # Setup task
    mock_task = MagicMock(spec=WorkoutTask)
    mock_task.state = TaskState.IN_PROGRESS
    mock_task.target_reps = 10
    mock_task.current_reps = 0
    
    # Configure the mock exercise properly
    mock_exercise = MagicMock()
    mock_exercise.name_en = "squat"
    mock_exercise.name_zh = "深蹲"
    mock_task.exercise = mock_exercise
    
    context.current_task = mock_task
    
    state.enter(context)
    
    # Simulate timeout
    with patch('time.time', return_value=state.last_activity_time + 61.0):
        transition = state.update(context, None) # No pose data
        assert transition.next_state_name == "WAITING"
        assert "逾時" in state._feedback

def test_task_executing_activity_reset():
    state = TaskExecutingState()
    context = GameContext()
    
    mock_task = MagicMock(spec=WorkoutTask)
    mock_task.state = TaskState.IN_PROGRESS
    mock_task.target_reps = 10
    mock_task.current_reps = 0
    
    mock_exercise = MagicMock()
    mock_exercise.name_en = "squat"
    mock_exercise.name_zh = "深蹲"
    mock_task.exercise = mock_exercise
    
    context.current_task = mock_task
    
    state.enter(context)
    initial_time = state.last_activity_time
    
    # Simulate activity (valid pose)
    mock_pose = MagicMock()
    mock_pose.confidence = 0.9
    
    # Mock keypoints for validator
    def get_keypoint(name):
        kp = MagicMock()
        kp.visible = True
        kp.confidence = 0.9
        kp.x = 0
        kp.y = 0
        return kp
    mock_pose.get_keypoint.side_effect = get_keypoint
    
    # Advance time slightly
    with patch('time.time', return_value=initial_time + 10.0):
        # We also need to patch calculate_angle to avoid errors in validator logic
        with patch("src.tasks.validators.squat_validator.calculate_angle", return_value=170.0):
            state.update(context, mock_pose)
            assert state.last_activity_time > initial_time
