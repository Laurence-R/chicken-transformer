# Contract: Rolling State

**Component**: `src/states/rolling_state.py`

## Interface

```python
class RollingState(GameState):
    def __init__(self, task_library: TaskLibrary):
        """
        Args:
            task_library: Access to list of exercises for the animation.
        """
        pass

    @property
    def name(self) -> str:
        return "ROLLING"

    def enter(self, context: GameContext) -> None:
        """
        - Set start time.
        - Select final task (randomly).
        - Initialize animation variables.
        """
        pass

    def update(self, context: GameContext, pose_data: Optional[PoseData]) -> StateTransition:
        """
        - Check if duration elapsed.
        - If elapsed -> Transition to TASK_DISPLAY (with selected task).
        - If not elapsed -> Update `context.rolling_current_item` for display.
        - Return StateTransition(None).
        """
        pass

    def exit(self, context: GameContext) -> None:
        """
        - Clean up animation state.
        """
        pass

    def get_display_message(self) -> str:
        """
        Returns:
            The name of the currently 'rolled' exercise (for the animation effect).
        """
        pass
```
