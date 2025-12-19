"""Unit tests for geometry utilities."""

from src.utils.data_structures import Keypoint
from src.utils.geometry import (
    calculate_angle,
    calculate_distance,
    calculate_horizontal_distance,
    calculate_vertical_distance,
    is_angle_in_range,
    is_point_above,
)


class TestCalculateAngle:
    """Test angle calculation function."""

    def test_right_angle(self):
        """Test 90-degree angle calculation."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=200, confidence=0.9)  # Vertex
        p3 = Keypoint(x=200, y=200, confidence=0.9)

        angle = calculate_angle(p1, p2, p3)
        assert abs(angle - 90.0) < 0.1

    def test_straight_angle(self):
        """Test 180-degree angle (straight line)."""
        p1 = Keypoint(x=0, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=100, confidence=0.9)
        p3 = Keypoint(x=200, y=100, confidence=0.9)

        angle = calculate_angle(p1, p2, p3)
        assert abs(angle - 180.0) < 0.1

    def test_acute_angle(self):
        """Test acute angle (45 degrees)."""
        p1 = Keypoint(x=100, y=0, confidence=0.9)
        p2 = Keypoint(x=100, y=100, confidence=0.9)
        p3 = Keypoint(x=200, y=100, confidence=0.9)

        angle = calculate_angle(p1, p2, p3)
        assert 89 < angle < 91  # Should be ~90°

    def test_zero_angle_collinear(self):
        """Test collinear points (degenerate case)."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=100, confidence=0.9)  # Same as p1
        p3 = Keypoint(x=200, y=200, confidence=0.9)

        angle = calculate_angle(p1, p2, p3)
        assert angle == 0.0  # Degenerate case


class TestIsAngleInRange:
    """Test angle range checking."""

    def test_angle_within_range(self):
        """Test angle within tolerance."""
        assert is_angle_in_range(85, 90, 15) is True
        assert is_angle_in_range(95, 90, 15) is True
        assert is_angle_in_range(90, 90, 15) is True

    def test_angle_outside_range(self):
        """Test angle outside tolerance."""
        assert is_angle_in_range(70, 90, 15) is False
        assert is_angle_in_range(110, 90, 15) is False

    def test_angle_at_boundary(self):
        """Test angle at exact boundary."""
        assert is_angle_in_range(75, 90, 15) is True  # Exactly at boundary
        assert is_angle_in_range(105, 90, 15) is True

    def test_custom_tolerance(self):
        """Test with custom tolerance values."""
        assert is_angle_in_range(88, 90, 5) is True
        assert is_angle_in_range(85, 90, 5) is True
        assert is_angle_in_range(84, 90, 5) is False


class TestCalculateDistance:
    """Test distance calculation."""

    def test_horizontal_distance(self):
        """Test distance along horizontal line."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=200, y=100, confidence=0.9)

        distance = calculate_distance(p1, p2)
        assert distance == 100.0

    def test_vertical_distance(self):
        """Test distance along vertical line."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=200, confidence=0.9)

        distance = calculate_distance(p1, p2)
        assert distance == 100.0

    def test_diagonal_distance(self):
        """Test Euclidean distance on diagonal."""
        p1 = Keypoint(x=0, y=0, confidence=0.9)
        p2 = Keypoint(x=3, y=4, confidence=0.9)

        distance = calculate_distance(p1, p2)
        assert distance == 5.0  # 3-4-5 triangle

    def test_zero_distance(self):
        """Test distance between same point."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=100, confidence=0.9)

        distance = calculate_distance(p1, p2)
        assert distance == 0.0


class TestVerticalDistance:
    """Test vertical distance calculation."""

    def test_positive_vertical_distance(self):
        """Test vertical distance when p2 is below p1."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=200, confidence=0.9)

        distance = calculate_vertical_distance(p1, p2)
        assert distance == 100.0

    def test_negative_vertical_distance(self):
        """Test vertical distance when p2 is above p1."""
        p1 = Keypoint(x=100, y=200, confidence=0.9)
        p2 = Keypoint(x=100, y=100, confidence=0.9)

        distance = calculate_vertical_distance(p1, p2)
        assert distance == -100.0

    def test_zero_vertical_distance(self):
        """Test zero vertical distance."""
        p1 = Keypoint(x=100, y=150, confidence=0.9)
        p2 = Keypoint(x=200, y=150, confidence=0.9)

        distance = calculate_vertical_distance(p1, p2)
        assert distance == 0.0


class TestHorizontalDistance:
    """Test horizontal distance calculation."""

    def test_positive_horizontal_distance(self):
        """Test horizontal distance when p2 is right of p1."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=200, y=100, confidence=0.9)

        distance = calculate_horizontal_distance(p1, p2)
        assert distance == 100.0

    def test_negative_horizontal_distance(self):
        """Test horizontal distance when p2 is left of p1."""
        p1 = Keypoint(x=200, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=100, confidence=0.9)

        distance = calculate_horizontal_distance(p1, p2)
        assert distance == -100.0


class TestIsPointAbove:
    """Test point elevation comparison."""

    def test_point_above(self):
        """Test when p1 is above p2."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=200, confidence=0.9)

        assert is_point_above(p1, p2) is True

    def test_point_below(self):
        """Test when p1 is below p2."""
        p1 = Keypoint(x=100, y=200, confidence=0.9)
        p2 = Keypoint(x=100, y=100, confidence=0.9)

        assert is_point_above(p1, p2) is False

    def test_point_at_same_level(self):
        """Test when points are at same Y coordinate."""
        p1 = Keypoint(x=100, y=150, confidence=0.9)
        p2 = Keypoint(x=200, y=150, confidence=0.9)

        assert is_point_above(p1, p2) is False

    def test_point_above_with_threshold(self):
        """Test with threshold margin."""
        p1 = Keypoint(x=100, y=100, confidence=0.9)
        p2 = Keypoint(x=100, y=105, confidence=0.9)

        assert is_point_above(p1, p2, threshold=0) is True
        assert is_point_above(p1, p2, threshold=10) is False  # Within threshold
