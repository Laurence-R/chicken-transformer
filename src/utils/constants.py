"""Constants for pose estimation and game configuration."""

# COCO 17-keypoint pose model keypoint indices
# Standard order used by YOLOv8-Pose and other COCO-based models
KEYPOINT_INDICES = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16,
}

# Game configuration constants
MIN_VISIBLE_KEYPOINTS = 8  # Minimum for valid pose detection
CONFIDENCE_THRESHOLD = 0.5  # Keypoint visibility threshold

# Exercise validation tolerances (degrees)
ANGLE_TOLERANCE_DEFAULT = 15  # ±15° for most exercises
ANGLE_TOLERANCE_STRICT = 10   # ±10° for exercises requiring precision
ANGLE_TOLERANCE_RELAXED = 20  # ±20° for beginner-friendly exercises

# Performance targets (milliseconds)
POSE_DETECTION_TIMEOUT = 50   # Max inference time per frame
VALIDATION_TIMEOUT = 5        # Max validation time per pose
FRAME_RENDER_TIMEOUT = 5      # Max UI render time per frame
