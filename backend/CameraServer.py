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
from typing import Tuple
from time import time
import hashlib

from backend import (decode_id_from_qr_message,
                     camera_server_ip,
                     camera_server_port)

from backend.util import detect_and_decode_qr_marker
from backend.inventory_server_config import inventory_server_ip, inventory_server_port
from backend.camera_config import media_file_path


class CameraServer():
  """
  Class to use Flask to host a camera web server. This web stream is used
  to:
     * Scan item QR codes
     * Take images of each inventory item to be stored in the database

  """

  def __init__(self, enable_qr_scanner: bool = True, suspend_scan_dur_thr_s: float = 3.0):
    """Initialise server instance 

    Args:
        enable_qr_scanner (bool, optional): Enable QR scanning function. 
            Defaults to True.
        suspend_scan_dur_thr_s (float, optional): Time QR scanning will be suspended 
            for after a valid code has been scanned. 
            Defaults to 3.0 seconds
    """
    # Enable/Disable displaying the QR message in the streamed image
    self.enableQrText = False

    self.app = Flask(__name__)
    # Enable CORS
    CORS(self.app)
    
    # Flag if True the QR scanning function of this server is enabled
    self.enable_qr_scanner = enable_qr_scanner
    
    # Flag if True QR scanning is disabled temporarily
    self.is_suspend_qr_scan = False
    
    # Counter to track the time spend while QR scanning is disabled
    self.time_qr_suspended_s = 0
    
    # Threshold for the maximum time QR scanning is disabled after a successful 
    # scan
    self.suspend_scan_dur_thr_s = suspend_scan_dur_thr_s
    
    self.frame = []

    # Define routes inside the constructor
    self.app.add_url_rule('/', 'video_feed', self.video_feed)
    self.configure_routes()
    
  def configure_routes(self):

    @self.app.route('/capture_image', methods=['GET'])
    def capture_image():
      """Serve requested image from the media directory
      """
      # Create a hex hash based on the frame data
      cam_img_bytes = self.frame.tobytes()
      hash_object = hashlib.sha256(cam_img_bytes)
      hash_hex = hash_object.hexdigest()

      img_path = Path(media_file_path) / f'{hash_hex}.png'

      # Save image to file
      cv.imwrite(img_path, self.display_img)
      return jsonify(hash_hex)
    
  def start_video_stream(self):
    """Launch video streaming
    """
    # Create OpenCV VideoCapture instance for webcam at port 0
    camera = cv.VideoCapture(0)
    while True:
      # Get a time marker for the start of this loop
      now = time()
      
      # Capture frame from the camera
      success, frame = camera.read()

      if not success:
        error('Failed to conntect to camera.')
        break
      else:
        # Compile frame for output stream
        _, buffer = cv.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Save recent frame for image capture function
        self.frame = frame
        
        if self.enable_qr_scanner:
          if self.is_suspend_qr_scan:
            # Increment timer to track the time since this function is disabled
            self.time_qr_suspended_s += (time() - now)
            # If threshold is reached -> lift suspension
            if self.time_qr_suspended_s > self.suspend_scan_dur_thr_s:
              self.is_suspend_qr_scan = False
          else:
            self.time_qr_suspended_s = 0
            try:
              # Detect and mark QR markers in frame
              (frame,
              _,
              num_markers,
              decoded_list) = detect_and_decode_qr_marker(frame)

              # Process detected markers and notify the inventory server
              id_valid, item_id  = self.handle_qr_marker_list(num_markers, decoded_list)
            except:
              warning('Detecting QR marker failed for this frame {frame.shape}')
              id_valid = False
            
            # If a valid marker has been scanned successfully -> Suspend further
            # scanning for self.suspend_scan_dur_thr_s seconds to avoid scanning the 
            # same item over and over again.
            if id_valid:
              info(f'Marker detection (ID = {item_id}). Suspend QR scanning for {self.suspend_scan_dur_thr_s} seconds ... ')
              self.is_suspend_qr_scan = True

        yield (b'--frame\r\n'
               # concat frame one by one and show result
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

  def handle_qr_marker_list(self, num_markers, decoded_list) -> Tuple[bool, int]:
    """Process the decoded list of QR markers in the image
    
    Function to handle the list of processed QR markers:
    * Check if more than one marker is detected
    * Decode message from detected marker
    * Check message validity
    * Send POST request to the Inventory Server /qr containing the scanner id

    Args:
        num_markers (int): Number of markers found
        decoded_list (list[str]): List of decoded marker payloads

    Returns:
        bool: Flag if True scanned marker is valid
        int: Retrieved item ID corresponding to the scanned QR marker
    """
    # Only use the decoded messages if one and only one marker is detected
    # within the image
    if num_markers == 1:

      # Retrieve the inventory ID from the the QR message payload
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
        
        return True, item_id
      else:
        info(f'Decoded message invalid {decoded_list[0]} -> {item_id}')

    elif num_markers > 1:
      warning(
          f'Multiple ({num_markers}) QR marker detected within the image. Aborting compiling the decoded message.')
    else:
      # If list is empty -> do nothing
      pass
    return False, -1

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
