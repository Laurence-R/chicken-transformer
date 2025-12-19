# Quick Start Guide: 健身骰子遊戲開發環境

**Date**: 2025-12-19  
**Purpose**: 快速建立 WSL 和 Jetson Orin Nano 開發環境

---

## 目錄

1. [開發策略](#開發策略)
2. [WSL 環境設置](#wsl-環境設置)
3. [Jetson Orin Nano 環境設置](#jetson-orin-nano-環境設置)
4. [專案初始化](#專案初始化)
5. [運行測試](#運行測試)
6. [常見問題](#常見問題)

---

## 開發策略

### 混合開發模式

```
WSL (x86_64)                    Jetson Orin Nano (ARM64)
├─ 邏輯開發                      ├─ TensorRT 整合
│  ├─ 狀態機實作                  │  ├─ YOLOv8-Pose 推論
│  ├─ 任務庫管理                  │  ├─ GStreamer 攝像頭
│  └─ 動作驗證器                  │  └─ 性能調優
├─ UI 開發                       └─ 最終整合測試
│  ├─ PyGame 介面
│  └─ Mock 姿態檢測器
└─ 單元測試
```

**切換時機**:
- WSL: 開發狀態機、UI、驗證邏輯（使用 Mock 數據）
- Jetson: TensorRT 模型部署、攝像頭整合、性能測試

---

## WSL 環境設置

### 1. 系統要求

- **OS**: WSL2 Ubuntu 22.04/24.04
- **Python**: 3.8 / 3.9 / 3.10（避免 3.12 語法）
- **記憶體**: 至少 4GB

### 2. 安裝 Python 3.10（如果 WSL 預設是 3.12）

```bash
# 檢查當前 Python 版本
python3 --version

# 如果是 3.12，安裝 3.10
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# 設置 Python 3.10 為預設
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
sudo update-alternatives --config python3  # 選擇 3.10
```

### 3. 安裝 uv 套件管理器

```bash
# 方法 1: 官方安裝腳本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 方法 2: pip 安裝（如果 curl 失敗）
pip install --user uv

# 驗證安裝
uv --version  # 應顯示 0.4.0+
```

### 4. 克隆專案並安裝依賴

```bash
# 克隆倉庫
git clone https://github.com/YOUR_USERNAME/chicken-transformer.git
cd chicken-transformer

# 創建虛擬環境（uv 會自動檢測 pyproject.toml 中的 Python 版本）
uv venv .venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝依賴（從 pyproject.toml 讀取，WSL 模式：無 TensorRT）
uv sync
```

### 5. 專案依賴管理

專案使用 `pyproject.toml` 管理依賴。主要依賴包括：

**核心依賴**:
- pygame >= 2.5.2
- opencv-python >= 4.8.1
- numpy >= 1.24.3
- pillow >= 10.1.0

**YOLOv8**（僅用於 ONNX 導出）:
- ultralytics >= 8.0.196

**開發工具**:
- pytest >= 7.4.3
- pytest-cov >= 4.1.0
- black >= 23.11.0
- ruff >= 0.1.6

### 6. 驗證安裝

```bash
# 測試 PyGame
python3 -c "import pygame; print(pygame.version.ver)"

# 測試 OpenCV
python3 -c "import cv2; print(cv2.__version__)"

# 測試 Mock 檢測器
python3 -m src.models.mock_detector
```

---

## Jetson Orin Nano 環境設置

### 1. 系統要求

- **JetPack**: 5.1.2+ (Ubuntu 20.04) 或 6.0+ (Ubuntu 22.04)
- **Python**: 3.8 (JetPack 5.x) 或 3.10 (JetPack 6.x)
- **CUDA**: 11.4+ (JetPack 5.x) 或 12.2+ (JetPack 6.x)
- **TensorRT**: 8.5.2+ (JetPack 5.x) 或 8.6+ (JetPack 6.x)

### 2. 檢查 JetPack 版本

```bash
# 檢查 JetPack 版本
sudo apt-cache show nvidia-jetpack | grep Version

# 檢查 TensorRT 版本
dpkg -l | grep tensorrt

# 檢查 CUDA 版本
nvcc --version
```

### 3. 安裝 uv（從源碼，ARM64 預編譯）

```bash
# 下載 ARM64 預編譯版本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip（如果 Rust 未安裝）
pip3 install --user uv

# 驗證
uv --version
```

### 4. 安裝 NVIDIA 專屬套件（不在 PyPI）

```bash
# 這些套件只能透過 apt 安裝（不在 requirements.txt）
sudo apt update
sudo apt install -y \
    python3-pycuda \
    python3-numpy \
    python3-opencv \
    libopencv-dev \
    nvidia-tensorrt

# 驗證 TensorRT Python 綁定
python3 -c "import tensorrt; print(tensorrt.__version__)"
```

### 5. 創建虛擬環境並安裝依賴

```bash
# 克隆專案
cd ~
git clone https://github.com/YOUR_USERNAME/chicken-transformer.git
cd chicken-transformer

# 創建虛擬環境（使用 uv，並繼承系統套件以訪問 TensorRT）
# 注意：uv 預設不支援 --system-site-packages，需使用 PYTHONPATH 變通
uv venv .venv

# 啟動虛擬環境
source .venv/bin/activate

# 設置 PYTHONPATH 以訪問系統安裝的 TensorRT 和 pycuda
export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"

# 安裝依賴（從 pyproject.toml，Jetson 專用配置組）
uv sync --extra jetson
```

### 6. Jetson 依賴管理

專案在 `pyproject.toml` 中定義 Jetson 專用依賴組：

**核心依賴**（透過 uv sync）:
- pygame >= 2.5.2
- numpy >= 1.24.3（與系統版本兼容）
- pillow >= 10.1.0
- pytest >= 7.4.3（開發工具）

**系統依賴**（透過 apt，不在 pyproject.toml）:
- pycuda（由 apt 安裝）
- tensorrt（由 apt 安裝）
- opencv-python（nvidia-jetson 定制版，由 apt 安裝）

**環境變數**:
```bash
# 添加到 ~/.bashrc 以持久化 TensorRT 訪問
echo 'export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"' >> ~/.bashrc
```

### 7. 轉換 YOLOv8-Pose 模型到 TensorRT

```bash
# 下載 YOLOv8n-Pose 預訓練模型（在 WSL 或 Jetson）
cd models/
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-pose.pt

# 導出為 ONNX（可在 WSL 完成）
python3 scripts/export_model.py --model yolov8n-pose.pt --format onnx

# 轉換為 TensorRT 引擎（必須在 Jetson 完成）
/usr/src/tensorrt/bin/trtexec \
    --onnx=models/yolov8n-pose.onnx \
    --saveEngine=models/yolov8n-pose.engine \
    --fp16 \
    --workspace=2048 \
    --verbose

# 驗證引擎
python3 scripts/test_tensorrt_engine.py
```

---

## 專案初始化

### 1. 目錄結構

```
chicken-transformer/
├── src/
│   ├── models/          # 姿態檢測器
│   │   ├── pose_detector.py       # 抽象接口
│   │   ├── tensorrt_detector.py   # Jetson 實現
│   │   └── mock_detector.py       # WSL Mock
│   ├── states/          # 遊戲狀態
│   │   ├── game_state.py          # 抽象基類
│   │   ├── waiting_state.py
│   │   ├── dice_roll_detecting.py
│   │   ├── task_display.py
│   │   ├── task_executing.py
│   │   └── completion_state.py
│   ├── tasks/           # 任務管理
│   │   ├── task_library.py
│   │   └── validators/
│   │       ├── action_validator.py  # 抽象基類
│   │       ├── squat_validator.py
│   │       ├── pushup_validator.py
│   │       └── jumping_jack_validator.py
│   ├── ui/              # PyGame UI
│   │   ├── camera_panel.py
│   │   ├── info_panel.py
│   │   └── skeleton_renderer.py
│   ├── camera/          # 攝像頭管理
│   │   └── camera_manager.py
│   └── utils/           # 工具函數
│       └── geometry.py  # 角度/距離計算
├── models/              # 模型檔案
│   ├── yolov8n-pose.pt
│   ├── yolov8n-pose.onnx
│   └── yolov8n-pose.engine
├── config/
│   └── exercises.json   # 任務庫配置
├── tests/
│   ├── test_states.py
│   ├── test_validators.py
│   └── test_detectors.py
├── scripts/
│   ├── export_model.py
│   └── test_tensorrt_engine.py
├── requirements-wsl.txt
├── requirements-jetson.txt
└── README.md
```

### 2. 創建配置文件 (`config/exercises.json`)

```json
{
  "exercises": [
    {
      "name_zh": "深蹲",
      "name_en": "squat",
      "validator_class": "SquatValidator",
      "min_reps": 5,
      "max_reps": 20,
      "min_sets": 1,
      "max_sets": 3,
      "difficulty": "medium"
    },
    {
      "name_zh": "伏地挺身",
      "name_en": "pushup",
      "validator_class": "PushupValidator",
      "min_reps": 5,
      "max_reps": 15,
      "min_sets": 1,
      "max_sets": 3,
      "difficulty": "hard"
    },
    {
      "name_zh": "開合跳",
      "name_en": "jumping_jack",
      "validator_class": "JumpingJackValidator",
      "min_reps": 10,
      "max_reps": 30,
      "min_sets": 1,
      "max_sets": 2,
      "difficulty": "easy"
    }
  ]
}
```

---

## 運行測試

### WSL 開發模式（Mock 檢測器）

```bash
# 啟動虛擬環境
source .venv/bin/activate

# 運行主程式（使用 Mock 檢測器）
python3 -m src.main --mode mock

# 運行單元測試
pytest tests/ -v --cov=src

# 運行特定測試
pytest tests/test_validators.py::test_squat_validator -v
```

### Jetson 生產模式（TensorRT 檢測器）

```bash
# 啟動虛擬環境
source .venv/bin/activate

# 確認 TensorRT 引擎存在
ls -lh models/yolov8n-pose.engine

# 運行主程式（使用 TensorRT 檢測器）
python3 -m src.main --mode tensorrt --camera csi

# 性能測試（100 幀）
python3 scripts/benchmark_detector.py --frames 100
```

### 檢查攝像頭

```bash
# Jetson: 列出可用攝像頭
v4l2-ctl --list-devices

# 測試 CSI 攝像頭（GStreamer）
gst-launch-1.0 nvarguscamerasrc ! nvvidconv ! autovideosink

# 測試 USB 攝像頭
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

---

## 常見問題

### Q1: WSL 中 `import pygame` 失敗

**問題**: `pygame.error: No available video device`

**解決方案**:
```bash
# 安裝 X11 轉發
sudo apt install -y x11-apps

# 在 Windows 安裝 VcXsrv 或 X410
# 啟動 X Server 並設置環境變量
export DISPLAY=:0
```

### Q2: Jetson 中 TensorRT 初始化失敗

**問題**: `ImportError: cannot import name 'tensorrt'`

**解決方案**:
```bash
# 確認 TensorRT 已安裝
dpkg -l | grep tensorrt

# 重新安裝 Python 綁定
sudo apt install --reinstall python3-tensorrt

# 檢查虛擬環境是否使用 --system-site-packages
python3 -c "import sys; print(sys.path)"
```

### Q3: YOLOv8 導出 ONNX 時記憶體不足

**問題**: `MemoryError` during export

**解決方案**:
```bash
# 在 WSL 導出（記憶體更充足）
python3 scripts/export_model.py --model yolov8n-pose.pt --format onnx

# 然後將 ONNX 複製到 Jetson
scp models/yolov8n-pose.onnx jetson@192.168.x.x:~/chicken-transformer/models/
```

### Q4: Jetson 推論速度慢（>100ms）

**診斷步驟**:
```bash
# 1. 確認使用 FP16
/usr/src/tensorrt/bin/trtexec \
    --loadEngine=models/yolov8n-pose.engine \
    --dumpProfile

# 2. 檢查 GPU 頻率
sudo jetson_clocks  # 鎖定最高頻率

# 3. 監控 GPU 使用率
tegrastats

# 4. 確認輸入解析度（640x640 vs 1920x1080）
```

### Q5: 攝像頭 FPS 低於 20

**調整 GStreamer 管線**:
```python
# 在 camera_manager.py 中調整
CSI_PIPELINE = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM), width=640, height=480, framerate=30/1 ! "  # 降低解析度
    "nvvidconv ! video/x-raw, format=BGRx ! "
    "videoconvert ! video/x-raw, format=BGR ! appsink"
)
```

---

## 效能目標

| 指標 | WSL Mock | Jetson TensorRT |
|------|----------|----------------|
| 姿態檢測 | <10ms | <40ms |
| 動作驗證 | <5ms | <5ms |
| UI 渲染 | <5ms | <5ms |
| 總幀時間 | <20ms (50 FPS) | <50ms (20 FPS) |

---

## 下一步

1. ✅ 環境設置完成
2. ⏳ 開始實作核心模組（從狀態機開始）
3. ⏳ 撰寫單元測試
4. ⏳ 整合 TensorRT 檢測器（Jetson）
5. ⏳ 調優性能（FPS >20）

---

**更新日期**: 2025-12-19  
**文件版本**: 1.0
