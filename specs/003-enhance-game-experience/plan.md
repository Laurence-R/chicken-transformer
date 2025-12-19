# Implementation Plan - Enhance Game Experience

**Feature**: Enhance Game Experience (UI Polish, Lottery Animation, FPS Optimization)
**Branch**: `003-enhance-game-experience`
**Spec**: [specs/003-enhance-game-experience/spec.md](spec.md)

## Technical Context

The current application suffers from low FPS (~7 FPS) and a lackluster user experience. Analysis reveals:

1.  **Performance Bottlenecks**:
    - `InfoPanel.update` calls `font.render` every frame for all text, which is extremely CPU-intensive.
    - `CameraPanel.update` performs inefficient image conversion and scaling using PyGame software routines instead of OpenCV's optimized C++ routines.
    - `GameWindow` redraws the entire screen every frame without dirty rect optimization (though full redraw might be necessary for camera feed, the info panel doesn't need it).

2.  **UI/UX Deficiencies**:
    - Visuals are "programmer art" with hardcoded RGB values.
    - No visual feedback for the "dice roll" event; it transitions instantly.
    - Text rendering is unoptimized and lacks style.

3.  **Architecture**:
    - The State Machine is robust, allowing easy insertion of a new `RollingState`.
    - `GameContext` holds the state, which is good.

## Constitution Check

- [x] **Jetson Optimization**: Optimizing the rendering loop is critical for the ARM64 CPU to keep up with the GPU inference.
- [x] **Real-Time Performance**: Targeting >20 FPS by reducing render time from >100ms to <5ms.
- [x] **Class-Based State Machine**: Implementing `RollingState` as a proper class.
- [x] **Minimal PyGame Interface**: Reducing overhead of PyGame calls.

## Gates & Checks

- [ ] **Gate 1**: FPS > 20 on Jetson (verified via `main.py` output).
- [ ] **Gate 2**: "Rolling" animation plays smoothly without blocking the main loop.
- [ ] **Gate 3**: UI looks consistent (colors, fonts) and supports Chinese characters.

## Phase 0: Research & Prototyping

*Goal: Validate optimization techniques and design the animation.*

- [ ] **Research Task 1**: Benchmark `cv2.resize/cvtColor` vs `pygame.transform/image` on Jetson (or assume cv2 is faster based on common knowledge). *Decision: Use OpenCV for heavy lifting.*
- [ ] **Research Task 2**: Design the "Rolling" animation. Since we want to avoid external assets, we will use a "Slot Machine" style text effect where numbers/icons cycle rapidly.

## Phase 1: Core Optimization (FPS Boost)

*Goal: Fix the low FPS issue first to make development smoother.*

- [ ] **Refactor `CameraPanel`**:
    - Use `cv2.resize` to scale frame to panel size *before* creating PyGame surface.
    - Use `cv2.cvtColor` for BGR->RGB conversion.
    - Ensure `pygame.image.frombuffer` is used correctly.
- [ ] **Refactor `InfoPanel`**:
    - Implement a caching mechanism for rendered text surfaces.
    - Only re-render text when the content changes (e.g., `fps` changes, `state` changes).
    - Use a `dirty` flag to control blitting.

## Phase 2: UI Polish & Theming

*Goal: Make the game look professional.*

- [ ] **Create `src/ui/theme.py`**:
    - Define a `Theme` class with color palettes (Background, Text, Highlight, Success, Error).
    - Define font configurations.
- [ ] **Update `InfoPanel`**:
    - Use `Theme` colors.
    - Draw rounded rectangles for sections.
    - Improve layout (padding, alignment).
- [ ] **Update `SkeletonRenderer`**:
    - Use `Theme` colors for joints and connections.
    - Optimize drawing (reduce number of calls if possible).

## Phase 3: Lottery Animation (Game Feel)

*Goal: Add the "Gacha" excitement.*

- [ ] **Create `src/states/rolling_state.py`**:
    - Inherit from `GameState`.
    - Implement `update` to cycle through random tasks/icons for 2-3 seconds.
    - Store the final result in `GameContext`.
- [ ] **Update `DiceRollDetectingState`**:
    - Transition to `ROLLING` instead of `TASK_DISPLAY`.
- [ ] **Update `GameManager`**:
    - Register the new state.
- [ ] **Update `InfoPanel`**:
    - Handle the `ROLLING` state to display the animation (large changing text).

## Phase 4: Validation

- [ ] **Test**: Run on Jetson and check FPS counter.
- [ ] **Test**: Trigger dice roll and verify animation.
- [ ] **Test**: Verify Chinese text display.
