# Deployment Guide

## Production Checklist

### 1. Hardware Verification
- [ ] Jetson Orin Nano (8GB recommended)
- [ ] CSI Camera connected (or USB Camera as fallback)
- [ ] Power Mode: 15W (MAXN)
- [ ] Fan Mode: Cool/Quiet

### 2. Software Environment
- [ ] JetPack 5.1.2+ or 6.0+
- [ ] Python 3.10+
- [ ] TensorRT 8.5.2+
- [ ] CUDA 11.4+

### 3. Model Verification
- [ ] Engine file exists: `assets/models/yolov8n-pose.engine`
- [ ] Engine file size is valid (~9-10MB for FP16)
- [ ] Benchmark script passes: `uv run scripts/benchmark_detector.py`
  - [ ] Average Inference Time < 50ms (Target: ~20ms)
  - [ ] FPS > 20

### 4. Application Configuration
- [ ] `config/exercises.json` contains valid exercises
- [ ] `pyproject.toml` has correct dependencies

### 5. Running the Application
```bash
# Check Display (Important for GUI)
echo $DISPLAY
# If empty or wrong, set it (usually :0 or :1)
export DISPLAY=:0

# Run with TensorRT and CSI Camera (using uv)
uv run src/main.py --mode tensorrt --camera csi

# OR Run with USB Camera
uv run src/main.py --mode tensorrt --camera usb
```

### 6. Troubleshooting
- **Camera fails to open**: Check `ls /dev/video*` and `nvgstcapture-1.0`
- **TensorRT error**: Re-run `scripts/export_model.py` and `trtexec`
- **Low FPS**: Run `sudo jetson_clocks`
