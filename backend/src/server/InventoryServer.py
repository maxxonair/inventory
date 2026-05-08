"""[Inventory] Inventory Server


Run this module manually from the projects backend directory with:

$ uv run -m src.InventoryServer

NOTE: This server is intended to be run as a containerized service
within a Docker or Podman environment and is auto-configured via the
install.py script to run containerized. Configure the server settings
in the inventory_server_config.py file before running standalone.

"""

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_session import Session
from logging import info, error
from datetime import timedelta
import asyncio
import cv2 as cv
import numpy as np
import queue
import math
import hashlib
from pathlib import Path

from server.InventoryUser import InventoryUser
from server.DataBaseClient import DataBaseClient

from server.database_config import CheckoutType, LoginStatus

from server.inventory_server_config import (
  inventory_server_ip,
  inventory_server_port,
  MEDIA_DEFAULT_PATH,
  DEFAULT_DB_HOST,
  DEFAULT_DB_PORT,
)

# Max size for thumbnail images in pixels
MAX_THUMB_SIZE_PX = 200


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

    self.event_queue = queue.Queue()

    # Store the camera server URL
    self.camera_registry = {"url": None}

    self.db_host = db_host
    self.db_port = db_port

    # Routes
    self.configure_routes()

  def configure_routes(self):
    """Configure Http routes for this server"""

    # --------------------------------------------------------------------------
    #       ROUTE --> /media/<filename>
    # --------------------------------------------------------------------------
    @self.app.route("/media/<filename>")
    def serve_image(filename):
      """Serve requested image from the media directory"""
      return send_from_directory(self.media_path, filename)

    # --------------------------------------------------------------------------
    #       ROUTE --> /checkout_item
    # --------------------------------------------------------------------------
    @self.app.route("/checkout_item", methods=["POST"])
    def checkout_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500

      client.update_inventory_item_checkout_status(
        int(data["itemId"]), session["user"], CheckoutType.BORROW
      )
      client.close_connection()
      return jsonify({"message": f"Item {data['itemId']} checked out"})

    # --------------------------------------------------------------------------
    #       ROUTE --> /return_item
    # --------------------------------------------------------------------------
    @self.app.route("/return_item", methods=["POST"])
    def return_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500

      client.update_inventory_item_checkout_status(
        int(data["itemId"]), session["user"], CheckoutType.RETURN
      )
      client.close_connection()
      return jsonify({"message": f"Item {data['itemId']} checked out"})

    # --------------------------------------------------------------------------
    #       ROUTE --> /items
    # --------------------------------------------------------------------------
    @self.app.route("/items")
    def get_items():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      data_dict = client.get_all_inventory_items_as_dict_list()
      client.close_connection()
      return jsonify(data_dict)

    # --------------------------------------------------------------------------
    #       ROUTE --> /get_item
    # --------------------------------------------------------------------------
    @self.app.route("/get_item", methods=["POST"])
    def get_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      data_dict = client.get_inventory_item_as_dict(int(data["itemId"]))
      client.close_connection()
      # TODO add callback funtion to check if item with ID exists in DB

      if data_dict is None:
        return jsonify({"error": "Item not found!"}), 401
      return jsonify(data_dict)

    # --------------------------------------------------------------------------
    #       ROUTE --> /image_upload
    # --------------------------------------------------------------------------
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

      # --- Generate thumbnail ---
      h, w = img_np.shape[:2]
      scale = min(MAX_THUMB_SIZE_PX / w, MAX_THUMB_SIZE_PX / h, 1)  # Never upscale
      thumb_np = cv.resize(
        img_np, (int(w * scale), int(h * scale)), interpolation=cv.INTER_AREA
      )

      thumb_path = Path(MEDIA_DEFAULT_PATH) / f"thumbnail_{hash_hex}.png"
      thumb_success = cv.imwrite(str(thumb_path), thumb_np)

      if not thumb_success:
        return {"error": "Failed to save thumbnail"}, 500

      return {"message": "Image saved", "image": f"{hash_hex}"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /add_item
    # --------------------------------------------------------------------------
    @self.app.route("/add_item", methods=["POST"])
    def add_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      new_id = client.add_inventory_item(data_dict)
      client.close_connection()
      return jsonify({"message": f"{new_id}"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /update_item
    # --------------------------------------------------------------------------
    @self.app.route("/update_item", methods=["POST"])
    def update_item():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = request.json
      item_id = int(data_dict["id"])
      data_dict.pop("id")
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      client.update_inventory_item(data_dict, item_id)
      client.close_connection()
      return jsonify({"status": "item updated"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /delete_item
    # --------------------------------------------------------------------------
    @self.app.route("/delete_item", methods=["POST"])
    def delete_item():
      """Remove item from inventory database"""
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.get_json()
      item_id = int(data.get("itemId"))
      info(f"Delete item with ID {item_id}")
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      client.delete_inventory_item(item_id)
      client.close_connection()

      return jsonify({"status": "success"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /add_storage
    # --------------------------------------------------------------------------
    @self.app.route("/add_storage", methods=["POST"])
    def add_storage():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      new_id = client.add_storage_location(data_dict)
      client.close_connection()
      return jsonify({"message": f"{new_id}"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /update_storage
    # --------------------------------------------------------------------------
    @self.app.route("/update_storage", methods=["POST"])
    def update_storage():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = request.json
      item_id = int(data_dict["id"])
      data_dict.pop("id")
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      client.update_storage_location(data_dict, item_id)
      client.close_connection()
      return jsonify({"status": "storage location updated"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /delete_storage
    # --------------------------------------------------------------------------
    @self.app.route("/delete_storage", methods=["POST"])
    def delete_storage():
      """Remove storage location from database"""
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.get_json()
      storage_id = int(data.get("id"))
      info(f"Delete storage location with ID {storage_id}")
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      client.delete_storage_location(storage_id)
      client.close_connection()

      return jsonify({"status": "success"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /storage
    # --------------------------------------------------------------------------
    @self.app.route("/storage")
    def get_storage():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

      client = DataBaseClient(host=self.db_host, port=self.db_port)

      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      
      data = request.get_json()
      storage_id = int(data.get("id"))
      info(f"Serve storage info fors ID {storage_id}")

      data_dict = client.get_storage_location(storage_id)

      client.close_connection()

      # Replace NaN with empty string
      cleaned_data = {
        k: ("" if isinstance(v, float) and math.isnan(v) else v)
        for k, v in data_dict.items()
      }

      return jsonify(cleaned_data)

    # --------------------------------------------------------------------------
    #       ROUTE --> /storage_locations
    # --------------------------------------------------------------------------
    @self.app.route("/storage_locations")
    def get_storage_locations():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

      client = DataBaseClient(host=self.db_host, port=self.db_port)

      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500

      data_dict_list = client.get_all_storage_locations_as_dict_list()

      client.close_connection()

      # Replace NaN with empty string
      cleaned_data = []
      for row in data_dict_list:
        cleaned_row = {
          k: ("" if isinstance(v, float) and math.isnan(v) else v)
          for k, v in row.items()
        }
        cleaned_data.append(cleaned_row)

      return jsonify(cleaned_data)

    # --------------------------------------------------------------------------
    #       ROUTE --> /login
    # --------------------------------------------------------------------------
    @self.app.route("/login", methods=["POST"])
    def login():
      data = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      is_user_exists, inventoryUser = client.get_inventory_user_as_object(
        str(data["username"])
      )

      info(f"Log in attempt: {data['username']} -> {is_user_exists}")
      if not is_user_exists:
        client.log_user_login(data["username"], LoginStatus.USER_NOT_FOUND)
        client.close_connection()
        return jsonify({"error": "User not found"}), 401
      if not inventoryUser.is_password(str(data["password"])):
        client.log_user_login(data["username"], LoginStatus.PASSWORD_INVALID)
        client.close_connection()
        return jsonify({"error": "Invalid credentials"}), 401
      else:
        client.log_user_login(data["username"], LoginStatus.SUCCESS)
        client.close_connection()

      # Login valid -> Create a session cookie for this user
      session["user"] = data["username"]
      return jsonify({"message": "Login successful"})

    # --------------------------------------------------------------------------
    #       ROUTE --> /logout
    # --------------------------------------------------------------------------
    @self.app.route("/logout", methods=["POST"])
    def logout():
      info("Log out user")
      session.clear()
      return jsonify({"message": "Logged out"})

    # --------------------------------------------------------------------------
    #       ROUTE --> /me
    # --------------------------------------------------------------------------
    @self.app.route("/me")
    def me():
      if "user" in session:
        info(f"User {session['user']} logged in")
        return jsonify({"user": session["user"]})
      return jsonify({"error": "Not logged in"}), 401

    # --------------------------------------------------------------------------
    #       ROUTE --> /user_privilege
    # --------------------------------------------------------------------------
    @self.app.route("/user_privilege", methods=["POST"])
    def user_privilege():
      """Return privilege level for a given user"""
      data = request.get_json()
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      # Load privilege level for this user
      info(f"Load privilege level for user {str(data.get('user'))}")
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      try:
        user_dict = client.get_inventory_user_as_dict(str(data.get("user")))
        info(
          f"User {data.get('user')} authorized up to privilege level {user_dict['user_privileges']}"
        )
        client.close_connection()
        return jsonify({"privilege": user_dict["user_privileges"]})
      except Exception as e:
        error(f"User {data.get('user')} not found: {e}")
        client.close_connection()
        return jsonify({"error": f"User: {data.get('user')} not found"}), 404

    # --------------------------------------------------------------------------
    #       ROUTE --> /users
    # --------------------------------------------------------------------------
    @self.app.route("/users")
    def get_users():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      data_dict = client.get_all_inventory_users_as_dict_list()
      client.close_connection()
      return jsonify(data_dict)

    # --------------------------------------------------------------------------
    #       ROUTE --> /add_user
    # --------------------------------------------------------------------------
    @self.app.route("/add_user", methods=["POST"])
    def add_user():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

      # TODO add check if user has sufficient privileges to add new user
      data_dict = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      new_user = InventoryUser(
        user_name=data_dict["username"],
        password=data_dict["password"],
        user_privileges=data_dict["privilege"],
      )
      new_id = client.add_inventory_user(new_user)
      client.close_connection()
      return jsonify({"message": f"{new_id}"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /delete_user
    # --------------------------------------------------------------------------
    @self.app.route("/delete_user", methods=["POST"])
    def delete_user():
      """Remove user from database"""
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data = request.get_json()
      user_name = int(data.get("username"))
      info(f"Delete user: {user_name}")
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      client.delete_inventory_user(user_name)
      client.close_connection()

      return jsonify({"status": "success"}), 200

    # --------------------------------------------------------------------------
    #       ROUTE --> /set_user_privilege
    # --------------------------------------------------------------------------
    @self.app.route("/update_user", methods=["POST"])
    def update_user():
      if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
      data_dict = request.json
      client = DataBaseClient(host=self.db_host, port=self.db_port)
      if not client.connect():
        return jsonify({"error": "Database connection failed"}), 500
      updated_user = InventoryUser(
        user_name=data_dict["username"],
        password=data_dict["password"],
        user_privileges=data_dict["privilege"],
      )
      client.update_inventory_user_privileges(updated_user)
      client.update_inventory_user_password(updated_user)
      client.close_connection()
      return jsonify({"message": "Success"})

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
