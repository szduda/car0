import threading
import time

from aiohttp import web
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from aiortc.codecs.h264 import H264Frame

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import Output

# Custom output class for H264Encoder
class InMemoryOutput(Output):
    def __init__(self):
        super().__init__()
        self.buffer = b""
        self.lock = threading.Lock()

    def write(self, buf):
        # Picamera2 will call this with encoded H264 data (NAL units)
        with self.lock:
            self.buffer += buf

    def read(self):
        # Return and clear the buffer
        with self.lock:
            data = self.buffer
            self.buffer = b""
        return data

# Setup camera
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720)}, encode="h264")
picam2.configure(video_config)

output = InMemoryOutput()
encoder = H264Encoder()

picam2.start_recording(encoder, output)
picam2.start()

# Shared frame buffer
current_nal = b""
nal_lock = threading.Lock()

# Thread: constantly read from encoder output
def reader_thread():
    global current_nal
    while True:
        data = output.read()
        if data:
            with nal_lock:
                current_nal = data
        time.sleep(0.01)

threading.Thread(target=reader_thread, daemon=True).start()

# WebRTC VideoTrack
class CameraTrack(VideoStreamTrack):
    kind = "video"

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        with nal_lock:
            nal = current_nal
        # Wrap into H264Frame for aiortc
        frame = H264Frame(nal)
        frame.pts = pts
        frame.time_base = time_base
        return frame

pcs = set()
routes = web.RouteTableDef()

@routes.post("/offer")
async def offer(request):
    params = await request.json()
    desc = params["offer"]
    _offer = RTCSessionDescription(sdp=desc["sdp"], type=desc["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    def on_ice():
        print("ICE state:", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            pcs.discard(pc)
            pc.close()

    pc.addTrack(CameraTrack())

    await pc.setRemoteDescription(_offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "answer": {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
    })

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=5001)
