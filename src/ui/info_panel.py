import pygame

from ..models.game_context import GameContext


class InfoPanel:
    """Panel for displaying game status, instructions, and progress."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))

        # Font setup - try to find a font that supports Chinese
        # Priority: Noto Sans CJK (Jetson default), Droid Sans Fallback, then others
        font_names = [
            "Noto Sans CJK TC",
            "Noto Sans CJK SC",
            "Droid Sans Fallback",
            "WenQuanYi Zen Hei",
            "Microsoft JhengHei",
        ]
        
        self.font_large = pygame.font.SysFont(font_names, 32)
        self.font_medium = pygame.font.SysFont(font_names, 24)
        self.font_small = pygame.font.SysFont(font_names, 18)

        # Fallback to default if still issues (will not support Chinese properly)
        if not self.font_large.get_height():
            print("Warning: No Chinese font found, falling back to default.")
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)

        self.bg_color = (50, 50, 50)
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 215, 0)  # Gold

    def update(self, context: GameContext, fps: float):
        """Update panel content based on game context."""
        self.surface.fill(self.bg_color)

        y_offset = 20
        padding = 20

        # 1. State Name
        state_name = context.current_state.name if context.current_state else "INIT"
        text = self.font_large.render(f"狀態: {state_name}", True, self.highlight_color)
        self.surface.blit(text, (padding, y_offset))
        y_offset += 50

        # 2. Message
        msg = context.get_current_message()
        lines = msg.split("\n")
        for line in lines:
            # Basic word wrap or just print lines
            text = self.font_medium.render(line, True, self.text_color)
            self.surface.blit(text, (padding, y_offset))
            y_offset += 35

        y_offset += 20

        # 3. Task Info (if executing)
        if context.current_task:
            task = context.current_task

            # Exercise Name
            ex_name = task.exercise.name_zh if hasattr(task, "exercise") else task.exercise_type
            text = self.font_medium.render(f"任務: {ex_name}", True, (100, 255, 255))
            self.surface.blit(text, (padding, y_offset))
            y_offset += 30

            # Target
            text = self.font_small.render(
                f"目標: {task.target_reps} 次 x {task.target_sets} 組", True, (200, 200, 200)
            )
            self.surface.blit(text, (padding, y_offset))
            y_offset += 25

            # Difficulty
            diff = task.exercise.difficulty if hasattr(task, "exercise") else "N/A"
            text = self.font_small.render(f"難度: {diff}", True, (200, 200, 200))
            self.surface.blit(text, (padding, y_offset))
            y_offset += 35

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

                text = self.font_medium.render(progress_text, True, (0, 255, 0))
                self.surface.blit(text, (padding, y_offset))
                y_offset += 30

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
