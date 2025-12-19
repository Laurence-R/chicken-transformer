import os
import sys
import time

import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.models.tensorrt_detector import TensorRTPoseDetector
    print("Successfully imported TensorRTPoseDetector")
except ImportError as e:
    print(f"Failed to import TensorRTPoseDetector: {e}")
    sys.exit(1)

def main():
    engine_path = "assets/models/yolov8n-pose.engine"
    if not os.path.exists(engine_path):
        print(f"Engine file not found: {engine_path}")
        sys.exit(1)

    print(f"Loading engine from {engine_path}...")
    try:
        detector = TensorRTPoseDetector(engine_path=engine_path)
        detector.initialize()
        print("Engine loaded successfully!")
    except Exception as e:
        print(f"Failed to load engine: {e}")
        sys.exit(1)

    # Create dummy image (640x640x3)
    dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)

    print("Running warm-up inference...")
    for _ in range(5):
        detector.detect(dummy_frame)

    print("Running benchmark (100 iterations)...")
    times = []
    for _ in range(100):
        start = time.time()
        detector.detect(dummy_frame)
        end = time.time()
        times.append((end - start) * 1000)

    avg_time = np.mean(times)
    p95_time = np.percentile(times, 95)
    p99_time = np.percentile(times, 99)

    print(f"Average Inference Time: {avg_time:.2f} ms")
    print(f"P95 Inference Time: {p95_time:.2f} ms")
    print(f"P99 Inference Time: {p99_time:.2f} ms")
    print(f"FPS: {1000/avg_time:.2f}")

    detector.release()
    print("Test completed.")

if __name__ == "__main__":
    main()
