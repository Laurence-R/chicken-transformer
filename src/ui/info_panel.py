import pygame

from ..models.game_context import GameContext
from .theme import Theme


class InfoPanel:
    """Panel for displaying game status, instructions, and progress."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA) # Enable alpha for rounded corners if needed

        self.font_large = pygame.font.SysFont(Theme.FONT_FAMILY_ZH, Theme.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.SysFont(Theme.FONT_FAMILY_ZH, Theme.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.SysFont(Theme.FONT_FAMILY_ZH, Theme.FONT_SIZE_SMALL)

        # Fallback to default if still issues (will not support Chinese properly)
        if not self.font_large.get_height():
            print("Warning: No Chinese font found, falling back to default.")
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)

        self.bg_color = Theme.COLOR_PANEL_BG
        self.text_color = Theme.COLOR_TEXT_MAIN
        self.highlight_color = Theme.COLOR_HIGHLIGHT
        
        # Text cache to avoid re-rendering same strings
        self._text_cache = {}

    def _render_text(self, text: str, font: pygame.font.Font, color: tuple) -> pygame.Surface:
        """Render text with caching."""
        key = (text, color, font)
        if key in self._text_cache:
            return self._text_cache[key]
        
        surface = font.render(text, True, color)
        
        # Simple eviction policy
        if len(self._text_cache) > 200:
            self._text_cache.clear()
            
        self._text_cache[key] = surface
        return surface

    def update(self, context: GameContext, fps: float):
        """Update panel content based on game context."""
        self.surface.fill(Theme.COLOR_BG)
        
        # Draw rounded panel background
        rect = self.surface.get_rect()
        pygame.draw.rect(self.surface, self.bg_color, rect, border_radius=15)
        pygame.draw.rect(self.surface, Theme.COLOR_ACCENT, rect, width=2, border_radius=15)

        y_offset = 20
        padding = 20

        # 1. State Name
        state_name = context.current_state.name if context.current_state else "INIT"
        text = self._render_text(f"狀態: {state_name}", self.font_large, self.highlight_color)
        self.surface.blit(text, (padding, y_offset))
        y_offset += 50

        # 2. Message
        msg = context.get_current_message()
        lines = msg.split("\n")
        for line in lines:
            # Basic word wrap or just print lines
            text = self._render_text(line, self.font_medium, self.text_color)
            self.surface.blit(text, (padding, y_offset))
            y_offset += 35

        y_offset += 20

        # Special handling for Rolling state
        if state_name == "ROLLING" and context.rolling_current_item:
             text = self._render_text(context.rolling_current_item, self.font_large, (0, 255, 255))
             self.surface.blit(text, (padding, y_offset))
             y_offset += 50

        # 3. Task Info (if executing)
        if context.current_task:
            task = context.current_task

            # Exercise Name
            ex_name = task.exercise.name_zh if hasattr(task, "exercise") else task.exercise_type
            text = self._render_text(f"任務: {ex_name}", self.font_medium, (100, 255, 255))
            self.surface.blit(text, (padding, y_offset))
            y_offset += 40  # Increased from 30

            # Target
            text = self._render_text(
                f"目標: {task.target_reps} 次 x {task.target_sets} 組", self.font_small, (200, 200, 200)
            )
            self.surface.blit(text, (padding, y_offset))
            y_offset += 30  # Increased from 25

            # Difficulty
            diff = task.exercise.difficulty if hasattr(task, "exercise") else "N/A"
            text = self._render_text(f"難度: {diff}", self.font_small, (200, 200, 200))
            self.surface.blit(text, (padding, y_offset))
            y_offset += 55  # Increased from 35

            # Progress Bar
            if context.current_task:
                task = context.current_task
                # Display current set progress
                current_set_display = (
                    task.current_sets + 1
                    if task.current_sets < task.target_sets
                    else task.target_sets
                )
                progress_text = f"進度: {task.current_reps}/{task.target_reps} (第 {current_set_display}/{task.target_sets} 組)"

                text = self._render_text(progress_text, self.font_medium, (0, 255, 0))
                self.surface.blit(text, (padding, y_offset))
                y_offset += 40  # Increased from 30

                # Bar
                bar_width = self.rect.width - 2 * padding
                bar_height = 20
                pygame.draw.rect(
                    self.surface, (100, 100, 100), (padding, y_offset, bar_width, bar_height)
                )

                if task.target_reps > 0:
                    pct = min(1.0, task.current_reps / task.target_reps)
                    fill_width = int(bar_width * pct)
                    pygame.draw.rect(
                        self.surface, (0, 255, 0), (padding, y_offset, fill_width, bar_height)
                    )
                y_offset += 30

        # 4. Score
        score_text = f"總分: {context.score}"
        text = self.font_large.render(score_text, True, self.highlight_color)
        self.surface.blit(text, (padding, self.rect.height - 80))

        # 5. FPS
        fps_text = f"FPS: {fps:.1f}"
        text = self.font_small.render(fps_text, True, (150, 150, 150))
        self.surface.blit(text, (self.rect.width - 100, self.rect.height - 30))

    def draw(self, screen: pygame.Surface):
        """Draw the panel onto the main screen."""
        screen.blit(self.surface, self.rect.topleft)
