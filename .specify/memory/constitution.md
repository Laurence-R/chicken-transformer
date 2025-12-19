<!--
Sync Impact Report:
Version: 1.0.0 (Initial ratification)
Changes:
  - New constitution established for Chicken Transformer project
  - Defined 6 core principles focused on Jetson Orin Nano optimization
  - Established real-time performance standards (>20 FPS camera, <50ms inference)
  - Mandated TensorRT acceleration and on-device inference
  - Set Python class-based architecture requirements
Templates Status:
  ✅ plan-template.md - Aligned with constitution check requirements
  ✅ spec-template.md - User story format compatible with performance goals
  ✅ tasks-template.md - Task categorization supports principle validation
Follow-up Items:
  - None - all placeholders filled
-->

# Chicken Transformer Constitution

## Core Principles

### I. Jetson Orin Nano Optimization (NON-NEGOTIABLE)

**All code MUST be optimized for Jetson Orin Nano hardware**. This includes:
- CUDA-aware memory management and allocation patterns
- TensorRT engine usage for all deep learning inference
- ARM64 architecture compatibility and optimization
- GPU memory constraints respected (<8GB total budget)
- Power efficiency considerations for embedded deployment

**Rationale**: The project targets a specific embedded platform with constrained resources. Code that doesn't respect these constraints will fail in production.

### II. Real-Time Performance Standards (NON-NEGOTIABLE)

**Performance requirements are mandatory, not aspirational**:
- Camera capture and processing: **>20 FPS sustained** (no frame drops under normal conditions)
- Model inference latency: **<50ms per frame** for YOLOv8-Pose with TensorRT
- End-to-end pipeline latency: **<100ms** from capture to UI update
- Memory footprint: **<4GB** for entire application including models

**Rationale**: Real-time vision applications require consistent performance. Missing these targets degrades user experience and system reliability.

### III. Class-Based State Machine Architecture

**All system logic MUST be implemented using Python classes with explicit state machines**:
- State transitions must be explicit and documented
- Each major component (camera, inference, UI) implemented as a class with clear state lifecycle
- State validation at each transition point
- No implicit state in global variables or module-level code

**Rationale**: Embedded systems require predictable behavior. Class-based state machines provide clear contracts, testability, and maintainability.

### IV. TensorRT Acceleration Mandatory

**YOLOv8-Pose inference MUST use TensorRT acceleration**:
- PyTorch/ONNX models must be converted to TensorRT engines during setup
- FP16 precision required for performance (FP32 only if accuracy demands)
- Engine serialization and caching for fast startup
- NO fallback to CPU or non-accelerated inference in production

**Rationale**: Without TensorRT, the performance requirements cannot be met on Jetson hardware. This is a hard technical constraint.

### V. On-Device Inference Only

**All model inference MUST execute on-device with zero external dependencies**:
- No cloud API calls for inference
- No network dependencies for core functionality
- Models must be bundled or downloadable once during setup
- System must function in fully offline/air-gapped environments

**Rationale**: Embedded deployment scenarios often lack reliable network connectivity. External dependencies introduce latency, cost, and single points of failure.

### VI. Minimal PyGame Interface

**The PyGame UI MUST be simple, intuitive, and performance-conscious**:
- Frame rendering overhead: **<5ms** per frame
- Clear visual hierarchy with minimal UI elements
- Direct frame buffer manipulation where possible (avoid excessive blitting)
- Keyboard/mouse input handling must not block main loop
- Display should reflect system state clearly (FPS counter, inference time, errors)

**Rationale**: Complex UIs consume CPU/GPU resources needed for inference. A minimal interface keeps the focus on real-time performance.

## Hardware & Deployment Standards

### Target Platform Requirements

- **Hardware**: NVIDIA Jetson Orin Nano (6GB or 8GB variants)
- **OS**: JetPack 5.x or later (Ubuntu 20.04+ based)
- **CUDA**: 11.4+ with cuDNN 8.6+
- **TensorRT**: 8.5+
- **Python**: 3.8-3.10 (JetPack compatibility range)

### Model Requirements

- **Primary Model**: YOLOv8-Pose (nano or small variant)
- **Input Resolution**: 640x640 or 640x480 (configurable)
- **Batch Size**: 1 (real-time processing)
- **Precision**: FP16 TensorRT engines

### Camera Requirements

- **Interface**: CSI (preferred) or USB (fallback)
- **Resolution**: 1280x720 or 1920x1080
- **Format**: MJPEG, YUYV, or raw Bayer (CSI)
- **Driver**: GStreamer or V4L2

## Development Standards

### Code Quality Gates

1. **Performance Profiling**: Every PR touching inference or capture pipeline must include profiling data (FPS, latency, memory)
2. **State Machine Validation**: Class state transitions must be documented in docstrings and validated in tests
3. **Resource Cleanup**: All GPU resources (CUDA streams, TensorRT contexts) must have explicit lifecycle management
4. **Error Handling**: Hardware errors (camera disconnect, GPU OOM) must be handled gracefully with clear user feedback

### Testing Requirements

- **Unit Tests**: Class state machines and individual components
- **Integration Tests**: Camera → Inference → UI pipeline
- **Performance Tests**: FPS benchmarks and latency measurements
- **Hardware Tests**: Actual Jetson device (CI/CD on target platform)

### Documentation Standards

- **Setup Guide**: Step-by-step Jetson environment setup
- **Architecture Diagram**: State machine and data flow visualization
- **Performance Baselines**: Expected FPS/latency for each hardware variant
- **Troubleshooting**: Common Jetson issues (CUDA OOM, camera permissions, etc.)

## Governance

This constitution supersedes all other development practices and guidelines. All code reviews, planning documents, and feature specifications must verify compliance with these principles.

**Amendment Process**:
1. Proposed changes must be documented with rationale
2. Impact analysis on existing code and architecture required
3. Team consensus or maintainer approval
4. Version bump according to semantic versioning rules

**Compliance Review**:
- Every feature specification must include "Constitution Check" section
- Implementation plans must map requirements to constitutional principles
- PR reviews must verify principle adherence (especially performance and TensorRT usage)

**Version**: 1.0.0 | **Ratified**: 2025-12-19 | **Last Amended**: 2025-12-19
