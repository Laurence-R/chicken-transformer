# Data Model: 健身骰子遊戲 (Fitness Dice Game)

**Date**: 2025-12-19  
**Phase**: 1 - Design & Contracts  
**Purpose**: 定義系統核心實體、屬性、關係和驗證規則

---

## 實體總覽

本系統包含以下核心實體：

1. **GameState** (抽象) - 遊戲狀態基類
2. **PoseData** - 姿態數據（YOLOv8-Pose 輸出）
3. **WorkoutTask** - 健身任務
4. **TaskLibrary** - 任務庫
5. **ProgressTracker** - 進度追蹤器
6. **ActionValidator** (抽象) - 動作驗證器基類

---

## 實體 1: GameState (抽象基類)

**用途**: 表示遊戲的五種狀態之一，封裝狀態特定的行為和轉換邏輯

### 屬性

| 屬性名 | 類型 | 描述 | 驗證規則 |
|--------|------|------|----------|
| `name` | `str` | 狀態名稱（唯讀） | 由子類定義，非空 |
| `timestamp` | `float` | 進入該狀態的時間戳 | Unix timestamp |

### 方法

- `enter(context: GameContext) -> None`: 進入狀態時的初始化邏輯
- `update(context: GameContext, pose_data: PoseData) -> StateTransition`: 每幀調用，處理狀態邏輯並返回轉換
- `exit(context: GameContext) -> None`: 離開狀態時的清理邏輯
- `get_display_message() -> str`: 返回當前狀態的 UI 提示文字

### 具體子類

1. **WaitingState** - 等待開始
2. **DiceRollDetectingState** - 擲骰子動作檢測
3. **TaskDisplayState** - 任務展示
4. **TaskExecutingState** - 任務執行中
5. **CompletionState** - 完成驗證

### 關係

- `GameContext` 維護當前 `GameState` 實例（組合關係）
- 各狀態之間透過 `StateTransition` 轉換

---

## 實體 2: PoseData

**用途**: 封裝單幀的人體姿態檢測結果（17 個 COCO 關鍵點）

### 屬性

| 屬性名 | 類型 | 描述 | 驗證規則 |
|--------|------|------|----------|
| `keypoints` | `List[Keypoint]` | 17 個關鍵點列表 | 長度必須為 17 |
| `bbox` | `BoundingBox` | 人體邊界框 | 可選（Optional） |
| `confidence` | `float` | 整體檢測置信度 | 0.0 ~ 1.0 |
| `frame_id` | `int` | 幀編號 | >= 0 |
| `timestamp` | `float` | 捕獲時間戳 | Unix timestamp |

### 嵌套結構: Keypoint

| 屬性名 | 類型 | 描述 | 驗證規則 |
|--------|------|------|----------|
| `x` | `float` | X 座標（像素） | >= 0 |
| `y` | `float` | Y 座標（像素） | >= 0 |
| `confidence` | `float` | 關鍵點置信度 | 0.0 ~ 1.0 |
| `visible` | `bool` | 是否可見 | confidence > 0.5 視為可見 |

### 嵌套結構: BoundingBox

| 屬性名 | 類型 | 描述 |
|--------|------|------|
| `x1, y1` | `float` | 左上角座標 |
| `x2, y2` | `float` | 右下角座標 |
| `width, height` | `float` | 寬度和高度 |

### COCO 關鍵點索引映射

```python
KEYPOINT_INDICES = {
    'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
    'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
    'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
    'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16
}
```

### 方法

- `get_keypoint(name: str) -> Keypoint`: 根據名稱獲取關鍵點
- `is_valid() -> bool`: 檢查數據是否有效（至少 8 個關鍵點可見）
- `get_skeleton_lines() -> List[Tuple[Keypoint, Keypoint]]`: 返回骨架連線用於渲染

### 關係

- `PoseDetector` 產生 `PoseData`
- `ActionValidator` 消費 `PoseData` 進行驗證
- `GameState.update()` 接收 `PoseData` 進行狀態邏輯處理

---

## 實體 3: WorkoutTask

**用途**: 表示一次健身任務（動作類型 + 次數 + 組數）

### 屬性

| 屬性名 | 類型 | 描述 | 驗證規則 |
|--------|------|------|----------|
| `id` | `str` | 任務唯一標識符 | UUID 格式 |
| `exercise_type` | `str` | 動作類型（例如 "squat"） | 必須存在於任務庫中 |
| `reps_per_set` | `int` | 每組次數 | 5 ~ 20 |
| `total_sets` | `int` | 總組數 | 1 ~ 3 |
| `description` | `str` | 任務描述文字 | 例如 "深蹲 15 次 x 2 組" |
| `validator` | `ActionValidator` | 關聯的驗證器實例 | 非空 |
| `created_at` | `float` | 創建時間戳 | Unix timestamp |

### 方法

- `to_display_string() -> str`: 生成 UI 顯示字串（例如 "深蹲 15 次 x 2 組"）
- `validate_rep(pose_data: PoseData) -> bool`: 委派給驗證器檢查單次動作
- `is_complete(current_reps: int, current_set: int) -> bool`: 判斷任務是否完成

### 關係

- `TaskLibrary` 創建 `WorkoutTask` 實例
- `TaskExecutingState` 維護當前 `WorkoutTask`
- `ProgressTracker` 追蹤 `WorkoutTask` 的完成狀態

---

## 實體 4: TaskLibrary

**用途**: 管理所有可用的健身動作定義，負責隨機抽取任務

### 屬性

| 屬性名 | 類型 | 描述 | 驗證規則 |
|--------|------|------|----------|
| `exercises` | `Dict[str, ExerciseDefinition]` | 動作定義字典 | 至少 10 種動作 |
| `config_path` | `str` | JSON 配置文件路徑 | 檔案必須存在 |

### 嵌套結構: ExerciseDefinition

| 屬性名 | 類型 | 描述 |
|--------|------|------|
| `name_zh` | `str` | 中文名稱（例如 "深蹲"） |
| `name_en` | `str` | 英文標識符（例如 "squat"） |
| `validator_class` | `str` | 驗證器類名（例如 "SquatValidator"） |
| `min_reps` | `int` | 最小次數（預設 5） |
| `max_reps` | `int` | 最大次數（預設 20） |
| `min_sets` | `int` | 最小組數（預設 1） |
| `max_sets` | `int` | 最大組數（預設 3） |
| `difficulty` | `str` | 難度等級（"easy", "medium", "hard"） |

### 方法

- `load_from_json(path: str) -> None`: 從 JSON 載入任務庫
- `get_random_task() -> WorkoutTask`: 隨機抽取一個任務
- `get_exercise(exercise_type: str) -> ExerciseDefinition`: 根據類型獲取定義
- `validate_library() -> bool`: 驗證庫完整性（至少 10 種動作）

### JSON 格式範例

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
    }
  ]
}
```

### 關係

- `DiceRollDetectingState` 使用 `TaskLibrary.get_random_task()` 創建任務
- `TaskLibrary` 實例化對應的 `ActionValidator`

---

## 實體 5: ProgressTracker

**用途**: 追蹤當前任務的執行進度（當前組、當前次數）

### 屬性

| 屬性名 | 類型 | 描述 | 驗證規則 |
|--------|------|------|----------|
| `current_set` | `int` | 當前組數（1-based） | 1 ~ total_sets |
| `current_reps` | `int` | 當前組已完成次數 | 0 ~ reps_per_set |
| `total_sets` | `int` | 總組數 | 來自 WorkoutTask |
| `reps_per_set` | `int` | 每組次數 | 來自 WorkoutTask |
| `last_rep_timestamp` | `float` | 最後一次有效動作時間戳 | Unix timestamp |
| `is_completed` | `bool` | 是否所有組都已完成 | 唯讀計算屬性 |

### 方法

- `reset() -> None`: 重置追蹤器（新任務開始時）
- `increment_rep() -> bool`: 增加一次計數，返回是否完成當前組
- `next_set() -> bool`: 進入下一組，返回是否所有組都已完成
- `get_progress_percentage() -> float`: 返回總進度百分比（0.0 ~ 1.0）
- `get_display_text() -> str`: 生成進度顯示文字（例如 "第 1 組：5/10 完成"）

### 狀態機邏輯

```
初始: current_set=1, current_reps=0
→ increment_rep() x10 → current_reps=10 (滿)
→ next_set() → current_set=2, current_reps=0
→ increment_rep() x10 → current_reps=10 (滿)
→ next_set() → is_completed=True
```

### 關係

- `TaskExecutingState` 擁有並更新 `ProgressTracker`
- `InfoPanel` (UI) 讀取 `ProgressTracker` 顯示進度

---

## 實體 6: ActionValidator (抽象基類)

**用途**: 驗證特定健身動作是否正確執行

### 屬性

| 屬性名 | 類型 | 描述 |
|--------|------|------|
| `exercise_name` | `str` | 動作名稱 |
| `tolerance_angle_degrees` | `float` | 角度容忍度（預設 17.5°） |
| `tolerance_distance_ratio` | `float` | 距離容忍度（預設 0.10） |

### 方法（抽象）

- `validate(pose_data: PoseData) -> ValidationResult`: 檢查動作是否正確
- `get_feedback_message(pose_data: PoseData) -> str`: 返回錯誤提示（例如 "蹲得不夠低"）

### 返回結構: ValidationResult

| 屬性名 | 類型 | 描述 |
|--------|------|------|
| `is_valid` | `bool` | 動作是否有效 |
| `confidence` | `float` | 驗證置信度（0.0 ~ 1.0） |
| `feedback` | `str` | 錯誤提示或鼓勵訊息 |

### 具體子類範例

#### SquatValidator（深蹲驗證器）

**驗證規則**：
1. 雙膝彎曲角度 85° ~ 110°（目標 90°，容忍 ±17.5°）
2. 髖關節 Y 座標高於膝關節 Y 座標（表示蹲下）
3. 軀幹相對垂直（肩膀-髖關節線與垂直線夾角 <30°）

```python
def validate(self, pose_data: PoseData) -> ValidationResult:
    left_knee_angle = calculate_angle(
        pose_data.get_keypoint('left_hip'),
        pose_data.get_keypoint('left_knee'),
        pose_data.get_keypoint('left_ankle')
    )
    
    is_in_range = is_angle_in_range(left_knee_angle, 90, self.tolerance_angle_degrees)
    hip_below = pose_data.get_keypoint('left_hip').y > pose_data.get_keypoint('left_knee').y
    
    return ValidationResult(
        is_valid=is_in_range and hip_below,
        confidence=0.9,
        feedback="深蹲姿勢正確！" if is_valid else "蹲得不夠低"
    )
```

#### PushupValidator（伏地挺身驗證器）

**驗證規則**：
1. 手肘彎曲角度 70° ~ 100°（目標 85°）
2. 鼻子 Y 座標接近手腕 Y 座標（±50 像素）
3. 軀幹保持直線（肩-髖-膝三點近似共線）

### 關係

- `WorkoutTask` 持有特定的 `ActionValidator` 實例
- `TaskExecutingState` 每幀調用驗證器檢查動作

---

## 實體關係圖

```
┌─────────────────┐
│  GameContext    │  (遊戲主控制器)
├─────────────────┤
│ - current_state │──────┐
│ - current_task  │──┐   │
│ - progress      │  │   │
└─────────────────┘  │   │
                     │   │
    ┌────────────────┘   │
    │                    │
    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  WorkoutTask    │  │   GameState     │ (抽象)
├─────────────────┤  ├─────────────────┤
│ - exercise_type │  │ - name          │
│ - reps_per_set  │  │ - timestamp     │
│ - total_sets    │  └─────────────────┘
│ - validator     │          │
└─────────────────┘          │ 繼承
    │                        │
    │ 關聯                   ├─ WaitingState
    │                        ├─ DiceRollDetectingState
    ▼                        ├─ TaskDisplayState
┌─────────────────┐          ├─ TaskExecutingState
│ ActionValidator │ (抽象)   └─ CompletionState
├─────────────────┤
│ - validate()    │
└─────────────────┘
    │ 繼承
    ├─ SquatValidator
    ├─ PushupValidator
    ├─ JumpingJackValidator
    └─ ... (10+ 驗證器)

┌─────────────────┐
│  PoseData       │  (姿態數據)
├─────────────────┤
│ - keypoints[17] │
│ - bbox          │
│ - confidence    │
└─────────────────┘
        │ 輸入
        ▼
┌─────────────────┐
│ PoseDetector    │  (抽象)
├─────────────────┤
│ - detect()      │
└─────────────────┘
    │ 繼承
    ├─ TensorRTDetector (Jetson)
    └─ MockDetector (WSL)
```

---

## 數據流程

### 擲骰子流程
```
1. WaitingState 檢測 PoseData → 發現跳躍
2. 轉換到 DiceRollDetectingState
3. 2 秒內檢測到舉手 → 調用 TaskLibrary.get_random_task()
4. 創建 WorkoutTask → 轉換到 TaskDisplayState
```

### 任務執行流程
```
1. TaskDisplayState 顯示任務 3 秒 → 轉換到 TaskExecutingState
2. TaskExecutingState.update(pose_data):
   - 調用 task.validate_rep(pose_data)
   - 若有效 → progress_tracker.increment_rep()
   - 若完成一組 → progress_tracker.next_set()
   - 若所有組完成 → 轉換到 CompletionState
```

---

## 驗證規則總結

### 容忍度參數（全局）

| 參數 | 值 | 應用範圍 |
|------|-----|----------|
| 角度容忍度 | ±17.5° | 所有關節角度檢查 |
| 距離容忍度 | ±10% | 相對距離比例檢查 |
| 置信度閾值 | >0.5 | 關鍵點可見性判斷 |
| 動作持續時間 | >0.3 秒 | 避免誤觸發（深蹲需保持） |

### 10+ 種動作驗證規則（簡要）

1. **深蹲 (Squat)**: 膝蓋角度 90°±17.5°, 髖低於膝
2. **伏地挺身 (Pushup)**: 手肘角度 85°±17.5°, 鼻子接近地面
3. **開合跳 (Jumping Jack)**: 雙手高於頭部, 雙腳分開寬度 >肩寬 1.5 倍
4. **弓箭步 (Lunge)**: 前膝角度 90°, 後膝接近地面
5. **平板支撐 (Plank)**: 肩-髖-踝三點共線, 持續時間檢測
6. **仰臥起坐 (Sit-up)**: 軀幹從平躺到起身 >60°
7. **波比跳 (Burpee)**: 序列檢測（蹲-跳-伏地挺身-起立）
8. **登山跑 (Mountain Climber)**: 膝蓋交替接近胸部
9. **高抬腿 (High Knees)**: 膝蓋高於髖關節, 交替檢測
10. **俄羅斯轉體 (Russian Twist)**: 軀幹旋轉角度 >30°, 手臂接觸地面

---

## 下一步

資料模型已完成，接下來：
1. ✅ 生成 `contracts/` 目錄（定義抽象接口）
2. ⏳ 生成 `quickstart.md`（環境設置和運行指南）
