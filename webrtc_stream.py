import json
from aiohttp import web
from aiortc import RTCPeerConnection, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaRelay
from picamera2 import Picamera2
import av
import threading
import time

# Start camera
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (1280, 720)},
    encode="h264"
)
picam2.configure(config)
picam2.start()

# Shared frame buffer
current_frame = None
frame_lock = threading.Lock()

# Background camera capture to memory
def capture_frames():
    global current_frame
    while True:
        with frame_lock:
            current_frame = picam2.capture_buffer("main")  # returns H.264 encoded buffer
        time.sleep(0.01)

threading.Thread(target=capture_frames, daemon=True).start()


# Track that feeds frames into WebRTC
class CameraTrack(VideoStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        with frame_lock:
            data = current_frame

        # Decode H264 into a frame for WebRTC
        packet = av.Packet(data)
        frame = None
        for f in av.codec.CodecContext.create("h264", "r").decode(packet):
            frame = f
            break

        frame.pts = pts
        frame.time_base = time_base
        return frame


pcs = set()
routes = web.RouteTableDef()


@routes.post("/offer")
async def offer(request):
    params = await request.json()

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    def on_ice_change():
        if pc.iceConnectionState == "failed":
            pc.close()
            pcs.discard(pc)

    # Add video track
    pc.addTrack(CameraTrack())

    # Handle offer
    await pc.setRemoteDescription(params['offer'])
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({"answer": pc.localDescription})
    )


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=5001)
