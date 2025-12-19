"""End-to-end integration test for Phase 2 components."""
import pytest
import numpy as np
from src.models.mock_detector import MockPoseDetector
from src.tasks.task_library import TaskLibrary
from src.utils.geometry import calculate_angle, calculate_distance
from src.utils.logger import setup_logger


class TestPhase2Integration:
    """Integration tests for Phase 2 foundational components."""
    
    def test_mock_detector_with_geometry(self):
        """Test MockPoseDetector output works with geometry utilities."""
        detector = MockPoseDetector(mode="squatting", confidence=0.9)
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        pose_data = detector.detect(frame)
        
        assert pose_data is not None
        assert pose_data.is_valid()
        
        # Test geometry calculations on detected pose
        left_hip = pose_data.get_keypoint('left_hip')
        left_knee = pose_data.get_keypoint('left_knee')
        left_ankle = pose_data.get_keypoint('left_ankle')
        
        # Calculate knee angle
        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        assert 0 <= knee_angle <= 180
        
        # Calculate hip-knee distance
        distance = calculate_distance(left_hip, left_knee)
        assert distance > 0
        
        detector.release()
    
    def test_task_library_with_config_file(self):
        """Test TaskLibrary loads actual config file."""
        library = TaskLibrary()
        library.load_from_json("config/exercises.json")
        
        assert len(library.exercises) >= 10
        assert library.validate_library()
        
        # Generate random task
        exercise, reps, sets = library.get_random_task()
        assert exercise.min_reps <= reps <= exercise.max_reps
        assert exercise.min_sets <= sets <= exercise.max_sets
    
    def test_pose_detection_multiple_frames(self):
        """Test detector handles multiple frames correctly."""
        detector = MockPoseDetector(mode="standing", confidence=0.85)
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Detect 10 frames
        frame_ids = []
        for _ in range(10):
            pose_data = detector.detect(frame)
            assert pose_data is not None
            frame_ids.append(pose_data.frame_id)
        
        # Verify frame IDs increment
        assert frame_ids == list(range(1, 11))
        
        detector.release()
    
    def test_pose_mode_switching_workflow(self):
        """Test realistic pose mode switching scenario."""
        detector = MockPoseDetector(mode="standing")
        detector.initialize()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Standing pose
        pose1 = detector.detect(frame)
        standing_hip_y = pose1.get_keypoint('left_hip').y
        
        # Switch to squatting
        detector.set_mode("squatting")
        pose2 = detector.detect(frame)
        squatting_hip_y = pose2.get_keypoint('left_hip').y
        
        # Hips should be lower (higher Y) in squatting
        assert squatting_hip_y > standing_hip_y
        
        # Switch to jumping
        detector.set_mode("jumping")
        pose3 = detector.detect(frame)
        jumping_wrist_y = pose3.get_keypoint('left_wrist').y
        jumping_shoulder_y = pose3.get_keypoint('left_shoulder').y
        
        # Wrists should be above shoulders in jumping
        assert jumping_wrist_y < jumping_shoulder_y
        
        detector.release()
    
    def test_logger_setup(self):
        """Test logger initialization."""
        logger = setup_logger(
            name="test_logger",
            log_file="logs/test.log",
            console=False,
            file_logging=True
        )
        
        assert logger is not None
        logger.info("Test log message")
        logger.debug("Test debug message")
    
    def test_complete_workflow_simulation(self):
        """Test simulated game workflow with all components."""
        # 1. Initialize detector
        detector = MockPoseDetector(mode="standing")
        detector.initialize()
        
        # 2. Load task library
        library = TaskLibrary()
        library.load_from_json("config/exercises.json")
        
        # 3. Get random task
        exercise, reps, sets = library.get_random_task()
        
        # 4. Simulate detection loop
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        
        detected_poses = []
        for i in range(5):
            pose_data = detector.detect(frame)
            assert pose_data is not None
            assert pose_data.is_valid()
            detected_poses.append(pose_data)
        
        # 5. Verify all poses are valid
        assert len(detected_poses) == 5
        for pose in detected_poses:
            assert pose.confidence > 0.0
            assert len(pose.keypoints) == 17
        
        # 6. Test geometry on last pose
        last_pose = detected_poses[-1]
        left_shoulder = last_pose.get_keypoint('left_shoulder')
        right_shoulder = last_pose.get_keypoint('right_shoulder')
        shoulder_width = calculate_distance(left_shoulder, right_shoulder)
        assert shoulder_width > 0
        
        # 7. Cleanup
        detector.release()
        
        print(f"\n✓ Workflow test passed:")
        print(f"  - Exercise: {exercise.name_zh} ({exercise.name_en})")
        print(f"  - Task: {reps} reps x {sets} sets")
        print(f"  - Detected {len(detected_poses)} valid poses")
        print(f"  - Shoulder width: {shoulder_width:.1f}px")
