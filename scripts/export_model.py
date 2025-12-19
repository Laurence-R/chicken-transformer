import os

from ultralytics import YOLO


def export_model():
    # Ensure assets directory exists
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "models")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "yolov8n-pose.pt")
    onnx_path = os.path.join(model_dir, "yolov8n-pose.onnx")

    # Download model if not exists (Ultralytics handles this automatically usually, but good to be explicit)
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}, downloading...")
        model = YOLO("yolov8n-pose.pt")
        model.save(model_path)
    else:
        print(f"Loading model from {model_path}...")
        model = YOLO(model_path)

    print("Exporting to ONNX...")
    # Export arguments optimized for TensorRT
    # dynamic=False ensures fixed input size which is often faster/simpler for TensorRT
    # simplify=True runs onnx-simplifier
    success = model.export(format="onnx", dynamic=False, simplify=True, imgsz=640)

    if success:
        print(f"Export successful! ONNX file saved to: {success}")
        # Move it to our assets folder if it wasn't saved there directly
        if success != onnx_path and os.path.exists(success):
            os.rename(success, onnx_path)
            print(f"Moved to: {onnx_path}")
    else:
        print("Export failed!")

if __name__ == "__main__":
    export_model()
