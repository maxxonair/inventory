from flask_cors import CORS
from flask import Flask, Response
import cv2 as cv
from logging import warning, error, info, debug
import numpy as np
import os
import sys
import asyncio

from frontend import FrontendApplication
from backend import (decode_id_from_qr_message,
                     camera_server_ip,
                     camera_server_port)

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

  def __init__(self, fnct_update_id):
    # Enable/Disable displaying the QR message in the streamed image
    self.enableQrText = False

    self.app = Flask(__name__)
    # Enable CORS
    CORS(self.app)

    # Initialize array to store last captured frame to black image
    self.captured_frame = np.zeros((512, 512), dtype=int)

    self.fnct_update_id = fnct_update_id

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
        # Save the most recent valid frame without marker drawings
        self.captured_frame = frame
        # Detect and mark QR markers in frame
        (frame,
         _,
         num_markers,
         decoded_list) = detect_and_decode_qr_marker(frame)

        # Process detected markers and notify UI
        self.handle_marker_list(num_markers, decoded_list)

        # Compile frame for output stream
        ret, buffer = cv.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               # concat frame one by one and show result
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

  def handle_marker_list(self, num_markers, decoded_list):
    """
    Function to handle the list of processed QR markers:
    * Check if more than one marker is detected
    * Decode message from detected marker
    * Check message validity
    * Update UI with detected marker

    """
    # Only use the decoded messages if one and only one marker is detected
    # within the image
    if num_markers == 1:

      # Decode the QR message
      is_valid, item_id = decode_id_from_qr_message(decoded_list[0])

      # Check validity of the decoded item ID
      if is_valid:
        debug(f'[+--] Valid QR marker detected -> {item_id}')

        # Way-around the not working direct communication between the
        # camera server and UI server. -> Write message to file and
        # detect/read the message using watchdog
        with open("./temp/qr", "w") as text_file:
          text_file.write(f'{item_id}')

      else:
        info(f'Decoded message invalid {decoded_list[0]} -> {item_id}')

    elif num_markers > 1:
      warning(
          f'Multiple ({num_markers}) QR marker detected within the image. Aborting compiling the decoded message.')
    else:
      # If list is empty -> do nothing
      pass

  def video_feed(self):
    """
    Video streaming route. Put this in the src attribute of an img tag
    """
    return Response(self.generate_frame_by_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

  async def run(self,
                host: str = camera_server_ip,
                port: int = camera_server_port):
    """
    Start the camera server
    """
    # Start video streaming server
    def start_flask():
      self.app.run(host=host,
                   port=port,
                   debug=False,
                   use_reloader=False,
                   threaded=True)

    # Run the Flask app in a separate thread and return it as an asyncio
    # task
    return await asyncio.to_thread(start_flask)

  def get_last_frame(self):
    """
    Returns the last captured frame as a numpy array. 

    This function is inteded to be used by the UI to capture inventory 
    item images for the database.
    """
    return np.array(self.captured_frame)


if __name__ == "__main__":
  server = CameraServer()

  server.run()
