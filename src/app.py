from flask import Flask, Response, render_template
from cam import VideoCamera

app = Flask(__name__)
cam = VideoCamera()

def gen(camera):
    while True:
        frame = cam.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
@app.route('/video_feed')
def video_feed():
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')