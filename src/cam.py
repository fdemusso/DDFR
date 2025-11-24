import cv2

class VideoCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()