"""GStreamer pipeline utilities for Jetson CSI cameras."""

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    """
    Return a GStreamer pipeline string for capturing from the CSI camera.
    
    Args:
        sensor_id: The ID of the camera sensor (default 0)
        capture_width: The width of the captured image
        capture_height: The height of the captured image
        display_width: The width of the displayed image
        display_height: The height of the displayed image
        framerate: The framerate of the captured video
        flip_method: The flip method (0=none, 2=rotate 180)
    
    Returns:
        A GStreamer pipeline string.
    """
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! "
        "appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
