"""[Inventory] Inventory Server


Run this module manually from the projects backend directory with:

$ uv run -m src.InventoryServer

"""

from flask import Flask, request, jsonify, send_from_directory, session, Response
from flask_cors import CORS
from flask_session import Session
from logging import info, error, debug
from datetime import timedelta
from PIL import Image
import asyncio
import cv2 as cv
import json
import io
import requests
import numpy as np
import queue
import hashlib
from pathlib import Path

from server.InventoryUser import InventoryUser
from server.DataBaseClient import DataBaseClient

# Import printer server address
from server.inventory_server_config import PRINTER_SERVER_PORT, PRINTER_SERVER_IP

from server.inventory_server_config import (
  inventory_server_ip,
  inventory_server_port,
  MEDIA_DEFAULT_PATH,
  DEFAULT_DB_HOST,
  DEFAULT_DB_PORT
)


class InventoryServer:
  def __init__(
    self,
    db_host: str = DEFAULT_DB_HOST,
    db_port: int = DEFAULT_DB_PORT,
    media_path: str = MEDIA_DEFAULT_PATH,
    session_timeout_min: float = 60.0,
  ):
    """Create InventoryServer instance

    Args:
        db_host (str, optional): Database server IP. 
            Defaults to DEFAULT_DB_HOST.
        db_port (int, optional): Database server port. 
            Defaults to DEFAULT_DB_PORT.
        media_path (str, optional): Media storage file path. 
            Defaults to MEDIA_DEFAULT_PATH.
        session_timeout_min (float, optional): Session timeout for active user 
            sessions. Defaults to 60.0 minutes
    """
    self.app = Flask(__name__)
    self.app.secret_key = "super-secret"
    self.app.config["SESSION_TYPE"] = "filesystem"
    CORS(self.app, supports_credentials=True)  # Enable CORS
    Session(self.app)

    self.app.permanent_session_lifetime = timedelta(minutes=session_timeout_min)

    # Set path to load media files from
    self.media_path = media_path

    self.scanned_qr_id = None

    # Create a database client instance. The client will handle all interaction
    # with the database server.
    self.db = DataBaseClient(host=db_host, port=db_port)

    self.event_queue = queue.Queue()

    # Routes
    self.configure_routes()

  def configure_routes(self):
    """Configure Http routes for this server"""

    @self.app.route("/media/<filename>")
    def serve_image(filename):
      """Serve requested image from the media directory"""
      return send_from_directory(self.media_path, filename)

    @self.app.route("/checkout_item", methods=["POST"])
    def checkout_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.json
      self.db.update_inventory_item_checkout_status(
        int(data["itemId"]), session["user"], 1
      )
      return jsonify({"message": f"Item {data['itemId']} checked out"})

    @self.app.route("/return_item", methods=["POST"])
    def return_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.json
      self.db.update_inventory_item_checkout_status(
        int(data["itemId"]), session["user"], 0
      )
      return jsonify({"message": f"Item {data['itemId']} checked out"})

    @self.app.route("/items")
    def get_items():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = self.db.get_all_inventory_items_as_dict_list()
      return jsonify(data_dict)

    @self.app.route("/get_item", methods=["POST"])
    def get_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.json
      data_dict = self.db.get_inventory_item_as_dict(int(data["itemId"]))

      # TODO add callback funtion to check if item with ID exists in DB

      if data_dict is None:
        return jsonify({"error": "Item not found!"}), 401
      return jsonify(data_dict)

    @self.app.route("/image_upload", methods=["POST"])
    def upload_file():
      if "avatar" not in request.files:
        return {"error": "No file part"}, 400

      file = request.files["avatar"]

      if file.filename == "":
        return {"error": "No selected file"}, 400

      # Read file content into bytes
      file_bytes = file.read()

      # Hash the file bytes
      hash_object = hashlib.sha256(file_bytes)
      hash_hex = hash_object.hexdigest()

      # Convert bytes to NumPy array for OpenCV
      nparr = np.frombuffer(file_bytes, np.uint8)
      img_np = cv.imdecode(nparr, cv.IMREAD_COLOR)

      if img_np is None:
        return {"error": "Could not decode image"}, 400

      # Save image using OpenCV
      img_path = Path(MEDIA_DEFAULT_PATH) / f"{hash_hex}.png"
      success = cv.imwrite(str(img_path), img_np)

      if not success:
        return {"error": "Failed to save image"}, 500

      return {"message": "Image saved", "image": f"{hash_hex}"}

    @self.app.route("/login", methods=["POST"])
    def login():
      data = request.json
      is_user_exists, inventoryUser = self.db.get_inventory_user_as_object(
        data["username"]
      )
      print(f"Log in attempt: {data['username']} -> {is_user_exists}")
      if not is_user_exists:
        return jsonify({"error": "User not found"}), 401
      if not inventoryUser.is_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

      # Login valid -> Create a session cookie for this user
      session["user"] = data["username"]
      return jsonify({"message": "Login successful"})

    @self.app.route("/add_item", methods=["POST"])
    def add_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = request.json
      new_id = self.db.add_inventory_item(data_dict)
      return jsonify({"message": f"{new_id}"}), 200

    @self.app.route("/update_item", methods=["POST"])
    def update_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = request.json
      item_id = int(data_dict["id"])
      data_dict.pop("id")
      self.db.update_inventory_item(data_dict, item_id)
      return jsonify({"status": "item updated"}), 200

    @self.app.route("/logout", methods=["POST"])
    def logout():
      print("Log out user")
      session.clear()
      return jsonify({"message": "Logged out"})

    @self.app.route("/store_media_image", methods=["POST"])
    def store_media_image():
      file = request.files.get("file")
      if file:
        # Read the file bytes into memory
        file_bytes = file.read()

        # Compute SHA-256 hash
        hash_hex = hashlib.sha256(file_bytes).hexdigest()

        # Save the file to the media storage
        save_path = MEDIA_DEFAULT_PATH / f"{hash_hex}.png"
        # Convert binary data back to PIL image
        image = Image.open(io.BytesIO(file_bytes))
        image.save(save_path)

        return {
          "status": "success",
          "hash": hash_hex,
          "message": f"Saved to {save_path}",
        }, 200

      return {"status": "error", "message": "No file provided"}, 400

    @self.app.route("/capture_image", methods=["POST"])
    def capture_image():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      # TODO missing action

    @self.app.route("/print_label", methods=["POST"])
    def print_label():
      """Print item label"""
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.get_json()
      item_id = int(data.get("itemId"))
      print(f"Issue label for item with ID {item_id}")

      url = f"http://{PRINTER_SERVER_IP}:{PRINTER_SERVER_PORT}/print_label"
      data = {"itemId": item_id}

      response = requests.post(url, json=data)

      if response.status_code == 200:
        resp_json = response.json()
        if resp_json.get("status") == "success":
          print(f"Print command for item {item_id} succeeded.")
          return jsonify({"status": "success"}), 200
        else:
          print(f"Print command failed: {resp_json}")
          return {"error": "Failed to print label"}, 500
      else:
        print(
          f"Request failed with status code {response.status_code}: {response.text}"
        )
        return {"error": "Failed to print label"}, 500

    @self.app.route("/delete_item", methods=["POST"])
    def delete_item():
      """Remove item from inventory database"""
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.get_json()
      item_id = int(data.get("itemId"))
      print(f"Delete item with ID {item_id}")

      # Issue label print job
      self.db.delete_inventory_item(item_id)

      return jsonify({"status": "success"}), 200

    @self.app.route("/me")
    def me():
      # !TODO! somehow this returns 200 even if the user is logged out.
      # Safeguarded by the frontend for now, but needs to be checked.
      if "user" in session:
        return jsonify({"user": session["user"]})
      return jsonify({"error": "Not logged in"}), 401

    @self.app.route("/user_privilege", methods=["POST"])
    def user_privilege():
      """Return privilege level for a given user"""
      data = request.get_json()
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      # Load privilege level for this user
      print(f"Load privilege level for user {str(data.get('user'))}")
      try:
        user_dict = self.db.get_inventory_user_as_dict(str(data.get("user")))
        print(
          f"User {data.get('user')} authorized up to privilege level {user_dict['user_privileges']}"
        )
        return jsonify({"privilege": user_dict["user_privileges"]})
      except:
        return jsonify({"error": f"User: {data.get('user')} not found"}), 404

    @self.app.route("/qr", methods=["POST"])
    def qr():
      """Update the QR in the state

      Interface function to allow the CameraServer to update the item ID after
      a successful QR scan

      """
      data = request.get_json()
      # Save scanned ID in state
      self.scanned_qr_id = int(data.get("id"))
      print(f"QR with ID {self.scanned_qr_id} scanned")

      # Notify the frontend of the successful scan via the QR event message
      # stream
      self.event_queue.put(self.scanned_qr_id)

      return jsonify({"status": "success"}), 200

    @self.app.route("/qr_events")
    def qr_events():
      """SSE endpoint for QR scan events"""

      def event_stream():
        while True:
          qr_id = self.event_queue.get()
          data = {"event": "update", "itemId": qr_id}
          print(f"Send event: {data}")
          yield f"data: {json.dumps(data)}\n\n"

      return Response(event_stream(), content_type="text/event-stream")

  def send_qr_event(self, id):
    """Compile and send a QR scanned event message

    Args:
        id (int): ID of the scanned QR code

    Yields:
        _type_: _description_
    """
    data = {"event": "update", "id": f"{id}"}

    yield f"data: {json.dumps(data)}\n\n"

  async def run(
    self, host: str = inventory_server_ip, port: int = inventory_server_port
  ):
    """Run the server

    This function is to run the inventory server in a separate thread
    """

    def start_flask():
      self.app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

    # Run the Flask app in a separate thread and return it as an asyncio
    # task
    return await asyncio.to_thread(start_flask)

  async def stop(self):
    info("Stopping Inventory Server...")


if __name__ == "__main__":
  """Allows to run the server directly as module
  """
  server = InventoryServer()
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(asyncio.gather(server.run()))
