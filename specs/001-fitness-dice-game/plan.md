# Implementation Plan: 健身骰子遊戲 (Fitness Dice Game)

**Branch**: `001-fitness-dice-game` | **Date**: 2025-12-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-fitness-dice-game/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

開發一個即時健身遊戲「弱雞轉換器」，玩家透過姿態識別與遊戲互動。核心流程：玩家執行跳躍+舉手動作擲骰子 → 系統隨機分配健身任務（10+ 種動作，次數 5-20，組數 1-3）→ YOLOv8n-Pose TensorRT 推理驗證動作正確性 → 實時計數並更新 PyGame UI → 完成後返回起始狀態。技術重點：Python 3.8+ 狀態機架構，TensorRT FP16 優化達 30-40 FPS 目標，OpenCV 攝像頭捕獲，左右分割布局（70% 攝像頭 + 30% 資訊面板），寬鬆驗證容忍度（±15-20°）確保遊戲友好性。

## Technical Context

**Language/Version**: Python 3.8-3.10 (JetPack 5.x 相容範圍)  
**Primary Dependencies**: 
- YOLOv8 (Ultralytics) + TensorRT 8.5+ (FP16 推理)
- PyGame 2.x (UI 框架)
- OpenCV 4.x (cv2，攝像頭捕獲，支援 CSI/USB)
- NumPy 1.x (骨架數據計算)
- uv (套件管理工具)

**Storage**: 
- 本地 JSON 檔案（任務庫配置，~10KB）
- TensorRT 引擎序列化檔案（~50-100MB）
- 無數據庫需求

**Testing**: 
- pytest (WSL 環境單元測試)
- Mock 姿態數據用於狀態機和驗證邏輯測試
- 端到端集成測試在 Jetson Orin Nano 實機進行

**Target Platform**: 
- **開發環境**: WSL2/Ubuntu 24.04, x86_64 (大部分邏輯開發和單元測試)
- **部署目標**: Jetson Orin Nano 6GB/8GB, ARM64, JetPack 5.x, Ubuntu 20.04/22.04

**Project Type**: Single embedded application (非 web/mobile)

**Performance Goals**: 
- 攝像頭捕獲和處理：>20 FPS 持續（無掉幀）
- YOLOv8n-Pose TensorRT 推理：<50ms/frame (640x640 輸入, FP16)
- PyGame UI 渲染：<5ms/frame
- 端到端延遲：<100ms (capture → inference → UI update)
- 啟動時間：<10 秒（包含 TensorRT 引擎加載）

**Constraints**: 
- 記憶體：應用總記憶體 <4GB，GPU 記憶體 <6GB（Jetson Orin Nano 8GB 限制）
- 完全離線運行，無雲端 API 依賴
- 單人遊戲場景（多人檢測僅選最大/中心骨架）
- CSI 或 USB 攝像頭，解析度 640x480 或 1280x720

**Scale/Scope**: 
- 10+ 種健身動作驗證規則
- 5 個遊戲狀態轉換
- 單次遊戲時長 5-30 分鐘
- 支援連續遊戲循環（3+ 次無崩潰）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 0 檢查（研究前）

- [x] **Jetson Optimization**: ✅ 是，核心功能依賴 GPU/CUDA。YOLOv8n-Pose 需 TensorRT 加速，已明確 FP16 精度和目標性能（30-40 FPS）
- [x] **Performance Standards**: ✅ 明確定義：>20 FPS 攝像頭，<50ms 推理，<100ms 端到端延遲，符合憲章 Principle II
- [x] **State Machine**: ✅ 已設計 5 個遊戲狀態（WAITING, DICE_ROLL_DETECTING, TASK_DISPLAY, TASK_EXECUTING, COMPLETION），將使用 Python 類別和 State Pattern 實作
- [x] **TensorRT Mandatory**: ✅ YOLOv8n-Pose 必須轉換為 TensorRT 引擎，無 CPU 推理後備方案，符合憲章 Principle IV
- [x] **On-Device Only**: ✅ 完全離線，無雲端 API，模型和任務庫皆本地存取，符合憲章 Principle V
- [x] **UI Minimalism**: ✅ PyGame 簡潔布局（左右分割），目標渲染 <5ms/frame，符合憲章 Principle VI
- [x] **Resource Budget**: ✅ 已估算：總記憶體 <4GB，GPU <6GB，符合 Jetson Orin Nano 8GB 限制
- [x] **Hardware Compatibility**: ✅ Python 3.8-3.10、JetPack 5.x、CUDA 11.4+、TensorRT 8.5+ 已確認

**Phase 0 結果**: ✅ **所有憲章檢查通過** - 無違規項目，已完成 Phase 0 研究

---

### Phase 1 檢查（設計後）

*Re-evaluation after data-model.md, contracts/, and quickstart.md generation*

- [x] **Jetson Optimization**: ✅ **強化驗證**
  - TensorRT 轉換流程已確認：ONNX → trtexec FP16 → Python inference wrapper
  - 目標推理時間 30-40ms/frame（640x640 輸入）已明確記錄於 [research.md](research.md)
  - GStreamer 硬體加速攝像頭管線已定義（CSI 優先，USB 備用）
  
- [x] **Performance Standards**: ✅ **設計階段驗證**
  - 已定義 PoseDetector 接口性能約定：TensorRT <50ms, Mock <10ms
  - GameState.update() 執行時間 <10ms 保證已寫入 [game-state.md](contracts/game-state.md)
  - ActionValidator.validate() 執行時間 <5ms 保證已寫入 [action-validator.md](contracts/action-validator.md)
  - 總端到端延遲預算分配：檢測 40ms + 驗證 5ms + 渲染 5ms = 50ms (20 FPS)
  
- [x] **State Machine**: ✅ **完整設計**
  - 5 個具體狀態類已設計（WaitingState, DiceRollDetectingState, TaskDisplayState, TaskExecutingState, CompletionState）
  - 狀態轉換圖和條件已記錄於 [game-state.md](contracts/game-state.md)
  - GameContext 數據模型已定義於 [data-model.md](data-model.md)
  
- [x] **TensorRT Mandatory**: ✅ **架構強制**
  - TensorRTPoseDetector 為 Jetson 唯一實現（無 CPU 後備）
  - MockPoseDetector 僅用於 WSL 開發，不部署到 Jetson
  - 引擎檔案路徑和初始化邏輯已記錄於 [pose-detector.md](contracts/pose-detector.md)
  
- [x] **On-Device Only**: ✅ **設計確認**
  - 所有接口無網路調用（PoseDetector, GameState, ActionValidator）
  - TaskLibrary 從本地 JSON 載入（config/exercises.json）
  - TensorRT 引擎本地存取（models/yolov8n-pose.engine）
  
- [x] **UI Minimalism**: ✅ **接口約束**
  - GameState.get_display_message() 僅返回字串，不涉及渲染邏輯
  - ValidationResult.feedback 為純文字反饋
  - PyGame 優化策略已記錄（pre-rendering, hardware surfaces）於 [research.md](research.md)
  
- [x] **Resource Budget**: ✅ **實現細節確認**
  - YOLOv8n-Pose 模型大小 ~6MB (參數 ~3M)
  - TensorRT 引擎預估 ~50-100MB（FP16 精度）
  - PyGame 表面和字體緩存預估 <100MB
  - 總 GPU 記憶體預算：TensorRT 引擎 100MB + 推理緩衝 ~200MB + 攝像頭緩衝 ~50MB = ~350MB << 6GB 限制
  
- [x] **Hardware Compatibility**: ✅ **環境配置驗證**
  - [quickstart.md](quickstart.md) 已明確 JetPack 5.1.2+, Python 3.8-3.10, CUDA 11.4+, TensorRT 8.5.2+ 要求
  - WSL 和 Jetson 的 uv 安裝指令已驗證（ARM64 支援）
  - 混合開發策略已記錄（WSL 邏輯開發 + Jetson TensorRT 整合）

**Phase 1 結果**: ✅ **所有憲章檢查再次通過** - 設計階段無違規，接口和約定符合所有原則

*Phase 2 (tasks.md 生成) 將由 `/speckit.tasks` 命令處理*

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
chicken-transformer/
├── src/
│   ├── models/              # YOLOv8-Pose 推理模組
│   │   ├── pose_detector.py       # 抽象接口定義
│   │   ├── tensorrt_detector.py   # TensorRT 實作（Jetson）
│   │   └── mock_detector.py       # Mock 實作（WSL 開發）
│   │
│   ├── states/              # 狀態機實作
│   │   ├── game_state.py          # State Pattern 基類和上下文
│   │   ├── waiting_state.py       # 等待開始狀態
│   │   ├── dice_roll_state.py     # 擲骰子動作檢測
│   │   ├── task_display_state.py  # 任務展示
│   │   ├── task_executing_state.py # 任務執行中
│   │   └── completion_state.py     # 完成驗證
│   │
│   ├── tasks/               # 任務定義和驗證邏輯
│   │   ├── task_library.py        # 任務庫載入器（JSON）
│   │   ├── workout_task.py        # WorkoutTask 資料類
│   │   ├── validators/            # 動作驗證器
│   │   │   ├── base_validator.py  # 驗證器抽象類
│   │   │   ├── squat_validator.py # 深蹲
│   │   │   ├── pushup_validator.py # 伏地挺身
│   │   │   └── ... (10+ 驗證器)
│   │   └── progress_tracker.py    # 進度追蹤器
│   │
│   ├── ui/                  # PyGame 介面
│   │   ├── game_window.py         # 主視窗和事件循環
│   │   ├── camera_panel.py        # 左側攝像頭顯示區域
│   │   ├── info_panel.py          # 右側資訊面板
│   │   ├── skeleton_renderer.py   # 骨架標記繪製
│   │   └── fps_monitor.py         # FPS 和延遲監控
│   │
│   ├── camera/              # 攝像頭管理
│   │   ├── camera_manager.py      # 攝像頭初始化和捕獲
│   │   └── gstreamer_pipeline.py  # GStreamer 管道（Jetson CSI）
│   │
│   ├── utils/               # 工具函數
│   │   ├── pose_utils.py          # 骨架關鍵點計算（角度、距離）
│   │   ├── config.py              # 配置載入
│   │   └── logger.py              # 日誌工具
│   │
│   └── main.py              # 應用程式入口
│
├── assets/                  # 資源檔案
│   ├── models/                    # TensorRT 引擎和 ONNX
│   │   ├── yolov8n-pose.onnx
│   │   └── yolov8n-pose.engine (Jetson 生成)
│   ├── tasks/                     # 任務庫配置
│   │   └── workout_library.json
│   └── fonts/                     # UI 字型（可選）
│
├── tests/                   # 測試套件
│   ├── unit/                      # 單元測試（WSL）
│   │   ├── test_states.py
│   │   ├── test_validators.py
│   │   ├── test_task_library.py
│   │   └── test_pose_utils.py
│   ├── integration/               # 集成測試（Jetson）
│   │   ├── test_camera_pipeline.py
│   │   ├── test_tensorrt_inference.py
│   │   └── test_end_to_end.py
│   └── fixtures/                  # Mock 數據
│       └── sample_poses.json
│
├── scripts/                 # 輔助腳本
│   ├── convert_to_tensorrt.py    # ONNX → TensorRT 轉換
│   ├── setup_jetson.sh           # Jetson 環境設置
│   └── benchmark.py              # 性能基準測試
│
├── pyproject.toml           # uv 專案配置
├── requirements.txt         # 依賴清單（uv 生成）
├── README.md                # 專案說明和快速開始
└── .gitignore
```

**Structure Decision**: 採用單一專案結構（Option 1）因為這是嵌入式應用，無前後端分離需求。目錄按功能模組化（models, states, tasks, ui, camera），支援 WSL Mock 開發（`mock_detector.py`）和 Jetson 部署（`tensorrt_detector.py`）的雙環境策略。`assets/` 存放模型和配置，`tests/` 區分單元測試（WSL）和集成測試（Jetson）。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**無違規項目** - 所有憲章檢查已通過，無需複雜度追蹤或例外說明。
