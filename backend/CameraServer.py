"""                 [Inventory] Camera Server 

Uses OpenCV to get a video stream from a connected webcam and flask to host the 
video stream.

For debugging run as a module with 

$ uv run -m backend.CameraServer

"""

from flask_cors import CORS
from flask import Flask, Response
import cv2 as cv
from logging import warning, error, info, debug
import asyncio
import requests

from backend import (decode_id_from_qr_message,
                     camera_server_ip,
                     camera_server_port)

from backend.util import detect_and_decode_qr_marker
from backend.inventory_server_config import inventory_server_ip, inventory_server_port


class CameraServer():
  """
  Class to use Flask to host a camera web server. This web stream is used
  to:
     * Scan item QR codes
     * Take images of each inventory item to be stored in the database

  """

  def __init__(self, enable_qr_scanner: bool = True):
    # Enable/Disable displaying the QR message in the streamed image
    self.enableQrText = False

    self.app = Flask(__name__)
    # Enable CORS
    CORS(self.app)
    
    self.enable_qr_scanner = enable_qr_scanner

    # Define routes inside the constructor
    self.app.add_url_rule('/', 'video_feed', self.video_feed)

  def start_video_stream(self):
    # Create OpenCV VideoCapture instance for webcam at port 0
    camera = cv.VideoCapture(0)
    while True:
      # Capture frame-by-frame
      success, frame = camera.read()

      if not success:
        error('Failed to conntect to camera.')
        break
      else:
        if self.enable_qr_scanner:
          # Detect and mark QR markers in frame
          (frame,
          _,
          num_markers,
          decoded_list) = detect_and_decode_qr_marker(frame)

          # Process detected markers and notify the inventory server
          self.handle_qr_marker_list(num_markers, decoded_list)

        # Compile frame for output stream
        _, buffer = cv.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               # concat frame one by one and show result
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

  def handle_qr_marker_list(self, num_markers, decoded_list):
    """
    Function to handle the list of processed QR markers:
    * Check if more than one marker is detected
    * Decode message from detected marker
    * Check message validity
    * Send POST request to the Inventory Server /qr containing the scanner id

    """
    # Only use the decoded messages if one and only one marker is detected
    # within the image
    if num_markers == 1:

      # Decode the QR message
      is_valid, item_id = decode_id_from_qr_message(decoded_list[0])

      # Check validity of the decoded item ID
      if is_valid:
        debug(f'[+--] Valid QR marker detected -> {item_id}')
        # Set inventory server url
        inventory_server_url = f'http://{inventory_server_ip}:{inventory_server_port}/qr'
        # Set request payload
        payload = {'id': f'{item_id}'}
        # Send request to inventory server
        _ = requests.post(inventory_server_url, json=payload)
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
    return Response(self.start_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

  async def stop(self):
      info("Stopping CameraServer...")

if __name__ == "__main__":
  """Allows to call this module directly
  """
  server = CameraServer()
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(asyncio.gather(
      server.run()))
