"""
This function starts and runs the camera web server


"""
from flask import Flask, render_template, Response, jsonify
import cv2 as cv
from logging import error
from flask_cors import CORS
import logging
from logging import info
import sys
import threading
import signal

app = Flask(__name__)
# Enable CORS
CORS(app)

# Flag, if true -> Start and run camera stream
enableCameraStream = True

# Flag to control the camera stream and server shutdown
enableCameraStream = True
stop_server = threading.Event()


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


@app.route('/shutdown', methods=['POST'])
def shutdown():
  """Endpoint to stop the server."""
  stop_server.set()  # Signal the server to stop
  return jsonify({"message": "Server is shutting down..."}), 200


def run_server():
  # Start video streaming server
  app.run(host='127.0.0.1',
          port=5000,
          debug=False,
          use_reloader=False,
          threaded=True)


def start_camera_stream():
  server_thread = threading.Thread(target=run_server)
  server_thread.start()

  return server_thread


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  server_thread = start_camera_stream()

  def handle_shutdown(signal, frame):
    info('Shutdown signal received.')
    stop_server.set()
    server_thread.join()  # Ensure the server thread has finished
    sys.exit(0)

  signal.signal(signal.SIGINT, handle_shutdown)  # Handle Ctrl+C
  signal.signal(signal.SIGTERM, handle_shutdown)  # Handle termination signals

  # Wait for the server thread to finish
  server_thread.join()
