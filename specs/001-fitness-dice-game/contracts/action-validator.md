# Contract: ActionValidator

**Date**: 2025-12-19  
**Type**: Abstract Base Class (ABC)  
**Purpose**: 定義健身動作驗證器的統一接口，實現策略模式

---

## 接口定義

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class ValidationResult:
    """驗證結果"""
    is_valid: bool              # 動作是否有效
    confidence: float           # 驗證置信度 (0.0 ~ 1.0)
    feedback: str               # 錯誤提示或鼓勵訊息
    debug_info: Optional[dict]  # 調試資訊（角度、距離等）

class ActionValidator(ABC):
    """動作驗證器抽象基類"""
    
    def __init__(self, 
                 tolerance_angle_degrees: float = 17.5,
                 tolerance_distance_ratio: float = 0.10,
                 min_confidence_threshold: float = 0.5):
        """
        Args:
            tolerance_angle_degrees: 角度容忍度（度）
            tolerance_distance_ratio: 距離容忍度比例
            min_confidence_threshold: 關鍵點最小置信度閾值
        """
        self.tolerance_angle = tolerance_angle_degrees
        self.tolerance_distance = tolerance_distance_ratio
        self.min_confidence = min_confidence_threshold
    
    @property
    @abstractmethod
    def exercise_name(self) -> str:
        """
        動作名稱（繁體中文）
        
        Returns:
            str: 例如 "深蹲", "伏地挺身"
        """
        pass
    
    @abstractmethod
    def validate(self, pose_data: PoseData) -> ValidationResult:
        """
        驗證單次動作是否正確
        
        Args:
            pose_data: 當前幀的姿態數據
            
        Returns:
            ValidationResult: 包含是否有效、置信度和反饋訊息
            
        Requirements:
            - 執行時間 <5ms（避免阻塞主循環）
            - 關鍵點置信度 <min_confidence_threshold 視為無效
            - 必須提供具體反饋訊息（不能只返回 True/False）
            
        Example:
            result = validator.validate(pose_data)
            if result.is_valid:
                print(f"✓ {result.feedback}")
            else:
                print(f"✗ {result.feedback}")
        """
        pass
    
    @abstractmethod
    def get_required_keypoints(self) -> list[str]:
        """
        返回驗證所需的關鍵點名稱列表
        
        Returns:
            list[str]: 例如 ["left_hip", "left_knee", "left_ankle"]
            
        Purpose:
            - 用於檢查 PoseData 是否包含足夠的可見關鍵點
            - 在驗證前進行快速失敗檢查
        """
        pass
    
    def can_validate(self, pose_data: PoseData) -> bool:
        """
        檢查 PoseData 是否包含足夠的關鍵點進行驗證
        
        Args:
            pose_data: 當前幀的姿態數據
            
        Returns:
            bool: True 表示可以進行驗證
            
        Note:
            此方法有默認實現，子類通常不需要覆寫
        """
        required = self.get_required_keypoints()
        for kp_name in required:
            kp = pose_data.get_keypoint(kp_name)
            if not kp.visible or kp.confidence < self.min_confidence:
                return False
        return True
```

---

## 約定 (Contracts)

### 前置條件 (Preconditions)

1. **PoseData 有效性**: 調用 `validate()` 前應先確認 `pose_data.is_valid()` 為 True
2. **關鍵點可見性**: 建議先調用 `can_validate()` 檢查必需關鍵點是否可見
3. **座標系一致**: PoseData 的關鍵點座標必須在像素座標系（非歸一化）

### 後置條件 (Postconditions)

1. **結果一致性**: 
   - `ValidationResult.is_valid == True` 時，`confidence` 應 ≥0.7
   - `feedback` 必須是非空字串（繁體中文）
   
2. **性能保證**:
   - `validate()` 執行時間 <5ms (99th percentile)
   - `can_validate()` 執行時間 <1ms
   
3. **冪等性**:
   - 對同一 `pose_data` 重複調用 `validate()` 返回相同結果

### 不變量 (Invariants)

1. **容忍度範圍**: 
   - `tolerance_angle_degrees` ∈ [5°, 30°]
   - `tolerance_distance_ratio` ∈ [0.05, 0.20]
2. **置信度範圍**: `ValidationResult.confidence` ∈ [0.0, 1.0]

---

## 具體實現類

### 1. SquatValidator (深蹲驗證器)

```python
class SquatValidator(ActionValidator):
    @property
    def exercise_name(self) -> str:
        return "深蹲"
    
    def get_required_keypoints(self) -> list[str]:
        return ["left_hip", "left_knee", "left_ankle", 
                "right_hip", "right_knee", "right_ankle",
                "left_shoulder", "right_shoulder"]
    
    def validate(self, pose_data: PoseData) -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                feedback="關鍵點不可見，請站在攝像頭前方",
                debug_info=None
            )
        
        # 計算左右膝蓋角度
        left_angle = calculate_angle(
            pose_data.get_keypoint('left_hip'),
            pose_data.get_keypoint('left_knee'),
            pose_data.get_keypoint('left_ankle')
        )
        right_angle = calculate_angle(
            pose_data.get_keypoint('right_hip'),
            pose_data.get_keypoint('right_knee'),
            pose_data.get_keypoint('right_ankle')
        )
        
        avg_angle = (left_angle + right_angle) / 2
        target_angle = 90.0
        
        # 檢查角度是否在容忍範圍內
        is_in_range = is_angle_in_range(
            avg_angle, target_angle, self.tolerance_angle
        )
        
        # 檢查髖關節是否低於膝關節（表示蹲下）
        left_hip_y = pose_data.get_keypoint('left_hip').y
        left_knee_y = pose_data.get_keypoint('left_knee').y
        hip_below_knee = left_hip_y > left_knee_y  # Y 軸向下為正
        
        # 綜合判斷
        is_valid = is_in_range and hip_below_knee
        
        if is_valid:
            feedback = "✓ 深蹲姿勢正確！"
            confidence = 0.9
        elif not hip_below_knee:
            feedback = "✗ 蹲得不夠低，髖關節需低於膝關節"
            confidence = 0.3
        else:
            feedback = f"✗ 膝蓋彎曲角度 {avg_angle:.1f}° (目標 90°±{self.tolerance_angle}°)"
            confidence = 0.4
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            feedback=feedback,
            debug_info={
                "left_knee_angle": left_angle,
                "right_knee_angle": right_angle,
                "avg_angle": avg_angle,
                "hip_below_knee": hip_below_knee
            }
        )
```

---

### 2. PushupValidator (伏地挺身驗證器)

```python
class PushupValidator(ActionValidator):
    @property
    def exercise_name(self) -> str:
        return "伏地挺身"
    
    def get_required_keypoints(self) -> list[str]:
        return ["left_shoulder", "left_elbow", "left_wrist",
                "right_shoulder", "right_elbow", "right_wrist",
                "nose"]
    
    def validate(self, pose_data: PoseData) -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(
                is_valid=False, confidence=0.0,
                feedback="請確保上半身在攝像頭視野內",
                debug_info=None
            )
        
        # 計算手肘彎曲角度
        left_angle = calculate_angle(
            pose_data.get_keypoint('left_shoulder'),
            pose_data.get_keypoint('left_elbow'),
            pose_data.get_keypoint('left_wrist')
        )
        right_angle = calculate_angle(
            pose_data.get_keypoint('right_shoulder'),
            pose_data.get_keypoint('right_elbow'),
            pose_data.get_keypoint('right_wrist')
        )
        
        avg_angle = (left_angle + right_angle) / 2
        target_angle = 85.0  # 伏地挺身目標角度略小於直角
        
        is_in_range = is_angle_in_range(
            avg_angle, target_angle, self.tolerance_angle
        )
        
        # 檢查鼻子是否接近手腕高度（表示身體下降）
        nose_y = pose_data.get_keypoint('nose').y
        avg_wrist_y = (
            pose_data.get_keypoint('left_wrist').y +
            pose_data.get_keypoint('right_wrist').y
        ) / 2
        
        body_lowered = abs(nose_y - avg_wrist_y) < 50  # 50 像素容忍
        
        is_valid = is_in_range and body_lowered
        
        if is_valid:
            feedback = "✓ 伏地挺身姿勢正確！"
            confidence = 0.85
        elif not body_lowered:
            feedback = "✗ 身體下降不足，請讓胸部接近地面"
            confidence = 0.3
        else:
            feedback = f"✗ 手肘彎曲角度 {avg_angle:.1f}° (目標 85°±{self.tolerance_angle}°)"
            confidence = 0.4
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            feedback=feedback,
            debug_info={
                "left_elbow_angle": left_angle,
                "right_elbow_angle": right_angle,
                "avg_angle": avg_angle,
                "body_lowered": body_lowered
            }
        )
```

---

### 3. JumpingJackValidator (開合跳驗證器)

```python
class JumpingJackValidator(ActionValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_state = "closed"  # "closed" or "open"
        self.valid_transition_count = 0
    
    @property
    def exercise_name(self) -> str:
        return "開合跳"
    
    def get_required_keypoints(self) -> list[str]:
        return ["left_wrist", "right_wrist", "nose",
                "left_ankle", "right_ankle", "left_hip", "right_hip"]
    
    def validate(self, pose_data: PoseData) -> ValidationResult:
        if not self.can_validate(pose_data):
            return ValidationResult(
                is_valid=False, confidence=0.0,
                feedback="請確保全身在攝像頭視野內",
                debug_info=None
            )
        
        # 檢查手是否高於頭部
        left_wrist_y = pose_data.get_keypoint('left_wrist').y
        right_wrist_y = pose_data.get_keypoint('right_wrist').y
        nose_y = pose_data.get_keypoint('nose').y
        hands_up = (left_wrist_y < nose_y) and (right_wrist_y < nose_y)
        
        # 檢查雙腳分開寬度
        left_ankle_x = pose_data.get_keypoint('left_ankle').x
        right_ankle_x = pose_data.get_keypoint('right_ankle').x
        ankle_distance = abs(left_ankle_x - right_ankle_x)
        
        shoulder_distance = abs(
            pose_data.get_keypoint('left_hip').x -
            pose_data.get_keypoint('right_hip').x
        )
        feet_wide = ankle_distance > shoulder_distance * 1.5
        
        # 狀態轉換邏輯
        current_state = "open" if (hands_up and feet_wide) else "closed"
        
        # 檢測完整循環（closed → open → closed）
        is_valid = False
        if self.last_state == "closed" and current_state == "open":
            self.valid_transition_count += 1
        elif self.last_state == "open" and current_state == "closed":
            if self.valid_transition_count > 0:
                is_valid = True
                self.valid_transition_count = 0
        
        self.last_state = current_state
        
        if is_valid:
            feedback = "✓ 開合跳完成！"
            confidence = 0.9
        elif current_state == "open":
            feedback = "保持雙手高舉、雙腳分開"
            confidence = 0.5
        else:
            feedback = "請跳起並同時張開手腳"
            confidence = 0.3
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            feedback=feedback,
            debug_info={
                "hands_up": hands_up,
                "feet_wide": feet_wide,
                "current_state": current_state,
                "ankle_distance": ankle_distance,
                "shoulder_distance": shoulder_distance
            }
        )
```

---

## 工具函數庫

驗證器依賴的幾何計算函數：

```python
import numpy as np
from typing import Tuple

def calculate_angle(p1: Keypoint, p2: Keypoint, p3: Keypoint) -> float:
    """
    計算 p1-p2-p3 三點形成的角度（以 p2 為頂點）
    
    Returns:
        float: 角度（度），範圍 [0, 180]
    """
    v1 = np.array([p1.x - p2.x, p1.y - p2.y])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y])
    
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1.0, 1.0)  # 避免數值誤差
    
    angle_rad = np.arccos(cos_angle)
    return np.degrees(angle_rad)

def is_angle_in_range(angle: float, target: float, tolerance: float) -> bool:
    """
    檢查角度是否在目標範圍內
    
    Args:
        angle: 測量角度
        target: 目標角度
        tolerance: 容忍度（度）
    
    Returns:
        bool: True 表示在範圍內
    """
    return abs(angle - target) <= tolerance

def calculate_distance(p1: Keypoint, p2: Keypoint) -> float:
    """
    計算兩點歐氏距離（像素）
    
    Returns:
        float: 距離（像素）
    """
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
```

---

## 測試要求

### 單元測試範例

```python
def test_squat_validator_correct_form():
    validator = SquatValidator(tolerance_angle_degrees=17.5)
    
    # 模擬正確深蹲姿態
    pose_data = create_mock_squat_pose(knee_angle=90, hip_y=200, knee_y=150)
    
    result = validator.validate(pose_data)
    
    assert result.is_valid == True
    assert result.confidence >= 0.8
    assert "正確" in result.feedback

def test_squat_validator_insufficient_depth():
    validator = SquatValidator()
    
    # 模擬蹲得不夠低
    pose_data = create_mock_squat_pose(knee_angle=120, hip_y=100, knee_y=150)
    
    result = validator.validate(pose_data)
    
    assert result.is_valid == False
    assert "不夠低" in result.feedback

def test_validator_performance():
    validator = SquatValidator()
    pose_data = create_mock_squat_pose(knee_angle=90, hip_y=200, knee_y=150)
    
    start = time.perf_counter()
    for _ in range(1000):
        validator.validate(pose_data)
    elapsed_ms = (time.perf_counter() - start) * 1000 / 1000
    
    assert elapsed_ms < 5
```

---

## 憲章符合性

| 原則 | 符合狀態 |
|------|---------|
| 即時性能 | ✅ validate() <5ms 保證 |
| 狀態機 | ✅ 作為 GameState 的輔助組件 |
| 最小 UI | ✅ 僅返回文字反饋，不渲染 |

---

## 相關文件

- [data-model.md](../data-model.md) - PoseData 和 WorkoutTask 定義
- [pose-detector.md](./pose-detector.md) - PoseData 結構
- [game-state.md](./game-state.md) - 狀態機接口
