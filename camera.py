from picamera2 import Picamera2
import io

CAM_RES = 1280, 720

picam = Picamera2()

config = picam.create_video_configuration(
    main={"size": CAM_RES, "format": "RGB888"}
)
picam.configure(config)
picam.start()

def get_frame():
    """Returns one JPEG-encoded frame (bytes)."""
    buffer = io.BytesIO()
    picam.capture_file(buffer, format="jpeg")
    return buffer.getvalue()