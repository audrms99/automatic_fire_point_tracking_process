'''
raps#1(camera) 에서 돌아가는 코드
'''

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import controls
import io
import logging
import socketserver
from http import server
import time
import threading

PAGE = """\
<html>
<head>
<title>picamera2 demo</title>
<style>
    .container {
        position: relative;
        display: inline-block;
    }
    #coordinates {
        margin-top: 10px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 5px;
        border-radius: 3px;
        display: inline-block;
    }
</style>
</head>
<body>
<h1>Picamera2 Streaming Demo</h1>
<div class="container">
    <img src="stream.mjpg" width="640" height="480" id="stream" />
</div>
<div id="coordinates">X: 0, Y: 0</div>

<script>
    const img = document.getElementById('stream');
    const coords = document.getElementById('coordinates');
    
    img.addEventListener('mousemove', function(e) {
        const rect = img.getBoundingClientRect();
        const x = Math.round(e.clientX - rect.left);
        const y = Math.round(e.clientY - rect.top);
        coords.textContent = `X: ${x}, Y: ${y}`;
    });
    
    img.addEventListener('mouseleave', function() {
        coords.textContent = 'X: 0, Y: 0';
    });
</script>
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# 카메라 초기화
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

picam2.set_controls({'AfMode': 2})  # 2는 연속 초점 (Continuous Autofocus)

'''
# 센서 크기 가져오기
sensor_w = 1920
sensor_h = 1080
zoom = 2.0  # 2배 줌

# 줌을 위한 크롭 계산
crop_w = int(sensor_w / zoom)
crop_h = int(sensor_h / zoom)
crop_x = int((sensor_w - crop_w) / 2)
crop_y = int((sensor_h - crop_h) / 2)

# 줌 설정
picam2.set_controls({"ScalerCrop": (crop_x, crop_y, crop_w, crop_h)})
'''

output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 8000)  # 모든 인터페이스에서 8000번 포트로 접근 가능
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
