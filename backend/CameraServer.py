from flask_cors import CORS
from flask import Flask, Response, render_template
from multiprocessing import Manager
import cv2 as cv
from logging import warning, error
import numpy as np
import os
import sys

# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from backend.util import detect_and_decode_qr_marker


class CameraServer():
  """
  Class to use Flask to host a camera web server. This web stream is used
  to:
     * Scan item QR codes
     * Take images of each inventory item to be stored in the database

  """

  def __init__(self):
    # Enable/Disable displaying the QR message in the streamed image
    self.enableQrText = False

    self.app = Flask(__name__)
    # Enable CORS
    CORS(self.app)

    self.manager = Manager()
    self.qr_message = self.manager.Value('d', '')

    self.image_manager = Manager()
    self.captured_frame = self.image_manager.Value('d', '')

    # Define routes inside the constructor
    self.app.add_url_rule('/', 'video_feed', self.video_feed)

  def generate_frame_by_frame(self):
    # Create OpenCV VideoCapture instance for webcam at port 0
    camera = cv.VideoCapture(0)
    while True:
      # Capture frame-by-frame
      success, frame = camera.read()
      if not success:
        error('Failed to conntect to camera.')
        break
      else:

        (frame,
         _,
         num_markers,
         decoded_list) = detect_and_decode_qr_marker(frame)

        # self.captured_frame.value = frame

        # Only use the decoded messages if one and only one marker is detected
        # within the image
        if num_markers > 1:
          warning(
              f'Multiple ({num_markers}) QR marker detected within the image. Aborting compiling the decoded message.')

        if num_markers == 1:
          # Valid detection -> Single QR marker found
          TODO = True  # Add function back
          # self.qr_message.value = str(decoded_list[0])

        ret, buffer = cv.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               # concat frame one by one and show result
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

  def video_feed(self):
    """
    Video streaming route. Put this in the src attribute of an img tag
    """
    return Response(self.generate_frame_by_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

  def run(self, host: str = '127.0.0.1', port: int = 5000):
    """
    Start the camera server
    """
    # Start video streaming server
    self.app.run(host=host,
                 port=port,
                 debug=False,
                 use_reloader=False,
                 threaded=True)

  def get_last_frame(self):
    return np.array(self.captured_frame.value)

  def get_qr_message(self):
    return str(self.qr_message.value)


if __name__ == "__main__":
  server = CameraServer()

  server.run()
