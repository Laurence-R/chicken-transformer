# Data Model: Enhance Game Experience

## UI Theme

A centralized configuration for UI aesthetics.

```python
class Theme:
    # Colors (R, G, B)
    COLOR_BG = (30, 30, 35)
    COLOR_PANEL_BG = (40, 40, 45)
    COLOR_TEXT_MAIN = (240, 240, 240)
    COLOR_TEXT_DIM = (180, 180, 180)
    COLOR_ACCENT = (0, 255, 255)  # Cyan
    COLOR_SUCCESS = (50, 255, 50)
    COLOR_WARNING = (255, 40, 40)
    
    # Fonts
    FONT_FAMILY_ZH = ["Noto Sans CJK TC", "Microsoft JhengHei", "SimHei"]
    FONT_SIZE_LARGE = 48
    FONT_SIZE_MEDIUM = 32
    FONT_SIZE_SMALL = 24
```

## Game Context Updates

The `GameContext` will be updated to support the Rolling state.

### Context Variables

| Variable | Type | Description |
| :--- | :--- | :--- |
| `rolling_current_item` | `str` | The name of the exercise currently being displayed during the rolling animation. |
| `rolling_end_time` | `float` | Timestamp when the rolling animation should finish. |

## State Machine Updates

### RollingState

- **Input**: `None` (Time-based)
- **Output**: `TaskDisplayState`
- **Transitions**:
    - `DiceRollDetectingState` -> `RollingState`
    - `RollingState` -> `TaskDisplayState`
