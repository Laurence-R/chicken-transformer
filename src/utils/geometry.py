"""Geometry utilities for pose angle calculation and distance measurement."""

import math

import numpy as np

from .data_structures import Keypoint


def calculate_angle(p1: Keypoint, p2: Keypoint, p3: Keypoint) -> float:
    """Calculate angle formed by three keypoints (p1-p2-p3).

    Computes the angle at vertex p2, formed by rays p2→p1 and p2→p3.
    Uses arctangent to compute the angle between two vectors.

    Args:
        p1: First point (end of first ray)
        p2: Vertex point (angle vertex)
        p3: Third point (end of second ray)

    Returns:
        Angle in degrees (0-180). Returns 0 if points are collinear.

    Example:
        >>> shoulder = Keypoint(100, 100, 0.9, True)
        >>> elbow = Keypoint(150, 150, 0.9, True)
        >>> wrist = Keypoint(200, 150, 0.9, True)
        >>> angle = calculate_angle(shoulder, elbow, wrist)  # ~45 degrees
    """
    # Convert keypoints to vectors relative to p2
    v1 = np.array([p1.x - p2.x, p1.y - p2.y])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y])

    # Calculate vector magnitudes
    mag1 = np.linalg.norm(v1)
    mag2 = np.linalg.norm(v2)

    # Handle degenerate cases (points too close)
    if mag1 < 1e-6 or mag2 < 1e-6:
        return 0.0

    # Normalize vectors
    v1_unit = v1 / mag1
    v2_unit = v2 / mag2

    # Calculate dot product and clamp to valid range for arccos
    dot_product = np.clip(np.dot(v1_unit, v2_unit), -1.0, 1.0)

    # Calculate angle in radians, then convert to degrees
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)

    return float(angle_deg)


def is_angle_in_range(angle: float, target: float, tolerance: float = 15.0) -> bool:
    """Check if measured angle is within tolerance of target angle.

    Used for exercise validation to determine if a pose meets the
    required angle criteria (e.g., squat knee angle 90° ± 15°).

    Args:
        angle: Measured angle in degrees
        target: Target angle in degrees
        tolerance: Allowed deviation from target (default ±15°)

    Returns:
        True if |angle - target| <= tolerance

    Example:
        >>> is_angle_in_range(85, 90, 15)  # True (within 15° of 90°)
        True
        >>> is_angle_in_range(70, 90, 15)  # False (20° away)
        False
    """
    deviation = abs(angle - target)
    return deviation <= tolerance


def calculate_distance(p1: Keypoint, p2: Keypoint) -> float:
    """Calculate Euclidean distance between two keypoints.

    Used for spatial validation (e.g., checking if feet are shoulder-width
    apart, measuring jump height by vertical displacement).

    Args:
        p1: First keypoint
        p2: Second keypoint

    Returns:
        Euclidean distance in pixels

    Example:
        >>> left_ankle = Keypoint(100, 500, 0.9, True)
        >>> right_ankle = Keypoint(200, 500, 0.9, True)
        >>> distance = calculate_distance(left_ankle, right_ankle)  # 100.0
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.sqrt(dx * dx + dy * dy)


def calculate_vertical_distance(p1: Keypoint, p2: Keypoint) -> float:
    """Calculate vertical distance between two keypoints (Y-axis only).

    Useful for measuring height differences, such as jump detection
    or checking body alignment.

    Args:
        p1: First keypoint
        p2: Second keypoint

    Returns:
        Vertical distance in pixels (positive if p2 is below p1)
    """
    return p2.y - p1.y


def calculate_horizontal_distance(p1: Keypoint, p2: Keypoint) -> float:
    """Calculate horizontal distance between two keypoints (X-axis only).

    Useful for measuring lateral separation, such as stance width
    or arm extension.

    Args:
        p1: First keypoint
        p2: Second keypoint

    Returns:
        Horizontal distance in pixels (positive if p2 is right of p1)
    """
    return p2.x - p1.x


def is_point_above(p1: Keypoint, p2: Keypoint, threshold: float = 0.0) -> bool:
    """Check if p1 is above p2 in image coordinates.

    Note: In image coordinates, Y increases downward, so "above" means
    smaller Y value.

    Args:
        p1: First keypoint
        p2: Second keypoint
        threshold: Additional margin in pixels (default 0)

    Returns:
        True if p1.y < p2.y - threshold
    """
    return p1.y < (p2.y - threshold)
