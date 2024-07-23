"""
This function starts and runs the camera web server


"""
from flask import Flask, render_template, Response, jsonify
import cv2 as cv
from qreader import QReader
from logging import error, info
from flask_cors import CORS
import logging

app = Flask(__name__)
# Enable CORS
CORS(app)

marker_found = False


def generateFrameByFrame():
  # Create OpenCV VideoCapture instance for webcam at port 0
  camera = cv.VideoCapture(0)
  while True:
    # Capture frame-by-frame
    success, frame = camera.read()
    if not success:
      error('Failed to conntect to camera.')
      break
    else:
      # Rotate by 180 degree to compensate for how the camera is mounted
      # inside the housing
      # frame = cv.rotate(frame, cv.ROTATE_180)

      # successFlag, decoded_info, frame = detect_qr_marker(frame)
      # if not marker_found:
      #   frame = detect_qr_marker(frame)

      # numCodes = len(decoded_info)
      # if numCodes == 1 and successFlag:
      #   info(f'Message: {decoded_info[0]}')

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


def detect_qr_marker(frame):
  """
  Detect and decode a or several QR codes within the image


  """
  qreader = QReader()
  image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
  decoded_text = qreader.detect_and_decode(image=image)

  # # Create QR code detector
  # qcd = cv.QRCodeDetector()

  # # Run detection and decoding on the frame
  # (successFlag,
  #  decoded_info,
  #  points,
  #  straight_qrcode) = qcd.detectAndDecodeMulti(frame)

  # # If detection is successful -> draw detection on frame
  # if successFlag:
  #   frame = cv.polylines(frame, points.astype(int), True, (0, 255, 0), 3)

  #   for info_text, p in zip(decoded_info, points):
  #     corner_point = p[0].astype(int)
  #     # TODO check boundaries before doing this
  #     corner_point[0] -= 25
  #     frame = cv.putText(frame, info_text, corner_point,
  #                        cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

  frame = cv.putText(frame, str(decoded_text), (20, 20),
                     cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

  return frame


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
