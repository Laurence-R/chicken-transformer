from typing import Optional

import cv2
import numpy as np
import pygame

from ..utils.data_structures import PoseData
from .skeleton_renderer import SkeletonRenderer
from .theme import Theme


class CameraPanel:
    """Panel for displaying camera feed and skeleton overlay."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.skeleton_renderer = SkeletonRenderer()
        self.surface = pygame.Surface((width, height))
        
        # Font setup for camera panel (FPS etc)
        self.font = Theme.get_font(24)

    def update(self, frame: Optional[np.ndarray], pose_data: Optional[PoseData]):
        """Update the panel content.

        Args:
            frame: BGR numpy array from camera/detector (H, W, 3)
            pose_data: Detected pose data
        """
        self.surface.fill((0, 0, 0))  # Clear black

        if frame is not None:
            # 1. Resize using OpenCV (Faster than PyGame)
            # We resize to the panel dimensions
            resized_frame = cv2.resize(frame, (self.rect.width, self.rect.height))

            # 2. Convert BGR to RGB using OpenCV
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            # 3. Create Surface directly from buffer (no scaling needed in PyGame)
            # Since we resized, the dimensions match self.rect
            img_surface = pygame.image.frombuffer(
                frame_rgb.tobytes(), (self.rect.width, self.rect.height), "RGB"
            )

            self.surface.blit(img_surface, (0, 0))

            # Calculate scale factors for skeleton
            # Keypoints are in original frame coordinates (w, h)
            h, w = frame.shape[:2]
            scale_x = self.rect.width / w
            scale_y = self.rect.height / h

            # Draw skeleton
            if pose_data:
                self.skeleton_renderer.draw(self.surface, pose_data, scale_x, scale_y)
        else:
            # No frame available
            text = self.font.render("No Camera Feed", True, Theme.COLOR_TEXT_MAIN)
            text_rect = text.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
            self.surface.blit(text, text_rect)

    def draw(self, screen: pygame.Surface):
        """Draw the panel onto the main screen."""
        screen.blit(self.surface, self.rect.topleft)
