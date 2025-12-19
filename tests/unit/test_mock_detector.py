"""Unit tests for MockPoseDetector."""
import pytest
import numpy as np
from src.models.mock_detector import MockPoseDetector


class TestMockPoseDetector:
    """Test MockPoseDetector for WSL development."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = MockPoseDetector(mode="standing")
        assert detector.initialize() is True
        assert detector.initialized is True
    
    def test_standing_pose_detection(self):
        """Test detection in standing mode."""
        detector = MockPoseDetector(mode="standing", confidence=0.9)
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        pose_data = detector.detect(frame)
        
        assert pose_data is not None
        assert len(pose_data.keypoints) == 17
        assert pose_data.confidence == 0.9
        assert pose_data.is_valid()  # Should have >=8 visible keypoints
    
    def test_squatting_pose_detection(self):
        """Test detection in squatting mode."""
        detector = MockPoseDetector(mode="squatting", confidence=0.85)
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        pose_data = detector.detect(frame)
        
        assert pose_data is not None
        assert pose_data.is_valid()
        
        # Verify hips are lowered (higher Y value in image coords)
        left_hip = pose_data.get_keypoint('left_hip')
        left_knee = pose_data.get_keypoint('left_knee')
        assert left_hip.y < left_knee.y  # Hip above knee in squatting pose
    
    def test_jumping_pose_detection(self):
        """Test detection in jumping mode."""
        detector = MockPoseDetector(mode="jumping", confidence=0.9)
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        pose_data = detector.detect(frame)
        
        assert pose_data is not None
        
        # Verify arms are raised (wrists above shoulders)
        left_wrist = pose_data.get_keypoint('left_wrist')
        left_shoulder = pose_data.get_keypoint('left_shoulder')
        assert left_wrist.y < left_shoulder.y  # Wrist above shoulder
    
    def test_mode_switching(self):
        """Test dynamically changing pose mode."""
        detector = MockPoseDetector(mode="standing")
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Get standing pose
        pose1 = detector.detect(frame)
        nose1 = pose1.get_keypoint('nose')
        
        # Switch to squatting
        detector.set_mode("squatting")
        pose2 = detector.detect(frame)
        nose2 = pose2.get_keypoint('nose')
        
        # Nose should be lower in squatting pose
        assert nose2.y > nose1.y
    
    def test_invalid_mode(self):
        """Test that invalid mode raises ValueError."""
        with pytest.raises(ValueError):
            MockPoseDetector(mode="invalid_mode")
        
        detector = MockPoseDetector(mode="standing")
        with pytest.raises(ValueError):
            detector.set_mode("invalid_mode")
    
    def test_frame_counting(self):
        """Test frame counter increments."""
        detector = MockPoseDetector()
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        pose1 = detector.detect(frame)
        assert pose1.frame_id == 1
        
        pose2 = detector.detect(frame)
        assert pose2.frame_id == 2
        
        pose3 = detector.detect(frame)
        assert pose3.frame_id == 3
    
    def test_noise_addition(self):
        """Test noise is added to keypoints when configured."""
        detector_no_noise = MockPoseDetector(mode="standing", noise_level=0.0)
        detector_no_noise.initialize()
        
        detector_with_noise = MockPoseDetector(mode="standing", noise_level=5.0)
        detector_with_noise.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        pose1 = detector_no_noise.detect(frame)
        pose2 = detector_with_noise.detect(frame)
        
        # Keypoints should differ due to noise
        nose1 = pose1.get_keypoint('nose')
        nose2 = pose2.get_keypoint('nose')
        
        # With noise, positions should likely differ
        assert nose1.x != nose2.x or nose1.y != nose2.y
    
    def test_get_model_info(self):
        """Test model info retrieval."""
        detector = MockPoseDetector(mode="standing")
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        detector.detect(frame)  # Detect once to get timing
        
        info = detector.get_model_info()
        
        assert info["model_name"] == "mock-standing"
        assert info["backend"] == "mock"
        assert info["precision"] == "none"
        assert isinstance(info["avg_inference_time_ms"], float)
    
    def test_get_input_size(self):
        """Test input size matches YOLOv8."""
        detector = MockPoseDetector()
        assert detector.get_input_size() == (640, 640)
    
    def test_release(self):
        """Test resource release."""
        detector = MockPoseDetector()
        detector.initialize()
        detector.release()
        
        assert detector.initialized is False
        assert detector.frame_count == 0
    
    def test_detect_before_initialize(self):
        """Test detecting before initialization raises error."""
        detector = MockPoseDetector()
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        with pytest.raises(RuntimeError):
            detector.detect(frame)
