"""UI Theme configuration."""

class Theme:
    """Centralized theme configuration for the application."""
    
    # Colors (R, G, B)
    COLOR_BG = (30, 30, 35)
    COLOR_PANEL_BG = (40, 40, 45)
    COLOR_TEXT_MAIN = (240, 240, 240)
    COLOR_TEXT_DIM = (180, 180, 180)
    COLOR_ACCENT = (0, 255, 255)  # Cyan
    COLOR_SUCCESS = (50, 255, 50)
    COLOR_WARNING = (255, 40, 40)
    COLOR_HIGHLIGHT = (255, 215, 0) # Gold
    
    # Aliases for semantic usage
    COLOR_BACKGROUND = COLOR_BG
    COLOR_SURFACE = COLOR_PANEL_BG
    COLOR_PRIMARY = COLOR_ACCENT
    COLOR_ERROR = COLOR_WARNING

    # Fonts
    FONT_FAMILY_ZH = ["Noto Sans CJK TC", "Noto Sans CJK SC", "Droid Sans Fallback", "WenQuanYi Zen Hei", "Microsoft JhengHei", "SimHei", "Arial"]
    FONT_SIZE_LARGE = 48
    FONT_SIZE_MEDIUM = 32
    FONT_SIZE_SMALL = 24

    @classmethod
    def get_font(cls, size: int):
        """Get a pygame font object with the specified size."""
        import pygame
        return pygame.font.SysFont(cls.FONT_FAMILY_ZH, size)
