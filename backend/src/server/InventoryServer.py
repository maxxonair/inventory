"""[Inventory] Inventory Server


Run this module manually from the projects backend directory with:

$ uv run -m src.InventoryServer

NOTE: This server is intended to be run as a containerized service
within a Docker or Podman environment and is auto-configured via the
install.py script to run containerized. Configure the server settings
in the inventory_server_config.py file before running standalone.

"""

from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import asyncio
import cv2 as cv
import numpy as np
import queue
import math
import hashlib
from pathlib import Path
from typing import Any
import uvicorn
import logging

from server.InventoryUser import InventoryUser
from server.DataBaseClient import DataBaseClient

from server.database_config import CheckoutType, LoginStatus

from server.inventory_server_config import (
  inventory_server_ip,
  inventory_server_port,
  MEDIA_DEFAULT_PATH,
)

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
  datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
info = logger.info
error = logger.error

# Max size for thumbnail images in pixels
MAX_THUMB_SIZE_PX = 200

ALLOWED_ITEM_FIELDS = {
  "name",
  "image",
  "description",
  "manufacturer",
  "details",
  "is_checked_out",
  "check_out_date",
  "check_out_poc",
  "tags",
  "location",
  "item_type",
  "manufacturer_link",
  "project",
  "manufacturer_location",
  "color",
  "material",
  "product_use",
  "number_items",
}

INTEGER_ITEM_FIELDS = {"location", "number_items", "is_checked_out"}


class InventoryServer:
  def __init__(
    self,
    media_path: str = MEDIA_DEFAULT_PATH,
    session_timeout_min: float = 60.0,
  ):
    """Create InventoryServer instance

    Args:
        media_path (str, optional): Media storage file path.
            Defaults to MEDIA_DEFAULT_PATH.
        session_timeout_min (float, optional): Session timeout for active user
            sessions. Defaults to 60.0 minutes
    """
    self.app = FastAPI()

    # Session middleware (replaces flask-session)
    self.app.add_middleware(
      SessionMiddleware,
      secret_key="super-secret",
      max_age=int(session_timeout_min * 60),
    )

    # CORS middleware
    self.app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )

    # Set path to load media files from
    self.media_path = media_path

    self.scanned_qr_id = None

    self.event_queue = queue.Queue()

    # Store the camera server URL
    self.camera_registry = {"url": None}

    # Initialize database client (will be connected on demand in each route)
    _ = DataBaseClient()

    # Routes
    self.configure_routes()

  def _sanitize_dict_list(self, data_dict_list):
    """Sanitize input data — replace NaN and None with empty string"""
    cleaned_data = []
    for row in data_dict_list:
      cleaned_row = {
        k: ("" if (isinstance(v, float) and math.isnan(v) or v is None) else v)
        for k, v in row.items()
      }
      cleaned_data.append(cleaned_row)
    return cleaned_data

  def _get_session_user(self, request: Request) -> str:
    """Return the logged-in username or raise 401."""
    user = request.session.get("user")
    if not user:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
      )
    return user

  def _db_connect(self) -> DataBaseClient:
    """Return a connected DataBaseClient or raise 500."""
    client = DataBaseClient()
    if not client.connect():
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database connection failed",
      )
    return client

  def configure_routes(self):
    """Configure HTTP routes for this server"""

    # --------------------------------------------------------------------------
    #       ROUTE --> /media/<filename>
    # --------------------------------------------------------------------------
    @self.app.get("/media/{filename}")
    def serve_image(filename: str):
      """Serve requested image from the media directory"""
      file_path = Path(self.media_path) / filename
      if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
      return FileResponse(str(file_path))

    # --------------------------------------------------------------------------
    #       ROUTE --> /checkout_item
    # --------------------------------------------------------------------------
    @self.app.post("/checkout_item")
    async def checkout_item(request: Request):
      user = self._get_session_user(request)
      data = await request.json()
      client = self._db_connect()
      client.update_inventory_item_checkout_status(
        int(data["itemId"]), user, CheckoutType.BORROW
      )
      client.close_connection()
      return {"message": f"Item {data['itemId']} checked out"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /return_item
    # --------------------------------------------------------------------------
    @self.app.post("/return_item")
    async def return_item(request: Request):
      user = self._get_session_user(request)
      data = await request.json()
      client = self._db_connect()
      client.update_inventory_item_checkout_status(
        int(data["itemId"]), user, CheckoutType.RETURN
      )
      client.close_connection()
      return {"message": f"Item {data['itemId']} returned"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /items
    # --------------------------------------------------------------------------
    @self.app.get("/items")
    def get_items(request: Request):
      self._get_session_user(request)
      client = self._db_connect()
      data_dict_list = client.get_all_inventory_items_as_dict_list()
      cleaned_data = self._sanitize_dict_list(data_dict_list)
      client.close_connection()
      return cleaned_data

    # --------------------------------------------------------------------------
    #       ROUTE --> /get_item
    # --------------------------------------------------------------------------
    @self.app.post("/get_item")
    async def get_item(request: Request):
      self._get_session_user(request)
      data = await request.json()
      client = self._db_connect()
      data_dict = client.get_inventory_item_as_dict(int(data["itemId"]))
      client.close_connection()
      if data_dict is None:
        raise HTTPException(status_code=404, detail="Item not found!")
      return data_dict

    # --------------------------------------------------------------------------
    #       ROUTE --> /image_upload
    # --------------------------------------------------------------------------
    @self.app.post("/image_upload")
    async def upload_file(avatar: UploadFile = File(...)):
      file_bytes = await avatar.read()

      # Hash the file bytes
      hash_hex = hashlib.sha256(file_bytes).hexdigest()

      # Convert bytes to NumPy array for OpenCV
      nparr = np.frombuffer(file_bytes, np.uint8)
      img_np = cv.imdecode(nparr, cv.IMREAD_COLOR)

      if img_np is None:
        raise HTTPException(status_code=400, detail="Could not decode image")

      # Save image using OpenCV
      img_path = Path(MEDIA_DEFAULT_PATH) / f"{hash_hex}.png"
      if not cv.imwrite(str(img_path), img_np):
        print(f"Failed to save uploaded image file to {img_path}")
        raise HTTPException(status_code=500, detail="Failed to save image")

      # --- Generate thumbnail ---
      h, w = img_np.shape[:2]
      scale = min(MAX_THUMB_SIZE_PX / w, MAX_THUMB_SIZE_PX / h, 1)  # Never upscale
      thumb_np = cv.resize(
        img_np, (int(w * scale), int(h * scale)), interpolation=cv.INTER_AREA
      )

      thumb_path = Path(MEDIA_DEFAULT_PATH) / f"thumbnail_{hash_hex}.png"
      if not cv.imwrite(str(thumb_path), thumb_np):
        print("Failed to save thumbnail")
        raise HTTPException(status_code=500, detail="Failed to save thumbnail")

      return {"message": "Image saved", "image": hash_hex}

    # --------------------------------------------------------------------------
    #       ROUTE --> /add_item
    # --------------------------------------------------------------------------
    @self.app.post("/add_item")
    async def add_item(request: Request):
      self._get_session_user(request)
      data_dict = await request.json()
      client = self._db_connect()
      new_id = client.add_inventory_item(data_dict)
      client.close_connection()
      return JSONResponse(content={"message": f"{new_id}"}, status_code=200)

    # --------------------------------------------------------------------------
    #       ROUTE --> /update_item
    # --------------------------------------------------------------------------
    @self.app.post("/update_item")
    async def update_item(request: Request):
      self._get_session_user(request)
      data_dict = await request.json()
      item_id = int(data_dict.pop("id"))

      # Strip unknown fields, coerce empty strings to None for integer columns
      data_dict = {
        k: (None if v == "" else v) if k in INTEGER_ITEM_FIELDS else v
        for k, v in data_dict.items()
        if k in ALLOWED_ITEM_FIELDS
      }

      client = self._db_connect()
      client.update_inventory_item(data_dict, item_id)
      client.close_connection()
      return {"status": "item updated"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /delete_item
    # --------------------------------------------------------------------------
    @self.app.post("/delete_item")
    async def delete_item(request: Request):
      """Remove item from inventory database"""
      self._get_session_user(request)
      data = await request.json()
      item_id = int(data.get("itemId"))
      info(f"Delete item with ID {item_id}")
      client = self._db_connect()
      client.delete_inventory_item(item_id)
      client.close_connection()
      return {"status": "success"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /add_storage
    # --------------------------------------------------------------------------
    @self.app.post("/add_storage")
    async def add_storage(request: Request):
      self._get_session_user(request)
      data_dict = await request.json()
      client = self._db_connect()
      new_id = client.add_storage_location(data_dict)
      client.close_connection()
      return JSONResponse(content={"message": f"{new_id}"}, status_code=200)

    # --------------------------------------------------------------------------
    #       ROUTE --> /update_storage
    # --------------------------------------------------------------------------
    @self.app.post("/update_storage")
    async def update_storage(request: Request):
      self._get_session_user(request)
      data_dict = await request.json()
      item_id = int(data_dict.pop("id"))
      client = self._db_connect()
      client.update_storage_location(data_dict, item_id)
      client.close_connection()
      return {"status": "storage location updated"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /delete_storage
    # --------------------------------------------------------------------------
    @self.app.post("/delete_storage")
    async def delete_storage(request: Request):
      """Remove storage location from database"""
      self._get_session_user(request)
      data = await request.json()
      storage_id = int(data.get("id"))
      info(f"Delete storage location with ID {storage_id}")
      client = self._db_connect()
      client.delete_storage_location(storage_id)
      client.close_connection()
      return {"status": "success"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /storage
    # --------------------------------------------------------------------------
    @self.app.get("/storage")
    def get_storage(request: Request, id: int):
      self._get_session_user(request)
      info(f"Serve storage info for ID {id}")
      client = self._db_connect()
      data_dict = client.get_storage_location(id)
      client.close_connection()

      if not data_dict:
        raise HTTPException(status_code=404, detail="Storage location not found")

      # get_storage_location may return a list — take the first row
      if isinstance(data_dict, list):
        if len(data_dict) == 0:
          raise HTTPException(status_code=404, detail="Storage location not found")
        data_dict = data_dict[0]

      # Replace NaN with empty string
      cleaned_data = {
        k: ("" if isinstance(v, float) and math.isnan(v) else v)
        for k, v in data_dict.items()
      }
      return cleaned_data

    # --------------------------------------------------------------------------
    #       ROUTE --> /storage_items
    # --------------------------------------------------------------------------
    @self.app.post("/storage_items")
    async def get_storage_items(request: Request):
      self._get_session_user(request)
      data = await request.json()
      storage_id = int(data.get("id"))
      info(f"Serve storage items for ID {storage_id}")
      client = self._db_connect()
      data_dict_list = client.get_storage_items(storage_id)
      cleaned_data = self._sanitize_dict_list(data_dict_list)
      client.close_connection()
      return cleaned_data

    # --------------------------------------------------------------------------
    #       ROUTE --> /storage_locations
    # --------------------------------------------------------------------------
    @self.app.get("/storage_locations")
    def get_storage_locations(request: Request):
      self._get_session_user(request)
      client = self._db_connect()
      data_dict_list = client.get_all_storage_locations_as_dict_list()
      client.close_connection()
      cleaned_data = self._sanitize_dict_list(data_dict_list)
      return cleaned_data

    # --------------------------------------------------------------------------
    #       ROUTE --> /login
    # --------------------------------------------------------------------------
    @self.app.post("/login")
    async def login(request: Request):
      data = await request.json()
      client = self._db_connect()
      is_user_exists, inventoryUser = client.get_inventory_user_as_object(
        str(data["username"])
      )

      info(f"Log in attempt: {data['username']} -> {is_user_exists}")
      if not is_user_exists:
        client.log_user_login(data["username"], LoginStatus.USER_NOT_FOUND)
        client.close_connection()
        raise HTTPException(status_code=401, detail="User not found")
      if not inventoryUser.is_password(str(data["password"])):
        client.log_user_login(data["username"], LoginStatus.PASSWORD_INVALID)
        client.close_connection()
        raise HTTPException(status_code=401, detail="Invalid credentials")

      client.log_user_login(data["username"], LoginStatus.SUCCESS)
      client.close_connection()

      # Login valid -> Create a session cookie for this user
      request.session["user"] = data["username"]
      return {"message": "Login successful"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /logout
    # --------------------------------------------------------------------------
    @self.app.post("/logout")
    def logout(request: Request):
      info("Log out user")
      request.session.clear()
      return {"message": "Logged out"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /me
    # --------------------------------------------------------------------------
    @self.app.get("/me")
    def me(request: Request):
      session_user = self._get_session_user(request)
      client = self._db_connect()
      try:
        user = client.get_inventory_user_as_dict(session_user)
        client.close_connection()
        if not user:
          raise HTTPException(status_code=404, detail="User not found")
        return {
          "id": user["id"],
          "username": user["user_name"],
          "user_privileges": user["user_privileges"],
        }
      except HTTPException:
        raise
      except Exception as e:
        error(f"User {session_user} not found: {e}")
        client.close_connection()
        raise HTTPException(status_code=404, detail=f"User: {session_user} not found")

    # --------------------------------------------------------------------------
    #       ROUTE --> /user_privilege
    # --------------------------------------------------------------------------
    @self.app.post("/user_privilege")
    async def user_privilege(request: Request):
      """Return privilege level for a given user"""
      self._get_session_user(request)
      data = await request.json()
      print(f"Load privilege level for user {str(data.get('user'))}")
      client = self._db_connect()
      try:
        user_dict = client.get_inventory_user_as_dict(str(data.get("user")))
        print(
          f"User {data.get('user')} authorized up to privilege level {user_dict['user_privileges']}"
        )
        client.close_connection()
        return {"privilege": user_dict["user_privileges"]}
      except Exception as e:
        error(f"User {data.get('user')} not found: {e}")
        client.close_connection()
        raise HTTPException(
          status_code=404, detail=f"User: {data.get('user')} not found"
        )

    # --------------------------------------------------------------------------
    #       ROUTE --> /users
    # --------------------------------------------------------------------------
    @self.app.get("/users")
    def users(request: Request):
      self._get_session_user(request)
      client = self._db_connect()
      data_dict = client.get_all_inventory_users_as_dict_list()
      client.close_connection()
      return data_dict

    # --------------------------------------------------------------------------
    #       ROUTE --> /setup
    # --------------------------------------------------------------------------
    @self.app.get("/setup")
    def setup_get():
      client = self._db_connect()
      user_list = client.get_all_inventory_users_as_dict_list()
      client.close_connection()
      return {"setup_required": len(user_list) == 0}

    @self.app.post("/setup")
    async def setup_post(request: Request):
      client = self._db_connect()
      user_list = client.get_all_inventory_users_as_dict_list()

      if len(user_list) > 0:
        client.close_connection()
        raise HTTPException(status_code=403, detail="Setup already complete")

      try:
        data = await request.json()
        from server.InventoryUser import UserPrivileges

        new_user = InventoryUser(
          user_name=data["username"],
          user_password=data["password"],
          user_privileges=UserPrivileges.OWNER,
        )
        client.add_inventory_user(new_user)
        client.close_connection()
        return JSONResponse(content={"message": "Admin user created"}, status_code=200)
      except HTTPException:
        raise
      except Exception as e:
        error(f"Setup error: {e}")
        client.close_connection()
        raise HTTPException(status_code=500, detail=str(e))

    # --------------------------------------------------------------------------
    #       ROUTE --> /add_user
    # --------------------------------------------------------------------------
    @self.app.post("/add_user")
    async def add_user(request: Request):
      self._get_session_user(request)
      # TODO add check if user has sufficient privileges to add new user
      data_dict = await request.json()
      client = self._db_connect()
      new_user = InventoryUser(
        user_name=data_dict["username"],
        user_password=data_dict["password"],
      )
      new_user.user_privileges = data_dict["privilege"]
      new_id = client.add_inventory_user(new_user)
      client.close_connection()
      return JSONResponse(content={"message": f"{new_id}"}, status_code=200)

    # --------------------------------------------------------------------------
    #       ROUTE --> /delete_user
    # --------------------------------------------------------------------------
    @self.app.post("/delete_user")
    async def delete_user(request: Request):
      """Remove user from database"""
      self._get_session_user(request)
      data = await request.json()
      user_name = str(data.get("username"))
      info(f"Delete user: {user_name}")
      client = self._db_connect()
      client.delete_inventory_user(user_name)
      client.close_connection()
      return {"status": "success"}

    # --------------------------------------------------------------------------
    #       ROUTE --> /update_user
    # --------------------------------------------------------------------------
    @self.app.post("/update_user")
    async def update_user(request: Request):
      self._get_session_user(request)
      data_dict = await request.json()
      client = self._db_connect()
      from server.InventoryUser import UserPrivileges

      updated_user = InventoryUser(
        user_name=data_dict["username"],
        user_password=data_dict["password"],
        user_privileges=UserPrivileges(data_dict["privilege"]),
      )
      client.update_inventory_user_privileges(updated_user)
      client.update_inventory_user_password(updated_user)
      client.close_connection()
      return {"message": "Success"}

  async def run(
    self, host: str = inventory_server_ip, port: int = inventory_server_port
  ):
    """Run the server using uvicorn"""
    config = uvicorn.Config(self.app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

  async def stop(self):
    info("Stopping Inventory Server...")


if __name__ == "__main__":
  """Allows to run the server directly as module"""
  server = InventoryServer()
  asyncio.run(server.run())
