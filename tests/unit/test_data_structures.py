"""Unit tests for core data structures."""

import pytest

from src.utils.constants import KEYPOINT_INDICES
from src.utils.data_structures import BoundingBox, Keypoint, PoseData


class TestKeypoint:
    """Test Keypoint dataclass."""

    def test_create_visible_keypoint(self):
        """Test creating keypoint with high confidence."""
        kp = Keypoint(x=100, y=200, confidence=0.9)
        assert kp.x == 100
        assert kp.y == 200
        assert kp.confidence == 0.9
        assert kp.visible is True  # confidence > 0.5

    def test_create_invisible_keypoint(self):
        """Test creating keypoint with low confidence."""
        kp = Keypoint(x=100, y=200, confidence=0.3)
        assert kp.visible is False  # confidence <= 0.5

    def test_invalid_coordinates(self):
        """Test that negative coordinates raise ValueError."""
        with pytest.raises(ValueError):
            Keypoint(x=-10, y=100, confidence=0.9)
        with pytest.raises(ValueError):
            Keypoint(x=100, y=-10, confidence=0.9)

    def test_invalid_confidence(self):
        """Test that confidence outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError):
            Keypoint(x=100, y=200, confidence=1.5)
        with pytest.raises(ValueError):
            Keypoint(x=100, y=200, confidence=-0.1)


class TestBoundingBox:
    """Test BoundingBox dataclass."""

    def test_create_valid_bbox(self):
        """Test creating valid bounding box."""
        bbox = BoundingBox(x1=50, y1=100, x2=200, y2=300)
        assert bbox.x1 == 50
        assert bbox.y1 == 100
        assert bbox.x2 == 200
        assert bbox.y2 == 300
        assert bbox.width == 150  # 200 - 50
        assert bbox.height == 200  # 300 - 100

    def test_invalid_bbox(self):
        """Test that invalid bbox (x2 < x1) raises ValueError."""
        with pytest.raises(ValueError):
            BoundingBox(x1=200, y1=100, x2=50, y2=300)


class TestPoseData:
    """Test PoseData dataclass."""

    @pytest.fixture
    def sample_keypoints(self):
        """Create 17 sample keypoints."""
        return [Keypoint(x=i * 10, y=i * 20, confidence=0.8) for i in range(17)]

    @pytest.fixture
    def sample_bbox(self):
        """Create sample bounding box."""
        return BoundingBox(x1=0, y1=0, x2=640, y2=640)

    def test_create_valid_pose_data(self, sample_keypoints, sample_bbox):
        """Test creating valid PoseData."""
        pose = PoseData(
            keypoints=sample_keypoints,
            bbox=sample_bbox,
            confidence=0.85,
            frame_id=10,
            timestamp=1234567890.0,
        )
        assert len(pose.keypoints) == 17
        assert pose.confidence == 0.85
        assert pose.frame_id == 10

    def test_invalid_keypoint_count(self, sample_bbox):
        """Test that non-17 keypoints raises ValueError."""
        with pytest.raises(ValueError):
            PoseData(
                keypoints=[Keypoint(0, 0, 0.9) for _ in range(10)],
                bbox=sample_bbox,
                confidence=0.85,
                frame_id=1,
                timestamp=0.0,
            )

    def test_get_keypoint_by_name(self, sample_keypoints, sample_bbox):
        """Test retrieving keypoint by COCO name."""
        pose = PoseData(
            keypoints=sample_keypoints, bbox=sample_bbox, confidence=0.85, frame_id=1, timestamp=0.0
        )

        nose = pose.get_keypoint("nose")
        assert nose == sample_keypoints[0]

        left_shoulder = pose.get_keypoint("left_shoulder")
        assert left_shoulder == sample_keypoints[KEYPOINT_INDICES["left_shoulder"]]

    def test_get_invalid_keypoint_name(self, sample_keypoints, sample_bbox):
        """Test that invalid keypoint name raises KeyError."""
        pose = PoseData(
            keypoints=sample_keypoints, bbox=sample_bbox, confidence=0.85, frame_id=1, timestamp=0.0
        )

        with pytest.raises(KeyError):
            pose.get_keypoint("invalid_keypoint")

    def test_is_valid_sufficient_keypoints(self, sample_bbox):
        """Test is_valid() returns True with >=8 visible keypoints."""
        keypoints = [Keypoint(x=i * 10, y=i * 20, confidence=0.9) for i in range(17)]  # 17 visible
        pose = PoseData(
            keypoints=keypoints, bbox=sample_bbox, confidence=0.85, frame_id=1, timestamp=0.0
        )
        assert pose.is_valid() is True

    def test_is_valid_insufficient_keypoints(self, sample_bbox):
        """Test is_valid() returns False with <8 visible keypoints."""
        # Only 5 visible keypoints
        keypoints = [
            Keypoint(x=i * 10, y=i * 20, confidence=0.9 if i < 5 else 0.3) for i in range(17)
        ]
        pose = PoseData(
            keypoints=keypoints, bbox=sample_bbox, confidence=0.85, frame_id=1, timestamp=0.0
        )
        assert pose.is_valid() is False

    def test_get_skeleton_lines(self, sample_keypoints, sample_bbox):
        """Test skeleton line generation."""
        pose = PoseData(
            keypoints=sample_keypoints, bbox=sample_bbox, confidence=0.85, frame_id=1, timestamp=0.0
        )

        lines = pose.get_skeleton_lines()
        assert len(lines) > 0
        assert all(isinstance(line, tuple) and len(line) == 2 for line in lines)
        assert all(isinstance(kp, Keypoint) for line in lines for kp in line)
