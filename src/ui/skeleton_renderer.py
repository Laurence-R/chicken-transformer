import pygame

from ..utils.data_structures import PoseData


class SkeletonRenderer:
    """Renders skeleton keypoints and connections on a PyGame surface."""

    def __init__(self):
        # Define connections between keypoints (limbs)
        self.SKELETON_CONNECTIONS = [
            ("nose", "left_eye"),
            ("nose", "right_eye"),
            ("left_eye", "left_ear"),
            ("right_eye", "right_ear"),
            ("left_shoulder", "right_shoulder"),
            ("left_shoulder", "left_elbow"),
            ("left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow"),
            ("right_elbow", "right_wrist"),
            ("left_shoulder", "left_hip"),
            ("right_shoulder", "right_hip"),
            ("left_hip", "right_hip"),
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
        ]

        self.colors = {
            "joint": (0, 255, 0),  # Green
            "limb": (0, 255, 255),  # Cyan
            "low_conf": (0, 0, 255),  # Blue (low confidence)
            "text": (255, 255, 255),  # White
        }

        self.font = pygame.font.SysFont("Arial", 12)

    def draw(
        self,
        surface: pygame.Surface,
        pose_data: PoseData,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
    ):
        """Draw skeleton on the given surface.

        Args:
            surface: PyGame surface to draw on
            pose_data: PoseData object containing keypoints
            scale_x: Horizontal scaling factor (if frame size != surface size)
            scale_y: Vertical scaling factor
        """
        if not pose_data:
            return

        # Draw limbs
        for start_name, end_name in self.SKELETON_CONNECTIONS:
            try:
                kp1 = pose_data.get_keypoint(start_name)
                kp2 = pose_data.get_keypoint(end_name)

                if kp1.visible and kp2.visible:
                    start_pos = (int(kp1.x * scale_x), int(kp1.y * scale_y))
                    end_pos = (int(kp2.x * scale_x), int(kp2.y * scale_y))
                    pygame.draw.line(surface, self.colors["limb"], start_pos, end_pos, 2)
            except KeyError:
                pass

        # Draw joints
        for kp in pose_data.keypoints:
            pos = (int(kp.x * scale_x), int(kp.y * scale_y))

            if kp.visible:
                pygame.draw.circle(surface, self.colors["joint"], pos, 4)
            elif kp.confidence > 0.1:  # Draw low confidence points differently
                pygame.draw.circle(surface, self.colors["low_conf"], pos, 2)
