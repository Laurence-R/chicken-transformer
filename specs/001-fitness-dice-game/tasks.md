# Tasks: 健身骰子遊戲 (Fitness Dice Game)

**Input**: Design documents from `/specs/001-fitness-dice-game/`
**Prerequisites**: ✅ plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Generated**: 2025-12-19  
**Branch**: `001-fitness-dice-game`

---

## Organization by User Story

Tasks are grouped by user story (P1, P2, P3) to enable:
- **Independent Implementation**: Each story can be developed separately
- **Independent Testing**: Each story has its own test criteria
- **Incremental Delivery**: MVP = User Story 1, then add P2, P3 progressively

---

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **Checkbox**: `- [ ]` (required for all tasks)
- **[ID]**: Task number (T001, T002, ...)
- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3) - ONLY for user story phase tasks
- **File path**: Exact file location in description

**Tests**: Not requested in specification - omitted from task list

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic directory structure

- [X] T001 Create project directory structure: src/{models,states,tasks,ui,camera,utils}/, assets/{models,tasks,fonts}/, tests/{unit,integration}/
- [X] T002 Initialize Python 3.10 virtual environment with uv venv .venv and install dependencies using uv sync (reads from pyproject.toml)
- [X] T003 [P] Create config/exercises.json with 10 exercise definitions (squat, pushup, jumping_jack, lunge, plank, situp, burpee, mountain_climber, high_knees, russian_twist)
- [X] T004 [P] Setup pytest configuration in pyproject.toml with coverage settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Data Structures

- [X] T005 [P] Create Keypoint dataclass in src/utils/data_structures.py with x, y, confidence, visible properties
- [X] T006 [P] Create BoundingBox dataclass in src/utils/data_structures.py with x1, y1, x2, y2, width, height
- [X] T007 [P] Create PoseData dataclass in src/utils/data_structures.py with keypoints[17], bbox, confidence, frame_id, timestamp, get_keypoint(), is_valid()
- [X] T008 [P] Define KEYPOINT_INDICES constant dict in src/utils/constants.py mapping 17 COCO keypoint names to indices

### Geometry & Validation Utilities

- [X] T009 [P] Implement calculate_angle(p1, p2, p3) function using NumPy in src/utils/geometry.py (returns degrees 0-180)
- [X] T010 [P] Implement is_angle_in_range(angle, target, tolerance) function in src/utils/geometry.py
- [X] T011 [P] Implement calculate_distance(p1, p2) function in src/utils/geometry.py (Euclidean distance)

### Abstract Base Classes (Contracts)

- [X] T012 Create PoseDetector ABC in src/models/pose_detector.py with initialize(), detect(), release(), get_input_size(), get_model_info() methods
- [X] T013 Create GameState ABC in src/states/game_state.py with name property, enter(), update(), exit(), get_display_message() methods
- [X] T014 Create StateTransition dataclass in src/states/game_state.py with next_state_name, context_updates
- [X] T015 Create ActionValidator ABC in src/tasks/validators/action_validator.py with exercise_name, validate(), get_required_keypoints(), can_validate()
- [X] T016 Create ValidationResult dataclass in src/tasks/validators/action_validator.py with is_valid, confidence, feedback, debug_info

### Mock Infrastructure (WSL Development)

- [X] T017 Implement MockPoseDetector in src/models/mock_detector.py with configurable modes (standing, squatting, jumping) and noise_level
- [X] T018 [P] Add command-line argument parsing in src/main.py to select --mode (mock|tensorrt) and --camera (csi|usb)

### Configuration & Logging

- [X] T019 [P] Create TaskLibrary class in src/tasks/task_library.py with load_from_json(), get_random_task(), get_exercise(), validate_library()
- [X] T020 [P] Create ExerciseDefinition dataclass in src/tasks/task_library.py with name_zh, name_en, validator_class, min/max reps/sets, difficulty
- [X] T021 [P] Setup Python logging configuration in src/utils/logger.py with console and file handlers

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 擲骰子獲取健身任務 (Priority: P1) 🎯 MVP

**Goal**: 玩家執行「跳躍+舉手」動作，系統識別後隨機分配健身任務並顯示

**Independent Test**: 
1. 啟動程式進入 WAITING 狀態
2. 在攝像頭前執行跳躍動作（Mock 模式模擬）
3. 2 秒內執行舉手動作
4. 系統應轉換到 TASK_DISPLAY 狀態並顯示隨機任務（例如「深蹲 15 次 x 2 組」）

### Core Entities for US1

- [X] T022 [P] [US1] Create WorkoutTask dataclass in src/tasks/workout_task.py with id, exercise_type, reps_per_set, total_sets, description, validator, created_at, to_display_string()
- [X] T023 [P] [US1] Create GameContext class in src/models/game_context.py with current_state, current_task, task_library, progress_tracker, ui, baseline_ankle_y, transition_to()

### State Machine for US1

- [X] T024 [P] [US1] Implement WaitingState in src/states/waiting_state.py with jump detection logic (_is_jumping checks ankle Y position)
- [X] T025 [P] [US1] Implement DiceRollDetectingState in src/states/dice_state.py with 2-second timeout and hands-raised detection (_is_hands_raised checks wrists above nose)
- [X] T026 [US1] Implement TaskDisplayState in src/states/task_display_state.py with 3-second display timer
- [X] T027 [US1] Integrate TaskLibrary.get_random_task() into DiceRollDetectingState to create WorkoutTask on successful detection

### PyGame UI for US1

- [X] T028 [P] [US1] Create GameWindow class in src/ui/game_window.py with 1280x720 resolution, 70/30 split layout, event loop, FPS control
- [X] T029 [P] [US1] Create CameraPanel class in src/ui/camera_panel.py to render left 70% area with frame display and skeleton overlay
- [X] T030 [P] [US1] Create InfoPanel class in src/ui/info_panel.py to render right 30% area with current state message, task description, FPS counter
- [X] T031 [US1] Integrate GameContext state transitions into GameWindow.update() main loop

### Camera Integration for US1

- [X] T032 [US1] Create CameraManager class in src/camera/camera_manager.py with OpenCV VideoCapture initialization, frame capture, FPS monitoring, error handling
- [X] T033 [US1] Connect CameraManager to MockPoseDetector in main loop: capture frame → detect pose → update GameContext

### Main Application for US1

- [X] T034 [US1] Implement main.py entry point with initialization sequence: parse args → create CameraManager → create MockPoseDetector → load TaskLibrary → create GameContext → start GameWindow loop
- [X] T035 [US1] Add graceful shutdown handling in main.py: Ctrl+C signal → release detector → close camera → destroy PyGame window

**Checkpoint**: User Story 1 完成 - 玩家可以擲骰子並看到隨機任務（Mock 模式）

---

## Phase 4: User Story 2 - 即時姿態檢測與任務進度追蹤 (Priority: P2)

**Goal**: 系統實時驗證玩家的健身動作是否正確，自動計數並更新進度顯示

**Independent Test**:
1. 手動設置 GameContext 為 TASK_EXECUTING 狀態，任務為「深蹲 5 次 x 1 組」
2. 在攝像頭前執行正確的深蹲動作（Mock 模式模擬 knee_angle=90°）
3. 系統應檢測到動作，計數增加到 1/5, 2/5, ..., 5/5
4. 完成後自動轉換到 COMPLETION 狀態

### Progress Tracking for US2

- [X] T036 [P] [US2] Create ProgressTracker class in src/tasks/progress_tracker.py with current_set, current_reps, total_sets, reps_per_set, increment_rep(), next_set(), get_progress_percentage(), get_display_text()

### Action Validators for US2 (10+ Exercises)

- [X] T037 [P] [US2] Implement SquatValidator in src/tasks/validators/squat_validator.py (knee angle 90°±17.5°, hip below knee)
- [X] T038 [P] [US2] Implement PushupValidator in src/tasks/validators/pushup_validator.py (elbow angle 85°±17.5°, nose near wrists)
- [X] T039 [P] [US2] Implement JumpingJackValidator in src/tasks/validators/jumping_jack_validator.py (hands above head, feet apart >1.5x shoulder width, state transition open↔closed)
- [X] T040 [P] [US2] Implement LungeValidator in src/tasks/validators/lunge_validator.py (front knee 90°, back knee near ground)
- [X] T041 [P] [US2] Implement PlankValidator in src/tasks/validators/plank_validator.py (shoulder-hip-ankle collinear, duration check)
- [X] T042 [P] [US2] Implement SitupValidator in src/tasks/validators/situp_validator.py (torso angle >60° from lying)
- [X] T043 [P] [US2] Implement BurpeeValidator in src/tasks/validators/burpee_validator.py (sequence: squat → jump → pushup → stand)
- [X] T044 [P] [US2] Implement MountainClimberValidator in src/tasks/validators/mountain_climber_validator.py (alternating knees to chest)
- [X] T045 [P] [US2] Implement HighKneesValidator in src/tasks/validators/high_knees_validator.py (knees above hips, alternating)
- [X] T046 [P] [US2] Implement RussianTwistValidator in src/tasks/validators/russian_twist_validator.py (torso rotation >30°, hands touch ground)

### State Machine Extension for US2

- [X] T047 [US2] Implement TaskExecutingState in src/states/task_executing_state.py with action validation loop, progress_tracker updates, and completion check
- [X] T048 [US2] Add validator instance creation logic in TaskLibrary based on validator_class name from exercises.json

### UI Enhancements for US2

- [X] T049 [US2] Extend InfoPanel to display progress bar with current_reps/reps_per_set and current_set/total_sets
- [X] T050 [US2] Add SkeletonRenderer class in src/ui/skeleton_renderer.py to draw 17 keypoints and skeleton lines on camera frame
- [X] T051 [US2] Add validation feedback display in InfoPanel (show ValidationResult.feedback message)

### Integration for US2

- [ ] T052 [US2] Connect TaskExecutingState.update() to call current_task.validate_rep(pose_data) and update ProgressTracker
- [X] T053 [US2] Add SkeletonRenderer to CameraPanel rendering pipeline to overlay keypoints on frame

**Checkpoint**: User Stories 1 AND 2 完成 - 玩家可以執行任務並看到實時計數（Mock 模式）

---

## Phase 5: User Story 3 - 完成驗證與遊戲循環 (Priority: P3)

**Goal**: 完成任務後顯示慶祝訊息，自動返回起始狀態，支持連續遊戲循環

**Independent Test**:
1. 手動設置 GameContext 為 TASK_EXECUTING 狀態，進度為最後一次動作（10/10, 2/2）
2. 執行一次正確動作觸發完成
3. 系統應轉換到 COMPLETION 狀態，顯示「任務完成！」訊息 3-5 秒
4. 自動返回 WAITING 狀態，清空任務數據

### State Machine Completion for US3

- [X] T054 [P] [US3] Implement CompletionState in src/states/completion_state.py with 3-second celebration display and auto-transition to WAITING
- [X] T055 [US3] Add completion animation rendering in InfoPanel (simple text animation or color flash)

### Game Loop & State Cleanup for US3

- [X] T056 [US3] Add state cleanup logic in GameContext.transition_to() to clear previous task data when entering WAITING
- [X] T057 [US3] Add continuous game loop support in main.py: allow repeated dice roll after completion without restart

### Edge Case Handling for US3

- [X] T058 [P] [US3] Add timeout detection in TaskExecutingState: if no valid action for 60 seconds, show "是否繼續任務？" prompt
- [ ] T059 [P] [US3] Add multi-person handling in PoseDetector: select skeleton with highest confidence or closest to center

**Checkpoint**: All user stories (P1-P3) 完成 - 完整遊戲循環可運行（Mock 模式）

---

## Phase 6: Jetson TensorRT Integration (Deployment)

**Purpose**: Replace Mock detector with TensorRT for Jetson Orin Nano deployment

**Prerequisites**: Jetson Orin Nano with JetPack 5.1.2+, TensorRT 8.5.2+, CUDA 11.4+

### Model Preparation

- [X] T060 Download YOLOv8n-pose.pt from Ultralytics releases to assets/models/ directory
- [X] T061 Create scripts/export_model.py to export YOLOv8n-pose.pt to ONNX format using ultralytics.YOLO.export()
- [X] T062 Run export script in WSL to generate assets/models/yolov8n-pose.onnx (architecture: input 640x640, output: 1x56x8400)
- [ ] T063 Transfer ONNX file to Jetson Orin Nano via scp or USB drive

### TensorRT Engine Conversion (Jetson Only)

- [ ] T064 Run trtexec on Jetson to convert ONNX to TensorRT engine: /usr/src/tensorrt/bin/trtexec --onnx=assets/models/yolov8n-pose.onnx --saveEngine=assets/models/yolov8n-pose.engine --fp16 --workspace=2048 --verbose
- [ ] T065 Verify engine file size (~50-100MB) and test loading with Python tensorrt bindings

### TensorRT Detector Implementation

- [X] T066 Implement TensorRTPoseDetector in src/models/tensorrt_detector.py with TensorRT engine loading, CUDA memory allocation, input preprocessing (BGR→RGB, resize 640x640, normalize)
- [X] T067 Implement inference method in TensorRTPoseDetector: copy input to GPU → execute TensorRT engine → parse output tensors → construct PoseData with 17 keypoints
- [X] T068 Add performance profiling in TensorRTPoseDetector to measure inference time and log if >50ms
- [X] T069 Implement resource cleanup in TensorRTPoseDetector.release() to free CUDA memory and TensorRT context

### GStreamer Camera Pipeline (Jetson CSI)

- [X] T070 Create GStreamerPipeline class in src/camera/gstreamer_pipeline.py with CSI pipeline string: nvarguscamerasrc → nvvidconv → BGRx → videoconvert → BGR → appsink
- [X] T071 Extend CameraManager to detect platform (aarch64 = Jetson) and use GStreamerPipeline for CSI camera initialization
- [X] T072 Add USB camera fallback in CameraManager if CSI initialization fails (use cv2.VideoCapture(0) with V4L2)

### Jetson Dependencies

- [ ] T073 Configure pyproject.toml with jetson dependency group for pygame, numpy, pillow (exclude opencv-python, tensorrt - installed via apt)
- [ ] T074 Update quickstart.md with Jetson installation steps: apt install python3-pycuda python3-opencv nvidia-tensorrt, set PYTHONPATH, then uv sync --group jetson

### Integration Testing (Jetson)

- [ ] T075 Run main.py with --mode tensorrt --camera csi on Jetson, verify FPS >20 and inference time <50ms
- [ ] T076 Create scripts/benchmark_detector.py to run 100 frames and report avg/p95/p99 inference times
- [ ] T077 Test all 10 validators with real camera input on Jetson, verify accuracy >90%

**Checkpoint**: Jetson TensorRT 整合完成 - 生產環境可運行（實機測試）

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Enhancements affecting multiple user stories

### Error Handling & Robustness

- [ ] T078 [P] Add camera disconnect detection in CameraManager with retry logic (3 attempts, 1 second interval)
- [ ] T079 [P] Add GPU out-of-memory handling in TensorRTPoseDetector with error message display
- [ ] T080 [P] Add low FPS warning in GameWindow: if FPS <10 for 5 seconds, show "性能低下，請檢查系統負載" alert

### Performance Optimization

- [ ] T081 Profile PyGame rendering with cProfile, optimize slow paths (target: <5ms per frame)
- [ ] T082 Add frame pre-conversion in CameraPanel to reduce BGR↔RGB conversion overhead (use pygame.image.frombuffer)
- [ ] T083 Enable Jetson clock locking in scripts/jetson_clocks.sh to maximize GPU/CPU frequency

### Documentation & Deployment

- [ ] T084 [P] Update README.md with quick start commands for WSL and Jetson
- [ ] T085 [P] Add architecture diagram to docs/ showing data flow: Camera → Detector → States → UI
- [ ] T086 [P] Create DEPLOYMENT.md with production checklist: engine file verification, camera tests, performance benchmarks
- [ ] T087 Run complete quickstart.md validation on fresh Jetson Orin Nano setup

### Code Quality

- [ ] T088 Run ruff linter and fix all errors: ruff check . --fix
- [ ] T089 Run black formatter: black src/ tests/
- [ ] T090 Add type hints to all public functions and verify with mypy (if requested)

**Checkpoint**: 生產就緒 - 所有功能完整，性能達標，文檔齊全

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
Phase 3 (US1) ───┐
    ↓            │
Phase 4 (US2) ───┤ ← Can proceed in parallel after Phase 2
    ↓            │
Phase 5 (US3) ───┘
    ↓
Phase 6 (Jetson TensorRT) ← Requires US1-US3 complete
    ↓
Phase 7 (Polish)
```

### User Story Dependencies

- **User Story 1 (P1)**: 
  - Depends on: Phase 2 (Foundational) complete
  - Independent from: US2, US3
  - Delivers: MVP - Dice roll and task display

- **User Story 2 (P2)**:
  - Depends on: Phase 2 (Foundational) complete
  - Builds on: US1 (uses WorkoutTask created by US1)
  - Independent test: Can manually trigger TASK_EXECUTING state
  - Delivers: Action validation and progress tracking

- **User Story 3 (P3)**:
  - Depends on: Phase 2 (Foundational) complete
  - Builds on: US2 (uses ProgressTracker.is_completed)
  - Independent test: Can manually trigger near-completion state
  - Delivers: Completion loop and state cleanup

### Within Each User Story

1. **Data Models** (can parallelize with [P])
2. **State Classes** (depends on data models)
3. **UI Components** (can parallelize with state classes if interfaces defined)
4. **Integration** (depends on all above)

### Parallel Opportunities Per Phase

- **Phase 1**: T003, T004 (parallel)
- **Phase 2**: 
  - T005-T008 (data structures, parallel)
  - T009-T011 (geometry utils, parallel)
  - T019-T020 (config classes, parallel)
- **Phase 3 (US1)**: T022-T023, T024-T026, T028-T030 (parallel within groups)
- **Phase 4 (US2)**: T037-T046 (all 10 validators, highly parallel)
- **Phase 5 (US3)**: T054-T055, T058-T059 (parallel)
- **Phase 6**: T073-T074 (docs, parallel)
- **Phase 7**: T078-T080, T084-T086 (parallel)

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

**MVP = User Story 1 (Phase 3)**
- Playable game loop: dice roll → task display → (manually restart)
- Mock detector for WSL development
- Basic UI with camera and info panels
- **Estimated Time**: 2-3 days (assuming 1 developer)

### Incremental Delivery

1. **Week 1**: Phase 1-2 (Setup + Foundation) + US1 (MVP)
2. **Week 2**: US2 (Action validation + 10 validators)
3. **Week 3**: US3 (Completion loop) + Phase 6 (Jetson TensorRT)
4. **Week 4**: Phase 7 (Polish) + Integration testing

### Parallel Development (if 2+ developers)

- **Developer A**: Focuses on state machine and UI (US1, US3)
- **Developer B**: Focuses on validators and pose detection (US2, Phase 6)
- **Sync Points**: After Phase 2, after US1, before Phase 7

---

## Summary Statistics

- **Total Tasks**: 90
- **Setup**: 4 tasks
- **Foundational**: 17 tasks (BLOCKING)
- **User Story 1 (P1 - MVP)**: 14 tasks
- **User Story 2 (P2)**: 18 tasks
- **User Story 3 (P3)**: 6 tasks
- **Jetson TensorRT**: 18 tasks
- **Polish**: 13 tasks

### Parallel Opportunities

- **Phase 2**: 10 tasks can run in parallel
- **Phase 4 (US2)**: 10 validators can be implemented simultaneously
- **Phase 7**: 6 documentation/testing tasks can parallelize

### MVP Scope Recommendation

**Minimum for first demo**: Phase 1-2 + User Story 1 (29 tasks)
- Delivers: Functional dice roll, random task assignment, basic UI
- Excludes: Action validation (use manual trigger for testing)

**Full MVP with core gameplay**: Add User Story 2 (47 tasks total)
- Delivers: Complete game loop with action validation
- Excludes: Automatic completion loop (manually restart for testing)

**Production-ready**: All 90 tasks
- Delivers: Full feature set with Jetson optimization

---

## Validation Checklist

Before marking feature complete:

- [ ] All 3 user stories independently testable
- [ ] Constitution Check re-verified (all 8 principles passing)
- [ ] Performance targets met: >20 FPS, <50ms inference, <100ms E2E
- [ ] 10+ validators implemented and tested
- [ ] Jetson TensorRT engine functional with <50ms inference
- [ ] Continuous game loop supports 3+ iterations without crash
- [ ] Documentation complete (README, quickstart, deployment guide)
- [ ] Code quality checks passed (ruff, black)

---

**Generated by**: `/speckit.tasks` command  
**Last Updated**: 2025-12-19  
**Ready for**: Phase 1 (Setup) implementation
