import pytest
from unittest.mock import MagicMock
from src.tasks.validators.squat_validator import SquatValidator, SquatState
from src.tasks.validators.pushup_validator import PushupValidator, PushupState
from src.utils.data_structures import PoseData, Keypoint

@pytest.fixture
def mock_pose_data():
    """Create a mock PoseData object with helper to set keypoints."""
    pose = MagicMock(spec=PoseData)
    pose.confidence = 0.9
    
    def get_keypoint(name):
        kp = MagicMock(spec=Keypoint)
        kp.visible = True
        kp.confidence = 0.9
        kp.x = 0
        kp.y = 0
        return kp
    
    pose.get_keypoint.side_effect = get_keypoint
    return pose

def test_squat_validator_flow(mock_pose_data):
    validator = SquatValidator()
    pose = mock_pose_data
    
    # Mock calculate_angle to control the flow
    # We need to patch calculate_angle where it is imported in the validator module
    with pytest.MonkeyPatch.context() as m:
        # 1. Standing (170 deg)
        m.setattr("src.tasks.validators.squat_validator.calculate_angle", lambda p1, p2, p3: 170.0)
        res = validator.validate(pose)
        assert validator.state == SquatState.STANDING
        assert not res.is_valid
        
        # 2. Start Descending (150 deg)
        m.setattr("src.tasks.validators.squat_validator.calculate_angle", lambda p1, p2, p3: 150.0)
        res = validator.validate(pose)
        assert validator.state == SquatState.DESCENDING
        assert "開始下蹲" in res.feedback
        
        # 3. Bottom (80 deg)
        m.setattr("src.tasks.validators.squat_validator.calculate_angle", lambda p1, p2, p3: 80.0)
        res = validator.validate(pose)
        assert validator.state == SquatState.BOTTOM
        assert "到達底部" in res.feedback
        
        # 4. Ascending (120 deg)
        m.setattr("src.tasks.validators.squat_validator.calculate_angle", lambda p1, p2, p3: 120.0)
        res = validator.validate(pose)
        assert validator.state == SquatState.ASCENDING
        assert "正在起立" in res.feedback
        
        # 5. Back to Standing (170 deg) -> Complete
        m.setattr("src.tasks.validators.squat_validator.calculate_angle", lambda p1, p2, p3: 170.0)
        res = validator.validate(pose)
        assert validator.state == SquatState.STANDING
        assert res.is_valid
        assert "完成" in res.feedback

def test_pushup_validator_flow(mock_pose_data):
    validator = PushupValidator()
    pose = mock_pose_data
    
    with pytest.MonkeyPatch.context() as m:
        # 1. Up (170 deg)
        m.setattr("src.tasks.validators.pushup_validator.calculate_angle", lambda p1, p2, p3: 170.0)
        res = validator.validate(pose)
        assert validator.state == PushupState.UP
        
        # 2. Descending (150 deg)
        m.setattr("src.tasks.validators.pushup_validator.calculate_angle", lambda p1, p2, p3: 150.0)
        res = validator.validate(pose)
        assert validator.state == PushupState.DESCENDING
        
        # 3. Down (80 deg)
        m.setattr("src.tasks.validators.pushup_validator.calculate_angle", lambda p1, p2, p3: 80.0)
        res = validator.validate(pose)
        assert validator.state == PushupState.DOWN
        
        # 4. Ascending (120 deg)
        m.setattr("src.tasks.validators.pushup_validator.calculate_angle", lambda p1, p2, p3: 120.0)
        res = validator.validate(pose)
        assert validator.state == PushupState.ASCENDING
        
        # 5. Up (170 deg) -> Complete
        m.setattr("src.tasks.validators.pushup_validator.calculate_angle", lambda p1, p2, p3: 170.0)
        res = validator.validate(pose)
        assert validator.state == PushupState.UP
        assert res.is_valid
