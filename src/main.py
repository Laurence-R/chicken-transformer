"""Main entry point for Fitness Dice Game."""

import argparse
import os
import sys
import time
import pygame
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game.game_manager import GameManager
from src.models.mock_detector import MockPoseDetector
from src.states.completion_state import CompletionState
from src.states.dice_state import DiceRollDetectingState
from src.states.rolling_state import RollingState
from src.states.task_display_state import TaskDisplayState
from src.states.task_executing_state import TaskExecutingState
from src.states.waiting_state import WaitingState
from src.tasks.task_library import TaskLibrary
from src.ui.game_window import GameWindow

# Conditional imports for Jetson modules
try:
    from src.camera.camera_manager import CameraManager
    from src.models.tensorrt_detector import TensorRTPoseDetector
except ImportError:
    TensorRTPoseDetector = None
    CameraManager = None


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        argparse.Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fitness Dice Game - 弱雞轉換器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # WSL development with mock detector
  python src/main.py --mode mock

  # Jetson with TensorRT and CSI camera
  python src/main.py --mode tensorrt --camera csi

  # Jetson with USB camera
  python src/main.py --mode tensorrt --camera usb
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["mock", "tensorrt"],
        default="mock",
        help="Pose detector mode: 'mock' for WSL development, 'tensorrt' for Jetson deployment",
    )

    parser.add_argument(
        "--camera",
        choices=["csi", "usb", "none"],
        default="none",
        help="Camera type: 'csi' for CSI camera, 'usb' for USB webcam, 'none' for mock mode",
    )

    parser.add_argument(
        "--mock-pose",
        choices=["standing", "squatting", "jumping", "pushup_up", "pushup_down"],
        default="standing",
        help="Initial pose for mock detector (only used with --mode mock)",
    )

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose logging"
    )

    parser.add_argument(
        "--fps", type=int, default=30, help="Target frames per second (default: 30)"
    )

    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_arguments()

    # Validate arguments
    if args.mode == "tensorrt" and args.camera == "none":
        print("Error: TensorRT mode requires --camera (csi|usb)", file=sys.stderr)
        sys.exit(1)

    if args.mode == "mock" and args.camera != "none":
        print("Warning: Mock mode ignores --camera argument", file=sys.stderr)

    print("Starting Fitness Dice Game...")
    print(f"  Mode: {args.mode}")
    print(f"  Camera: {args.camera}")
    print(f"  Target FPS: {args.fps}")
    print(f"  Debug: {args.debug}")

    # Initialize UI first to show loading screen
    try:
        game_window = GameWindow(fps=args.fps)
    except Exception as e:
        print(f"Failed to initialize GameWindow: {e}")
        print("Ensure you have a display environment (e.g., XServer for WSL)")
        sys.exit(1)

    # Initialize Components
    game_window.draw_loading_screen(0.1, "Loading Task Library...")
    try:
        task_lib = TaskLibrary()
        # Load exercises from config relative to project root
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "exercises.json"
        )
        task_lib.load_from_json(config_path)
        print(f"Loaded {len(task_lib.exercises)} exercises.")
    except Exception as e:
        print(f"Error loading task library: {e}")
        game_window.close()
        sys.exit(1)

    game_manager = GameManager(task_lib)

    # Register States
    game_manager.register_state(WaitingState())
    game_manager.register_state(DiceRollDetectingState())
    game_manager.register_state(RollingState(task_lib))
    game_manager.register_state(TaskDisplayState(task_lib))
    game_manager.register_state(TaskExecutingState())
    game_manager.register_state(CompletionState())

    game_manager.set_initial_state("WAITING")

    # Initialize Camera (if needed)
    game_window.draw_loading_screen(0.3, "Initializing Camera...")
    camera_manager = None
    if args.camera != "none":
        if CameraManager is None:
            print("Error: CameraManager not available (missing dependencies?)")
            game_window.close()
            sys.exit(1)
        camera_manager = CameraManager(camera_type=args.camera, fps=args.fps)
        if not camera_manager.initialize():
            print("Failed to initialize camera")
            game_window.close()
            sys.exit(1)

    # Initialize Detector
    game_window.draw_loading_screen(0.6, "Loading AI Model...")
    detector = None
    if args.mode == "mock":
        detector = MockPoseDetector(mode=args.mock_pose)
        if not detector.initialize():
            print("Failed to initialize mock detector")
            if camera_manager:
                camera_manager.release()
            game_window.close()
            sys.exit(1)
    elif args.mode == "tensorrt":
        if TensorRTPoseDetector is None:
            print("Error: TensorRTPoseDetector not available (missing tensorrt/pycuda?)")
            if camera_manager:
                camera_manager.release()
            game_window.close()
            sys.exit(1)

        engine_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "models",
            "yolov8n-pose.engine",
        )
        detector = TensorRTPoseDetector(engine_path=engine_path)
        if not detector.initialize():
            print("Failed to initialize TensorRT detector")
            if camera_manager:
                camera_manager.release()
            game_window.close()
            sys.exit(1)
    else:
        print(f"Unknown mode: {args.mode}")
        if camera_manager:
            camera_manager.release()
        game_window.close()
        sys.exit(1)

    game_window.draw_loading_screen(1.0, "Starting Game...")
    time.sleep(0.5) # Short pause to show 100%

    print("\nGame Started! Press Esc to exit.")

    try:
        while game_window.running:
            # Get Frame
            frame = None
            if camera_manager:
                ret, frame = camera_manager.read()
                if not ret:
                    print("Failed to read frame from camera")
                    continue
            else:
                # Mock frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Detect
            pose_data = detector.detect(frame)

            # Update Game Logic
            game_manager.update(pose_data)

            # Update UI
            game_window.update(game_manager.context, frame, pose_data)

            # Console logging (debug only)
            if args.debug:
                msg = game_manager.get_current_message().replace("\n", " ")
                state = game_manager.current_state.name if game_manager.current_state else "None"
                print(f"[{state}] {msg} | Pose: {pose_data.confidence if pose_data else 0.0:.2f}")

    except KeyboardInterrupt:
        print("\nGame Stopped.")
    finally:
        if detector:
            detector.release()
        if camera_manager:
            camera_manager.release()
        game_window.close()


if __name__ == "__main__":
    main()
