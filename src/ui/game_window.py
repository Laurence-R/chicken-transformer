import time
from typing import Optional

import pygame

from ..models.game_context import GameContext
from ..utils.data_structures import PoseData
from .camera_panel import CameraPanel
from .info_panel import InfoPanel
from .theme import Theme


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
        
        # Pre-render warning text
        self.warning_font = Theme.get_font(24)
        self.warning_text = self.warning_font.render("WARNING: Low Performance", True, Theme.COLOR_ERROR)

    def handle_events(self):
        """Process PyGame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def draw_loading_screen(self, progress: float, message: str):
        """Draw a loading screen with progress bar.
        
        Args:
            progress: Float between 0.0 and 1.0
            message: Text to display
        """
        self.handle_events()  # Keep window responsive
        
        self.screen.fill(Theme.COLOR_BACKGROUND)
        
        # Draw Title
        title_font = Theme.get_font(48)
        title_surf = title_font.render("Fitness Dice Game", True, Theme.COLOR_PRIMARY)
        title_rect = title_surf.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title_surf, title_rect)
        
        # Draw Message
        msg_font = Theme.get_font(24)
        msg_surf = msg_font.render(message, True, Theme.COLOR_TEXT_MAIN)
        msg_rect = msg_surf.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(msg_surf, msg_rect)
        
        # Draw Progress Bar
        bar_width = 400
        bar_height = 20
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height // 2 + 60
        
        # Background
        pygame.draw.rect(self.screen, Theme.COLOR_SURFACE, (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        # Fill
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, Theme.COLOR_ACCENT, (bar_x, bar_y, fill_width, bar_height), border_radius=10)
            
        pygame.display.flip()

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
                self.screen.blit(self.warning_text, (10, 10))
        else:
            if hasattr(self, "low_fps_start"):
                del self.low_fps_start

        # Update panels
        self.camera_panel.update(frame, pose_data)
        self.info_panel.update(context, fps)

        # Draw panels
        self.camera_panel.draw(self.screen)
        self.info_panel.draw(self.screen)

        # Use update with specific rects instead of flip for potential performance gain
        # (though with full screen video, the gain is minimal)
        pygame.display.update([self.camera_panel.rect, self.info_panel.rect])
        self.clock.tick(self.target_fps)

    def close(self):
        """Clean up resources."""
        pygame.quit()
