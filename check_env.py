import shutil
import sys


def check_import(module_name):
    try:
        __import__(module_name)
        print(f"[OK] {module_name}")
    except ImportError:
        print(f"[MISSING] {module_name}")

print(f"Python version: {sys.version}")
print(f"In venv: {sys.prefix != sys.base_prefix}")
print(f"uv installed: {shutil.which('uv') is not None}")

check_import("pygame")
check_import("cv2")
check_import("numpy")
check_import("PIL")
check_import("ultralytics")
check_import("pytest")
check_import("tensorrt")
