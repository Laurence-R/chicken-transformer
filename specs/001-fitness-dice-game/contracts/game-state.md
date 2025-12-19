# Contract: GameState

**Date**: 2025-12-19  
**Type**: Abstract Base Class (ABC)  
**Purpose**: 定義遊戲狀態的統一接口，實現狀態模式

---

## 接口定義

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class StateTransition:
    """狀態轉換結果"""
    next_state_name: Optional[str]  # None 表示保持當前狀態
    context_updates: dict  # 需要更新到 GameContext 的數據

class GameState(ABC):
    """遊戲狀態抽象基類"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        狀態名稱（唯一標識符）
        
        Returns:
            str: 例如 "WAITING", "DICE_ROLL_DETECTING"
        """
        pass
    
    @abstractmethod
    def enter(self, context: 'GameContext') -> None:
        """
        進入狀態時的初始化邏輯
        
        Args:
            context: 遊戲上下文，包含共享數據和狀態
            
        Requirements:
            - 設置狀態特定的計時器和標誌位
            - 記錄進入時間戳（用於超時檢測）
            - 更新 UI 顯示訊息
            
        Example:
            self.enter_time = time.time()
            context.ui.show_message("請跳躍並舉手擲骰子")
        """
        pass
    
    @abstractmethod
    def update(self, context: 'GameContext', pose_data: Optional[PoseData]) -> StateTransition:
        """
        每幀調用，處理狀態邏輯並決定是否轉換
        
        Args:
            context: 遊戲上下文
            pose_data: 當前幀的姿態數據（可能為 None）
            
        Returns:
            StateTransition: 包含下一個狀態名稱和需要更新的上下文數據
            
        Requirements:
            - 執行時間 <10ms（避免阻塞主循環）
            - 返回 StateTransition(next_state_name=None, ...) 表示保持當前狀態
            - 轉換條件必須明確且可測試
            
        Example:
            if self._detect_jump(pose_data):
                return StateTransition(
                    next_state_name="DICE_ROLL_DETECTING",
                    context_updates={"last_action": "jump"}
                )
            return StateTransition(next_state_name=None, context_updates={})
        """
        pass
    
    @abstractmethod
    def exit(self, context: 'GameContext') -> None:
        """
        離開狀態時的清理邏輯
        
        Args:
            context: 遊戲上下文
            
        Requirements:
            - 清理狀態特定的資源（計時器、臨時數據）
            - 不應拋出異常（使用 try-except 保護）
            
        Example:
            context.clear_temporary_flags()
            self.enter_time = None
        """
        pass
    
    @abstractmethod
    def get_display_message(self) -> str:
        """
        返回當前狀態的 UI 提示文字
        
        Returns:
            str: 顯示在 InfoPanel 的訊息（繁體中文）
            
        Example:
            "等待開始 - 請跳躍並舉手"
            "正在擲骰子... (2 秒內)"
            "任務：深蹲 15 次 x 2 組"
        """
        pass
```

---

## 約定 (Contracts)

### 前置條件 (Preconditions)

1. **初始化順序**: `enter()` 必須在首次 `update()` 前調用
2. **上下文有效性**: `context` 必須包含有效的 `ui`, `task_library`, `progress_tracker` 實例
3. **姿態數據可選**: `update()` 的 `pose_data` 可為 None（攝像頭故障或無人檢測）

### 後置條件 (Postconditions)

1. **轉換一致性**: 
   - `StateTransition.next_state_name` 必須對應已註冊的狀態名稱或為 None
   - `context_updates` 中的鍵必須是 GameContext 的有效屬性
   
2. **性能保證**:
   - `update()` 執行時間 <10ms (99th percentile)
   - `enter()` / `exit()` 執行時間 <5ms
   
3. **異常安全**:
   - `exit()` 不應拋出異常（內部捕獲並記錄）
   - `update()` 異常不應導致狀態機崩潰

### 不變量 (Invariants)

1. **狀態唯一性**: 每個狀態實例的 `name` 全局唯一
2. **單向時間**: `enter_time` 只在 `enter()` 中設置，`update()` 中只讀
3. **無副作用查詢**: `get_display_message()` 不修改狀態

---

## 具體實現類

### 1. WaitingState (等待開始)

**轉換條件**:
- 檢測到跳躍動作 → `DICE_ROLL_DETECTING`

**關鍵邏輯**:
```python
def update(self, context, pose_data):
    if pose_data and self._is_jumping(pose_data):
        return StateTransition(
            next_state_name="DICE_ROLL_DETECTING",
            context_updates={"jump_detected_time": time.time()}
        )
    return StateTransition(next_state_name=None, context_updates={})

def _is_jumping(self, pose_data: PoseData) -> bool:
    # 雙腳離地：腳踝 Y 座標明顯高於平常
    left_ankle = pose_data.get_keypoint('left_ankle')
    right_ankle = pose_data.get_keypoint('right_ankle')
    avg_ankle_y = (left_ankle.y + right_ankle.y) / 2
    return avg_ankle_y < context.baseline_ankle_y - 50  # 上升 50 像素
```

---

### 2. DiceRollDetectingState (擲骰子檢測)

**轉換條件**:
- 2 秒內檢測到舉手 → `TASK_DISPLAY`
- 超時 2 秒未舉手 → `WAITING`

**關鍵邏輯**:
```python
def update(self, context, pose_data):
    elapsed = time.time() - self.enter_time
    
    if elapsed > 2.0:  # 超時
        return StateTransition(
            next_state_name="WAITING",
            context_updates={"error_message": "擲骰子超時"}
        )
    
    if pose_data and self._is_hands_raised(pose_data):
        task = context.task_library.get_random_task()
        return StateTransition(
            next_state_name="TASK_DISPLAY",
            context_updates={"current_task": task}
        )
    
    return StateTransition(next_state_name=None, context_updates={})

def _is_hands_raised(self, pose_data: PoseData) -> bool:
    left_wrist = pose_data.get_keypoint('left_wrist')
    right_wrist = pose_data.get_keypoint('right_wrist')
    nose = pose_data.get_keypoint('nose')
    return left_wrist.y < nose.y and right_wrist.y < nose.y
```

---

### 3. TaskDisplayState (任務展示)

**轉換條件**:
- 顯示 3 秒後 → `TASK_EXECUTING`

**關鍵邏輯**:
```python
def enter(self, context):
    self.enter_time = time.time()
    context.ui.show_task(context.current_task)
    context.progress_tracker.reset()

def update(self, context, pose_data):
    if time.time() - self.enter_time > 3.0:
        return StateTransition(
            next_state_name="TASK_EXECUTING",
            context_updates={}
        )
    return StateTransition(next_state_name=None, context_updates={})
```

---

### 4. TaskExecutingState (任務執行)

**轉換條件**:
- 完成所有組 → `COMPLETION`

**關鍵邏輯**:
```python
def update(self, context, pose_data):
    if not pose_data:
        return StateTransition(next_state_name=None, context_updates={})
    
    # 驗證動作
    task = context.current_task
    if task.validate_rep(pose_data):
        set_complete = context.progress_tracker.increment_rep()
        
        if set_complete:
            all_complete = context.progress_tracker.next_set()
            if all_complete:
                return StateTransition(
                    next_state_name="COMPLETION",
                    context_updates={"completion_time": time.time()}
                )
    
    return StateTransition(next_state_name=None, context_updates={})
```

---

### 5. CompletionState (完成驗證)

**轉換條件**:
- 顯示完成訊息 2 秒後 → `WAITING`

**關鍵邏輯**:
```python
def enter(self, context):
    self.enter_time = time.time()
    context.ui.show_completion_animation()

def update(self, context, pose_data):
    if time.time() - self.enter_time > 2.0:
        return StateTransition(
            next_state_name="WAITING",
            context_updates={"last_task": context.current_task}
        )
    return StateTransition(next_state_name=None, context_updates={})
```

---

## 狀態轉換圖

```
┌─────────────┐
│   WAITING   │ (初始狀態)
└─────────────┘
      │ 檢測到跳躍
      ▼
┌──────────────────────┐
│ DICE_ROLL_DETECTING  │
└──────────────────────┘
      │ 2秒內舉手               │ 超時
      ▼                          ▼
┌──────────────┐          (返回 WAITING)
│ TASK_DISPLAY │
└──────────────┘
      │ 顯示 3 秒
      ▼
┌──────────────────┐
│ TASK_EXECUTING   │ ◄──┐
└──────────────────┘    │ 未完成保持
      │ 完成所有組      │
      ▼                  │
┌──────────────┐          │
│  COMPLETION  │ ─────────┘
└──────────────┘
      │ 顯示 2 秒
      ▼
  (返回 WAITING)
```

---

## 測試要求

### 單元測試覆蓋

1. **狀態進入/退出**:
   ```python
   def test_waiting_state_enter():
       state = WaitingState()
       context = MockGameContext()
       state.enter(context)
       assert state.enter_time > 0
   ```

2. **轉換邏輯**:
   ```python
   def test_dice_roll_timeout():
       state = DiceRollDetectingState()
       context = MockGameContext()
       state.enter(context)
       time.sleep(2.1)
       
       transition = state.update(context, None)
       assert transition.next_state_name == "WAITING"
   ```

3. **性能測試**:
   ```python
   def test_update_performance():
       state = TaskExecutingState()
       context = MockGameContext()
       pose_data = create_mock_pose_data()
       
       start = time.perf_counter()
       for _ in range(100):
           state.update(context, pose_data)
       elapsed_ms = (time.perf_counter() - start) * 1000 / 100
       
       assert elapsed_ms < 10
   ```

---

## 憲章符合性

| 原則 | 符合狀態 |
|------|---------|
| 即時性能 | ✅ update() <10ms 保證 |
| 狀態機 | ✅ 核心設計模式 |
| 最小 UI | ✅ 僅返回顯示字串，不渲染 |

---

## 相關文件

- [data-model.md](../data-model.md) - GameContext 和 WorkoutTask 定義
- [pose-detector.md](./pose-detector.md) - PoseData 結構
- [action-validator.md](./action-validator.md) - 動作驗證接口
