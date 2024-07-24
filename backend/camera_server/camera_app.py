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

# Global variable to store the decoded QR marker message
decoded_message = ''

app = Flask(__name__)
# Enable CORS
CORS(app)


def generateFrameByFrame():
  global decoded_message
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

      # Only use the decoded messages if one and only one marker is detected
      # within the image
      if num_markers > 1:
        warning(
            f'Multiple ({num_markers}) QR marker detected within the image. Aborting compiling the decoded message.')
        decoded_message = ''
      if num_markers == 1:
        decoded_message = str(decoded_list[0])
      else:
        # Case: No markers found
        # decoded_message = ''
        DoNothing = True

      ret, buffer = cv.imencode('.jpg', frame)
      frame = buffer.tobytes()
      yield (b'--frame\r\n'
             # concat frame one by one and show result
             b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
  # Video streaming route. Put this in the src attribute of an img tag
  return Response(generateFrameByFrame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
  """Video streaming home page."""
  return render_template('index.html')


def get_decoded_message():
  """
  Getter function to return the decoded message if any
  """
  info(f'message {decoded_message}')
  return decoded_message


def detect_and_decode_qr_marker(frame):
  """
  Detect and decode a or several QR codes within the image using pyzbar


  """
  # ------------------------------------------------------------------------
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
    frame = cv.putText(frame, decoded_text, (d.rect.left, d.rect.top + d.rect.height),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv.LINE_AA)

  return frame, qr_marker_found, num_markers, decoded_list


def run_camera_server():
  # Start video streaming server
  app.run(host='127.0.0.1',
          port=5000,
          debug=False,
          use_reloader=False,
          threaded=True)


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  run_camera_server()
