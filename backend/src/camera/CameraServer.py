"""[Inventory] Camera Server

Uses OpenCV to get a video stream from a connected webcam and flask to host the
video stream.

For debugging run as a module with

$ uv run -m backend.src.camera.CameraServer

"""

from pyzbar.pyzbar import decode
from flask_cors import CORS
from flask import Flask, Response, jsonify
import cv2 as cv
from logging import warning, error, info, debug
import asyncio
import requests
from typing import Tuple
from time import time
import numpy as np
import pygame
import threading

from .qr_config import qr_id_iden_str, qr_iden_str, qr_msg_delimiter
from .camera_config import (
  camera_server_ip,
  camera_server_port,
  DEFAULT_INVENTORY_HOST,
  DEFAULT_INVENTORY_PORT,
)


class CameraServer:
  """
  Class to use Flask to host a camera web server. This web stream is used
  to:
     * Scan item QR codes
     * Take images of each inventory item to be stored in the database

  """

  def __init__(
    self,
    enable_qr_scanner: bool = True,
    suspend_scan_dur_thr_s: float = 3.0,
    camera_index: int = 1,
  ):
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
    CORS(self.app, supports_credentials=True)

    self.camera_index = camera_index

    # Flag if True the QR scanning function of this server is enabled
    self.enable_qr_scanner = enable_qr_scanner

    # Flag if True QR scanning is disabled temporarily
    self.is_suspend_qr_scan = False

    # Counter to track the time spend while QR scanning is disabled
    self.time_qr_suspended_s = 0

    # Threshold for the maximum time QR scanning is disabled after a successful
    # scan
    self.suspend_scan_dur_thr_s = suspend_scan_dur_thr_s

    # Define routes inside the constructor
    self.app.add_url_rule("/", "video_feed", self.video_feed)
    self.configure_routes()

  def play_beep(self):
    """Play a beep sound (when a QR code is scanned successfully)"""
    pygame.mixer.music.load("beep.wav")

    def _play():
      pygame.mixer.music.play()

    threading.Thread(target=_play, daemon=True).start()

  def play_shutter_sound(self):
    """Play a beep sound (when a QR code is scanned successfully)"""
    pygame.mixer.music.load("camera_shutter.wav")

    def _play():
      pygame.mixer.music.play()

    threading.Thread(target=_play, daemon=True).start()

  def detect_and_decode_qr_marker(self, frame, enableQrText: bool = False):
    """Detect and decode one or several QR code messages within a given image.

    This functions uses pyzbar for detection and decoding

    Args:
        frame (np.ndarray): Camaera image
        enableQrText (bool, optional): Enable drawing QR payload in output image.
            Defaults to False (For debugging only)

    """
    # ---------------------------------------------------------------------
    # ----- Decode QR message with Pyzbar
    # ---------------------------------------------------------------------
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
      if enableQrText:
        frame = cv.putText(
          frame,
          decoded_text,
          (d.rect.left, d.rect.top + d.rect.height),
          cv.FONT_HERSHEY_SIMPLEX,
          0.6,
          (0, 0, 255),
          1,
          cv.LINE_AA,
        )

    return frame, qr_marker_found, num_markers, decoded_list

  def decode_id_from_qr_message(self, msg: str):
    """
    Decode QR message and retrieve item ID

    Expected message format:
    <qr_iden_str> <qr_msg_delimiter> <qr_id_iden_str> <qr_msg_delimiter> <ITEM_ID>

    """
    is_msg_valid = False
    item_id = -1

    # First check if all substring identifier are contained in the message
    if qr_iden_str in msg and qr_id_iden_str in msg and qr_msg_delimiter in msg:
      try:
        # Remove all identifier strings and convert to integer
        # Step 1: Split the test_str using the delimiter
        parts = msg.split(qr_msg_delimiter)

        # Step 2: Retrieve the ID message
        id_str = parts[-1]

        if id_str:
          # Step 3: Convert the remaining part to an integer
          item_id = int(id_str)
          is_msg_valid = True
      except:
        warning("Parsing QR code message failed. ")

    return is_msg_valid, item_id

  def send_image(self, image_bytes) -> Tuple[bool, str]:
    """Send image capture to inventory server"""
    files = {"file": ("camera_frame.png", image_bytes, "image/png")}
    url = f"http://{DEFAULT_INVENTORY_HOST}:{DEFAULT_INVENTORY_PORT}/store_media_image"
    try:
      response = requests.post(url, files=files)
      # raise exception for HTTP errors
      response.raise_for_status()
      # parse JSON response from the inventory server
      data = response.json()

      # Extract values
      success = data.get("status") == "success"
      image_hash = data.get("hash", "")

      print(f"Success: {success}, Hash: {image_hash}")
      return True, image_hash

    except requests.exceptions.RequestException as e:
      print(f"Error sending image: {e}")
      return False, ""
    except ValueError:
      # JSON decoding failed
      print("Invalid JSON response from server.")
      return False, ""

  def configure_routes(self):
    @self.app.route("/capture_image", methods=["POST"])
    def capture_image():
      """Serve requested image from the media directory"""
      try:
        self.play_shutter_sound()
      except:
        info('Failed to play sound: camera shutter')
      _, buffer = cv.imencode(".jpg", self.frame)
      frame_bytes = buffer.tobytes()

      # Send captured frame to inventory server to save it in media vault
      ret, hash_hex = self.send_image(frame_bytes)

      if ret:
        return jsonify(hash_hex)
      else:
        return {"error": "Failed to save image"}, 500

  def start_video_stream(self):
    """Launch video streaming"""
    # Create OpenCV VideoCapture instance for webcam at port 0
    camera = cv.VideoCapture(int(self.camera_index))
    while True:
      # Get a time marker for the start of this loop
      now = time()

      # Capture frame from the camera
      success, self.frame = camera.read()

      if not success:
        error("Failed to conntect to camera.")
        break
      else:
        # Compile frame for output stream
        _, buffer = cv.imencode(".jpg", self.frame)
        frame_bytes = buffer.tobytes()

        if self.enable_qr_scanner:
          if self.is_suspend_qr_scan:
            # Increment timer to track the time since this function is disabled
            self.time_qr_suspended_s += time() - now
            # If threshold is reached -> lift suspension
            if self.time_qr_suspended_s > self.suspend_scan_dur_thr_s:
              self.is_suspend_qr_scan = False
          else:
            self.time_qr_suspended_s = 0
            try:
              # Detect and mark QR markers in frame
              (self.frame, _, num_markers, decoded_list) = (
                self.detect_and_decode_qr_marker(self.frame)
              )

              # Process detected markers and notify the inventory server
              id_valid, item_id = self.handle_qr_marker_list(num_markers, decoded_list)
            except:
              warning(f"Detecting QR marker failed for this frame {self.frame.shape}")
              id_valid = False

            # If a valid marker has been scanned successfully -> Suspend further
            # scanning for self.suspend_scan_dur_thr_s seconds to avoid scanning the
            # same item over and over again.
            if id_valid:
              info(
                f"Marker detection (ID = {item_id}). Suspend QR scanning for {self.suspend_scan_dur_thr_s} seconds ... "
              )
              self.is_suspend_qr_scan = True

        yield (
          b"--frame\r\n"
          # concat frame one by one and show result
          b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

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
      is_valid, item_id = self.decode_id_from_qr_message(decoded_list[0])

      # Check validity of the decoded item ID
      if is_valid:
        debug(f"[+--] Valid QR marker detected -> {item_id}")

        # Play sound to indicate a successful scan
        try:
          self.play_beep()
        except:
          info('Failed to play sound: beep')

        # Set inventory server url
        inventory_server_url = (
          f"http://{DEFAULT_INVENTORY_HOST}:{DEFAULT_INVENTORY_PORT}/qr"
        )
        # Set request payload
        payload = {"id": f"{item_id}"}
        # Send request to inventory server
        _ = requests.post(inventory_server_url, json=payload)

        return True, item_id
      else:
        info(f"Decoded message invalid {decoded_list[0]} -> {item_id}")

    elif num_markers > 1:
      warning(
        f"Multiple ({num_markers}) QR marker detected within the image. Aborting compiling the decoded message."
      )
    else:
      # If list is empty -> do nothing
      pass
    return False, -1

  def video_feed(self):
    """
    Video streaming route. Put this in the src attribute of an img tag
    """
    return Response(
      self.start_video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

  async def run(self, host: str = camera_server_ip, port: int = camera_server_port):
    """
    Start the camera server
    """

    # Start video streaming server
    def start_flask():
      self.app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

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
  loop.run_until_complete(asyncio.gather(server.run()))
