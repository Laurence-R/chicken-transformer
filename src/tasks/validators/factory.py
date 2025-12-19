import importlib
from typing import Optional

from .action_validator import ActionValidator


class ValidatorFactory:
    @staticmethod
    def create_validator(validator_class_name: str) -> Optional[ActionValidator]:
        """Dynamically load and instantiate a validator class.

        Args:
            validator_class_name: Name of the validator class (e.g., "SquatValidator")

        Returns:
            Instance of the validator class, or None if not found.
        """
        # Convert CamelCase to snake_case for module name
        # e.g. SquatValidator -> squat_validator
        # This is a simple heuristic, might need adjustment if naming convention differs
        module_name = ""
        if validator_class_name.endswith("Validator"):
            base_name = validator_class_name[:-9]  # Remove "Validator"
            # Convert CamelCase to snake_case
            import re

            module_name = re.sub(r"(?<!^)(?=[A-Z])", "_", base_name).lower()
            module_name = f"{module_name}_validator"
        else:
            return None

        try:
            # Try to import the module from the same package
            module = importlib.import_module(f".{module_name}", package="src.tasks.validators")
            validator_class = getattr(module, validator_class_name)
            return validator_class()
        except (ImportError, AttributeError) as e:
            print(f"Failed to load validator {validator_class_name}: {e}")
            return None
