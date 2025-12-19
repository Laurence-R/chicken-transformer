import pygame
import numpy as np
from typing import Optional
from .skeleton_renderer import SkeletonRenderer
from ..utils.data_structures import PoseData

class CameraPanel:
    """Panel for displaying camera feed and skeleton overlay."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.skeleton_renderer = SkeletonRenderer()
        self.surface = pygame.Surface((width, height))
        self.font = pygame.font.SysFont("Arial", 24)

    def update(self, frame: Optional[np.ndarray], pose_data: Optional[PoseData]):
        """Update the panel content.
        
        Args:
            frame: BGR numpy array from camera/detector (H, W, 3)
            pose_data: Detected pose data
        """
        self.surface.fill((0, 0, 0)) # Clear black

        if frame is not None:
            # Frame is expected to be HxWx3 BGR (OpenCV format)
            # Convert to RGB for PyGame
            # Note: We assume frame is a numpy array.
            
            # Manual BGR to RGB conversion (slicing is fast enough for MVP)
            frame_rgb = frame[..., ::-1]
            
            h, w, c = frame_rgb.shape
            
            # Create PyGame surface from buffer
            # We need to transpose axes because PyGame uses (width, height) but numpy uses (height, width)
            # Actually pygame.image.frombuffer expects data in row-major order (like numpy), 
            # but we need to specify the dimensions correctly (w, h).
            img_surface = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")
            
            # Scale to fit panel
            img_surface = pygame.transform.scale(img_surface, (self.rect.width, self.rect.height))
            self.surface.blit(img_surface, (0, 0))
            
            # Calculate scale factors for skeleton
            # Keypoints are in original frame coordinates (w, h)
            scale_x = self.rect.width / w
            scale_y = self.rect.height / h
            
            # Draw skeleton
            if pose_data:
                self.skeleton_renderer.draw(self.surface, pose_data, scale_x, scale_y)
        else:
            # No frame available
            text = self.font.render("No Camera Feed", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
            self.surface.blit(text, text_rect)

    def draw(self, screen: pygame.Surface):
        """Draw the panel onto the main screen."""
        screen.blit(self.surface, self.rect.topleft)
