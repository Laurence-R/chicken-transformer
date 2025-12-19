import time
from typing import Optional

import pygame

from ..models.game_context import GameContext
from ..utils.data_structures import PoseData
from .camera_panel import CameraPanel
from .info_panel import InfoPanel


class GameWindow:
    """Main game window managing the UI loop and panels."""

    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        pygame.init()
        pygame.display.set_caption("Fitness Dice Game - 弱雞轉換器")

        self.width = width
        self.height = height
        self.target_fps = fps

        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.running = True

        # Layout: 70% Camera (Left), 30% Info (Right)
        camera_width = int(width * 0.7)
        info_width = width - camera_width

        self.camera_panel = CameraPanel(0, 0, camera_width, height)
        self.info_panel = InfoPanel(camera_width, 0, info_width, height)

    def handle_events(self):
        """Process PyGame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, context: GameContext, frame, pose_data: Optional[PoseData]):
        """Update and render the game window.

        Args:
            context: Current game state context
            frame: Camera frame (BGR numpy array)
            pose_data: Detected pose data
        """
        self.handle_events()

        if not self.running:
            return

        fps = self.clock.get_fps()

        # Low FPS Warning
        if fps < 10 and fps > 0:
            if not hasattr(self, "low_fps_start"):
                self.low_fps_start = time.time()
            elif time.time() - self.low_fps_start > 5.0:
                # Draw warning overlay
                font = pygame.font.SysFont("Arial", 24)
                text = font.render("WARNING: Low Performance", True, (255, 0, 0))
                self.screen.blit(text, (10, 10))
        else:
            if hasattr(self, "low_fps_start"):
                del self.low_fps_start

        # Update panels
        self.camera_panel.update(frame, pose_data)
        self.info_panel.update(context, fps)

        # Draw panels
        self.camera_panel.draw(self.screen)
        self.info_panel.draw(self.screen)

        pygame.display.flip()
        self.clock.tick(self.target_fps)

    def close(self):
        """Clean up resources."""
        pygame.quit()
