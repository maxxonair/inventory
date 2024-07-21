"""
This function starts and runs the camera web server


"""
from flask import Flask, render_template, Response
import cv2 as cv
from logging import error
import logging

app = Flask(__name__)

# Flag, if true -> Start and run camera stream
enableCameraStream = True


def generateFrameByFrame():
  if enableCameraStream:
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
        frame = cv.rotate(frame, cv.ROTATE_180)

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


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  app.run(debug=True)
