"""
This function starts and runs the camera web server


"""
from flask import Flask, render_template, Response, jsonify
import cv2 as cv
import numpy as np
from logging import error, info, warning
from flask_cors import CORS
import logging

# QR code reader
from pyzbar.pyzbar import decode
from multiprocessing import Manager


class CameraServer():

  def __init__(self):
    # Enable/Disable displaying the QR message in the streamed image
    self.enableQrText = False

    self.app = Flask(__name__)
    # Enable CORS
    CORS(self.app)
    self.manager = Manager()
    self.decoded_message = self.manager.Value('d', '')
    # Define routes inside the constructor
    self.app.add_url_rule('/', 'index', self.index)
    self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)

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
         decoded_list) = self.detect_and_decode_qr_marker(frame)

        # Only use the decoded messages if one and only one marker is detected
        # within the image
        if num_markers > 1:
          warning(
              f'Multiple ({num_markers}) QR marker detected within the image. Aborting compiling the decoded message.')
          self.decoded_message.value = ''
        if num_markers == 1:
          self.decoded_message.value = str(decoded_list[0])
        else:
          # Case: No markers found
          self.decoded_message.value = ''

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

  def index(self):
    """Video streaming home page."""
    return render_template('index.html')

  def run(self):
    """
    Start the camera server
    """
    # Start video streaming server
    self.app.run(host='127.0.0.1',
                 port=5000,
                 debug=False,
                 use_reloader=False,
                 threaded=True)

  def get_decoded_msg(self) -> str:
    return str(self.decoded_message.value)
  # ------------------------------------------------------------------------
  #                 [IMAGE PROCESSING FUNCTIONS]
  # ------------------------------------------------------------------------

  def detect_and_decode_qr_marker(self, frame):
    """
    Detect and decode a or several QR codes within the image using pyzbar


    """
    # ---------------------------------------------------------------------
    # ----- Use Pyzbar
    # Initialize flag to track if a marker has been found
    qr_marker_found = False
    # Initialize counter to track the number of markers detected in the image
    num_markers = 0
    # Initialize a list to store all decoded messages
    decoded_list = []

    for d in decode(frame):
      qr_marker_found = True
      num_markers += 1
      decoded_text = str(d.data.decode())
      decoded_list.append(decoded_text)

      # Draw perimeter of the marker
      frame = cv.polylines(frame, [np.array(d.polygon)], True, (0, 255, 0), 2)
      # Draw marker text
      if self.enableQrText:
        frame = cv.putText(frame, decoded_text, (d.rect.left, d.rect.top + d.rect.height),
                           cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv.LINE_AA)

    return frame, qr_marker_found, num_markers, decoded_list

  # ------------------------------------------------------------------------


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  server = CameraServer()
  server.run()
