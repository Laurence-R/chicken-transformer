# Research: Enhance Game Experience

**Feature**: Enhance Game Experience
**Date**: 2025-12-20

## Research Task 1: PyGame Optimization on Jetson

**Question**: What is the most efficient way to render camera frames in PyGame on Jetson Orin Nano?

**Findings**:
- PyGame's `pygame.transform.scale` and `pygame.image.frombuffer` are CPU-bound and can be slow for high-resolution images (640x480 or higher).
- OpenCV (`cv2`) functions are highly optimized (often using SIMD/NEON instructions on ARM) and are generally faster for image manipulation than PyGame's software renderer.
- **Benchmark (Estimated)**:
    - PyGame Scale: ~15-20ms per frame (HD)
    - OpenCV Resize: ~2-5ms per frame (HD)
- **Conclusion**: We should perform all image resizing and color conversion using OpenCV *before* handing the data to PyGame.

**Decision**:
- Use `cv2.resize()` to scale the frame to the exact panel dimensions.
- Use `cv2.cvtColor()` to convert BGR to RGB.
- Use `pygame.image.frombuffer()` only for the final surface creation.

## Research Task 2: Lottery Animation Design

**Question**: How to implement a "Gacha" style animation without external assets or blocking the main loop?

**Findings**:
- **Blocking**: `time.sleep()` is forbidden in the main loop. We must use the state machine's `update()` method which is called every frame.
- **Visuals**: A "Slot Machine" effect can be achieved by rapidly cycling through the names/icons of available exercises.
- **Duration**: 2-3 seconds is the sweet spot for anticipation.
- **Implementation**:
    - `RollingState` tracks `start_time`.
    - Every `update()`, if `current_time - last_switch_time > switch_interval` (e.g., 0.1s), pick a random exercise to display.
    - Decrease `switch_interval` over time to create a "slowing down" effect (optional but nice).

**Decision**:
- Implement `RollingState` with a timer-based slot machine effect.
- Display the text of random exercises in the center of the screen.
- Use the new `Theme` colors for a flashy effect.

## Research Task 3: UI Theming

**Question**: What color palette should we use?

**Decision**: "Cyber Fitness" Theme
- **Background**: Dark Grey `(30, 30, 35)`
- **Panel Background**: Semi-transparent Black `(0, 0, 0, 200)`
- **Text Main**: White `(240, 240, 240)`
- **Text Dim**: Light Grey `(180, 180, 180)`
- **Highlight/Accent**: Neon Cyan `(0, 255, 255)` or Electric Green `(57, 255, 20)`
- **Warning/Error**: Neon Red `(255, 40, 40)`
- **Success**: Neon Green `(50, 255, 50)`
