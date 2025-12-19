from unittest.mock import MagicMock

import pytest

from src.tasks.validators.factory import ValidatorFactory
from src.tasks.validators.jumping_jack_validator import JumpingJackState, JumpingJackValidator
from src.tasks.validators.squat_validator import SquatValidator
from src.utils.data_structures import Keypoint, PoseData


def test_validator_factory():
    # Test existing validators
    v1 = ValidatorFactory.create_validator("SquatValidator")
    assert isinstance(v1, SquatValidator)

    v2 = ValidatorFactory.create_validator("JumpingJackValidator")
    assert isinstance(v2, JumpingJackValidator)

    # Test non-existent validator
    v3 = ValidatorFactory.create_validator("NonExistentValidator")
    assert v3 is None

    # Test invalid name format
    v4 = ValidatorFactory.create_validator("InvalidName")
    assert v4 is None


@pytest.fixture
def mock_pose_data():
    pose = MagicMock(spec=PoseData)
    pose.confidence = 0.9

    def get_keypoint(name):
        kp = MagicMock(spec=Keypoint)
        kp.visible = True
        kp.confidence = 0.9
        # Default positions
        kp.x = 100
        kp.y = 100
        return kp

    pose.get_keypoint.side_effect = get_keypoint
    return pose


def test_jumping_jack_validator_flow(mock_pose_data):
    validator = JumpingJackValidator()
    pose = mock_pose_data

    # Mock calculate_distance
    with pytest.MonkeyPatch.context() as m:
        # Setup keypoint positions for logic
        # We need to control:
        # 1. shoulder_width (fixed)
        # 2. feet_distance (variable)
        # 3. hands_up/down (variable via y coords)

        # Mock calculate_distance to return values based on inputs
        # This is tricky with lambda, so we define a side_effect function
        def mock_dist(p1, p2):
            # Identify points by some property or just return controlled values
            # Since we can't easily identify mock objects, we'll rely on the order of calls
            # or just mock the result directly if we can control the flow step by step
            return 0  # Placeholder

        # Better approach: Mock the return value for specific calls?
        # Or just mock the logic inside validator? No, we want to test logic.

        # Let's just mock calculate_distance to return specific values for each step
        # Step 1: Closed (Feet close, Hands down)
        # shoulder_width = 50
        # feet_distance = 30 (< 50)

        # We need to set keypoint y values for hands
        # Hands down: wrist.y > shoulder.y

        l_shoulder = MagicMock(y=50)
        r_shoulder = MagicMock(y=50)
        l_wrist = MagicMock(y=100)  # Down
        r_wrist = MagicMock(y=100)  # Down

        pose.get_keypoint.side_effect = lambda name: {
            "left_shoulder": l_shoulder,
            "right_shoulder": r_shoulder,
            "left_wrist": l_wrist,
            "right_wrist": r_wrist,
            "left_ankle": MagicMock(),
            "right_ankle": MagicMock(),
            "left_hip": MagicMock(),
            "right_hip": MagicMock(),
        }.get(name, MagicMock())

        # 1. Initial Closed State
        # feet_dist = 30, shoulder_width = 50
        m.setattr(
            "src.tasks.validators.jumping_jack_validator.calculate_distance",
            lambda p1, p2: 50 if p1 == l_shoulder else 30,
        )

        res = validator.validate(pose)
        assert validator.state == JumpingJackState.CLOSED

        # 2. Opening (Feet open, Hands still down)
        # feet_dist = 80 (> 1.5*50=75), Hands down
        m.setattr(
            "src.tasks.validators.jumping_jack_validator.calculate_distance",
            lambda p1, p2: 50 if p1 == l_shoulder else 80,
        )
        res = validator.validate(pose)
        assert validator.state == JumpingJackState.OPENING

        # 3. Open (Feet open, Hands up)
        # Hands up: wrist.y < shoulder.y
        l_wrist.y = 0
        r_wrist.y = 0
        res = validator.validate(pose)
        assert validator.state == JumpingJackState.OPEN
        assert "到達頂點" in res.feedback

        # 4. Closing (Feet closed, Hands up)
        # feet_dist = 30, Hands up
        m.setattr(
            "src.tasks.validators.jumping_jack_validator.calculate_distance",
            lambda p1, p2: 50 if p1 == l_shoulder else 30,
        )
        res = validator.validate(pose)
        assert validator.state == JumpingJackState.CLOSING

        # 5. Closed (Feet closed, Hands down) -> Complete
        # Hands down
        l_wrist.y = 100
        r_wrist.y = 100
        res = validator.validate(pose)
        assert validator.state == JumpingJackState.CLOSED
        assert res.is_valid
        assert "完成" in res.feedback
