# 健身骰子遊戲 - 弱雞轉換器 (Chicken Transformer)

**Fitness Dice Game powered by YOLOv8-Pose + TensorRT on Jetson Orin Nano**

一個基於姿態識別的即時健身互動遊戲，玩家透過攝像頭執行「舉手保持」動作擲骰子，系統隨機分配健身任務並實時驗證動作正確性。

## 特色功能

- 🎲 **體感擲骰子**: 透過「舉手保持」動作觸發任務抽取 (需保持 1 秒)
- 🏋️ **10+ 種健身動作**: 深蹲、伏地挺身、開合跳、波比跳等
- 🤖 **即時姿態檢測**: YOLOv8n-Pose + TensorRT FP16 加速（<50ms 推理）
- 📊 **進度追蹤**: 實時計數、組數管理、視覺反饋
- 🎮 **簡潔 UI**: PyGame 左右分割布局（70% 攝像頭 + 30% 資訊面板）
- ⚡ **高性能**: 維持 >20 FPS 流暢遊戲體驗 (待改進)

## 系統需求

### 開發環境 (WSL/Linux)
- Python 3.8-3.10
- uv 套件管理器
- USB 攝像頭

### 部署環境 (Jetson Orin Nano)
- JetPack 5.1.2+ (Ubuntu 20.04/22.04)
- CUDA 11.4+, TensorRT 8.5.2+
- CSI 或 USB 攝像頭
- 6GB/8GB RAM

## 快速開始

### 1. 克隆專案

```bash
git clone https://github.com/YOUR_USERNAME/chicken-transformer.git
cd chicken-transformer
```

### 2. 安裝依賴 (WSL/Linux)

```bash
# 安裝 uv 套件管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 創建虛擬環境
uv venv .venv
source .venv/bin/activate

# 安裝依賴
uv sync
```

### 3. 運行遊戲 (WSL/Linux - Mock 模式)

```bash
# 使用 Mock 檢測器（無需攝像頭）
uv run src/main.py --mode mock

# 使用 Mock 檢測器 + 隨機姿態
uv run src/main.py --mode mock --mock-pose random
```

### 4. 部署到 Jetson Orin Nano

詳細步驟請參考 [DEPLOYMENT.md](DEPLOYMENT.md)

```bash
# 1. 安裝系統依賴
sudo apt install python3-pycuda python3-opencv nvidia-tensorrt

# 2. 設置環境
uv venv .venv
source .venv/bin/activate
export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"
uv sync --extra jetson

# 3. 轉換模型 (需先有 ONNX)
# 注意：需先在開發機執行 scripts/export_model.py 產生 ONNX 並傳輸到 Jetson
/usr/src/tensorrt/bin/trtexec --onnx=assets/models/yolov8n-pose.onnx --saveEngine=assets/models/yolov8n-pose.engine --fp16 --memPoolSize=workspace:2048

# 4. 性能優化 (鎖定時脈)
sudo ./scripts/jetson_clocks.sh

# 5. 運行 (CSI 攝像頭)
# 提示：若無法顯示視窗，請檢查 DISPLAY 變數 (例如: export DISPLAY=:1)
export DISPLAY=:0
uv run src/main.py --mode tensorrt --camera csi

# 5. 運行 (USB 攝像頭)
# 若 CSI 攝像頭無法使用，可使用 USB 攝像頭
uv run src/main.py --mode tensorrt --camera usb
```

## 專案結構

```
chicken-transformer/
├── src/                    # 原始碼
│   ├── models/            # 姿態檢測器 (TensorRT/Mock)
│   ├── states/            # 遊戲狀態機
│   ├── tasks/             # 任務庫與驗證器
│   ├── ui/                # PyGame 介面
│   ├── camera/            # 攝像頭管理
│   └── utils/             # 工具函數
├── assets/                # 資源檔案
│   ├── models/           # TensorRT 引擎
│   └── tasks/            # 任務庫配置
├── config/               # 配置檔案
├── tests/                # 測試套件
└── specs/                # 規範文檔
```

## 開發指南

### 運行測試

```bash
pytest tests/ -v --cov=src
```

### 代碼格式化

```bash
black src/ tests/
ruff check . --fix
```

### 性能基準測試 (Jetson)

```bash
python scripts/benchmark_detector.py
```

### 開機自啟服務

```bash
# 安裝 systemd 服務
sudo cp scripts/fitness-game.service /etc/systemd/system/
sudo systemctl enable fitness-game.service
sudo systemctl start fitness-game.service
```

## 憲章原則

本專案遵循 [Constitution](`.specify/memory/constitution.md`) 的 6 項核心原則：

1. **Jetson 優化**: 針對 ARM64 + CUDA 架構優化
2. **即時性能**: >20 FPS, <50ms 推理, <100ms E2E
3. **狀態機架構**: Python 類別實作清晰的狀態轉換
4. **TensorRT 強制**: 無 CPU 後備，FP16 精度
5. **設備本地**: 完全離線運行
6. **UI 極簡**: <5ms 渲染開銷

## 文檔

- [功能規範](specs/001-fitness-dice-game/spec.md)
- [實作計劃](specs/001-fitness-dice-game/plan.md)
- [任務分解](specs/001-fitness-dice-game/tasks.md)
- [環境設置](specs/001-fitness-dice-game/quickstart.md)
- [資料模型](specs/001-fitness-dice-game/data-model.md)
- [接口契約](specs/001-fitness-dice-game/contracts/)

## 授權

MIT License

## 作者

Laurence - 基於 Speckit 工作流程開發
