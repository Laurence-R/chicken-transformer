# Feature Specification: Enhance Game Experience

**Feature Branch**: `003-enhance-game-experience`
**Created**: 2025-12-20
**Status**: Draft
**Input**: User description: "我發現目前的專案使用上，仍存在一些問題：1. 使用上沒有抽獎的感覺。2. UI 介面並沒有到非常的好看。3. FPS 大約只有 7 fps 左右。請針對以上的問題進行修復。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Smooth Gameplay Performance (Priority: P1)

As a player, I want the game to run smoothly without lag so that my movements are tracked accurately and the experience feels responsive.

**Why this priority**: Currently, the game runs at ~7 FPS, which makes it difficult to play and causes motion sickness/frustration. 20+ FPS is required for real-time interaction.

**Independent Test**: Run the game on Jetson Orin Nano and measure the average FPS over a 60-second session.

**Acceptance Scenarios**:

1. **Given** the game is running on Jetson Orin Nano with TensorRT enabled, **When** the player performs actions, **Then** the frame rate stays consistently above 20 FPS.
2. **Given** the game is in the "Waiting" state, **When** no complex tasks are active, **Then** the idle FPS is optimized to save power/resources.

---

### User Story 2 - Lottery/Gacha Animation (Priority: P2)

As a player, I want to see an exciting animation when I trigger the dice roll so that I feel the anticipation of "drawing" a new workout task.

**Why this priority**: The current transition is too instant and lacks the "gamification" element of a dice game.

**Independent Test**: Trigger the dice roll gesture and observe the screen.

**Acceptance Scenarios**:

1. **Given** the player holds the "Hands Up" pose for 1 second, **When** the dice roll is triggered, **Then** a visual animation (e.g., rolling dice, shuffling cards, or flashing slots) plays for 1.5-3 seconds.
2. **Given** the animation is playing, **When** it finishes, **Then** the selected task is revealed with a visual "pop" or emphasis.

---

### User Story 3 - Modern UI Polish (Priority: P3)

As a player, I want a visually appealing interface with clear text and nice colors so that the game feels professional and fun.

**Why this priority**: The current UI is functional but "ugly" (basic colors, default fonts).

**Independent Test**: Launch the game and inspect the UI elements.

**Acceptance Scenarios**:

1. **Given** the game is running, **When** looking at the Info Panel, **Then** the background, text colors, and borders use a cohesive theme (e.g., Cyberpunk, Neon, or Clean Fitness).
2. **Given** Chinese text is displayed, **When** rendering, **Then** the font is crisp, readable, and correctly aligned (no overlapping or cut-off text).
3. **Given** the camera feed, **When** skeletons are drawn, **Then** the lines are smooth and colors are distinct from the background.

### Edge Cases

- **Asset Loading Failure**: If animation images/assets fail to load, the system MUST fallback to a simple text-based "Rolling..." indicator or a procedural shape animation.
- **Low Power Mode**: If the device is in a low-power state (throttling), the system SHOULD automatically reduce visual effects (e.g., disable complex skeleton smoothing) to maintain FPS.
- **Interruption**: If the user walks away during the "Rolling" animation, the game should continue to the "Task Display" state and wait for the user to return (timeout logic handled by existing Waiting state).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST achieve a minimum of 20 FPS during active gameplay on the target hardware (Jetson Orin Nano).
- **FR-002**: System MUST implement a "Rolling" state between "Dice Detection" and "Task Execution".
- **FR-003**: The "Rolling" state MUST display a dynamic animation (frames or procedural) that lasts between 1.5 to 3 seconds.
- **FR-004**: The UI MUST use a custom color palette (defined in constants) rather than hardcoded RGB values.
- **FR-005**: The UI MUST support rounded corners or styled borders for panels to improve aesthetics.
- **FR-006**: The Skeleton Renderer MUST be optimized to minimize drawing calls (e.g., batching lines/circles).
- **FR-007**: System MUST display a "Loading/Initializing" screen if model loading takes more than 2 seconds.

### Success Criteria

- **Performance**: Average FPS > 20 on Jetson Orin Nano (High Performance Mode).
- **Engagement**: "Rolling" animation successfully plays 100% of the time before a task starts.
- **Aesthetics**: UI passes a visual review (subjective: better than "basic PyGame rects").

### Assumptions

- The low FPS (7fps) is likely due to unoptimized rendering (drawing too many shapes per frame) or inefficient frame capture/conversion, rather than the model inference itself (which was benchmarked at <50ms).
- We have access to or can generate simple assets for the dice animation.
