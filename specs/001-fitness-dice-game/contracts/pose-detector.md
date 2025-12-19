# Contract: PoseDetector

**Date**: 2025-12-19  
**Type**: Abstract Base Class (ABC)  
**Purpose**: 定義姿態檢測器的統一接口，支持 TensorRT (Jetson) 和 Mock (WSL) 實現

---

## 接口定義

```python
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

class PoseDetector(ABC):
    """姿態檢測器抽象基類"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化檢測器（載入模型、分配資源）
        
        Returns:
            bool: 初始化成功返回 True，失敗返回 False
            
        Raises:
            RuntimeError: 如果無法載入模型或 TensorRT 引擎初始化失敗
        """
        pass
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> Optional[PoseData]:
        """
        對單幀圖像進行姿態檢測
        
        Args:
            frame: BGR 格式圖像 (H x W x 3), dtype=uint8
            
        Returns:
            PoseData: 檢測結果，包含 17 個關鍵點和置信度
            None: 如果未檢測到人體或處理失敗
            
        Requirements:
            - 處理時間 <50ms (Jetson TensorRT 實現)
            - 處理時間 <10ms (WSL Mock 實現)
            - 返回 COCO 格式的 17 個關鍵點
            - 置信度 <0.3 的關鍵點標記為不可見
        """
        pass
    
    @abstractmethod
    def release(self) -> None:
        """
        釋放檢測器資源（CUDA 記憶體、TensorRT 上下文）
        
        Requirements:
            - 必須在程序結束前調用
            - 冪等性：多次調用不會出錯
        """
        pass
    
    @abstractmethod
    def get_input_size(self) -> tuple[int, int]:
        """
        返回模型輸入尺寸
        
        Returns:
            (width, height): 例如 (640, 640)
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """
        返回模型元資訊
        
        Returns:
            dict: 包含以下鍵值
                - "model_name": str (例如 "yolov8n-pose")
                - "backend": str ("tensorrt" | "mock")
                - "precision": str ("fp16" | "fp32" | "none")
                - "avg_inference_time_ms": float
        """
        pass
```

---

## 約定 (Contracts)

### 前置條件 (Preconditions)

1. **初始化必須先調用**: 在調用 `detect()` 前必須先成功調用 `initialize()`
2. **輸入格式**: `detect()` 接收的 `frame` 必須是:
   - NumPy 數組 (H x W x 3)
   - BGR 色彩空間
   - dtype=uint8
   - H, W 可為任意尺寸（內部會自動縮放到模型輸入尺寸）

### 後置條件 (Postconditions)

1. **PoseData 有效性**: 
   - 若返回非 None，則 `PoseData.is_valid()` 必須為 True
   - 至少 8 個關鍵點的 confidence >0.5
   
2. **性能保證**:
   - TensorRT 實現: `detect()` 執行時間 <50ms (95th percentile)
   - Mock 實現: `detect()` 執行時間 <10ms
   
3. **資源管理**:
   - `release()` 後不可再調用 `detect()`
   - `initialize()` 可重複調用（自動釋放舊資源）

### 不變量 (Invariants)

1. **關鍵點數量**: 返回的 `PoseData.keypoints` 長度始終為 17
2. **座標範圍**: 關鍵點座標在原始 frame 座標系內（非歸一化）
3. **線程安全**: 單個實例不保證線程安全，多線程需使用鎖

---

## 具體實現類

### TensorRTPoseDetector (Jetson)

**額外約定**:
- 首次調用 `initialize()` 需 3-10 秒（載入 TensorRT 引擎）
- 後續熱啟動 <1 秒
- 需要 CUDA 可用（`torch.cuda.is_available() == True`）
- 引擎檔案路徑: `models/yolov8n-pose.engine`

**錯誤處理**:
```python
if not torch.cuda.is_available():
    raise RuntimeError("CUDA 不可用，無法初始化 TensorRT 檢測器")
    
if not os.path.exists("models/yolov8n-pose.engine"):
    raise FileNotFoundError("TensorRT 引擎檔案不存在")
```

### MockPoseDetector (WSL)

**額外約定**:
- 返回預定義的姿態序列（用於測試）
- 可配置返回模式：`"standing"`, `"squatting"`, `"jumping"`
- `initialize()` 立即返回 True（無資源載入）

**構造參數**:
```python
def __init__(self, mode: str = "standing", noise_level: float = 0.0):
    """
    Args:
        mode: 預定義姿態模式
        noise_level: 關鍵點座標噪音範圍 (0.0 ~ 1.0)
    """
```

---

## 使用範例

### 正常流程

```python
# 創建檢測器（根據平台選擇）
if platform.machine() == "aarch64":  # Jetson
    detector = TensorRTPoseDetector(engine_path="models/yolov8n-pose.engine")
else:  # WSL 開發環境
    detector = MockPoseDetector(mode="standing")

# 初始化
if not detector.initialize():
    raise RuntimeError("檢測器初始化失敗")

# 主循環
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 檢測
    pose_data = detector.detect(frame)
    
    if pose_data and pose_data.is_valid():
        # 處理姿態數據
        print(f"檢測到人體，置信度: {pose_data.confidence:.2f}")
    else:
        print("未檢測到有效姿態")

# 清理
detector.release()
cap.release()
```

### 錯誤處理範例

```python
try:
    detector = TensorRTPoseDetector()
    detector.initialize()
except FileNotFoundError as e:
    print(f"模型檔案缺失: {e}")
    # Fallback to mock
    detector = MockPoseDetector()
except RuntimeError as e:
    print(f"CUDA 不可用: {e}")
    sys.exit(1)
```

---

## 測試要求

### 單元測試覆蓋

1. **初始化測試**:
   - 重複初始化不崩潰
   - 無效路徑拋出正確異常
   
2. **檢測測試**:
   - 空白圖像返回 None
   - 有效人體圖像返回 PoseData
   - 性能測試（100 幀平均時間）
   
3. **資源釋放測試**:
   - 釋放後調用 detect() 拋出異常
   - 記憶體洩漏檢測

### Mock 實現測試

```python
def test_mock_detector_returns_valid_pose():
    detector = MockPoseDetector(mode="standing")
    detector.initialize()
    
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    pose_data = detector.detect(dummy_frame)
    
    assert pose_data is not None
    assert len(pose_data.keypoints) == 17
    assert pose_data.is_valid()
    
    detector.release()
```

---

## 憲章符合性

| 原則 | 符合狀態 |
|------|---------|
| Jetson 優化 | ✅ TensorRT FP16 專用實現 |
| 即時性能 | ✅ <50ms 檢測時間保證 |
| 狀態機 | ✅ 作為 GameState 輸入 |
| TensorRT 強制 | ✅ Jetson 必須使用 TensorRT |
| 設備本地 | ✅ 無網路調用 |
| 最小 UI | ✅ 僅提供數據，不涉及渲染 |

---

## 相關文件

- [data-model.md](../data-model.md) - PoseData 結構定義
- [research.md](../research.md) - TensorRT 轉換流程
- [game-state.md](./game-state.md) - 狀態機接口
