"""
Test suite for InventoryServer (FastAPI) -- covers every HTTP route.

HOW THIS WORKS
--------------
InventoryServer.py talks to a real database through `DataBaseClient`. These
tests never hit a real database: `DataBaseClient` is patched wherever
InventoryServer.py uses it, so every route only ever talks to a MagicMock
(see the `mock_db` fixture). That keeps the tests fast, deterministic, and
independent of your actual schema/migrations.

Session auth is exercised for real rather than mocked: tests either omit the
session cookie (to check the 401 paths) or log in through the real
POST /login flow (with a mocked `authenticate_user` return value) and let
Starlette's SessionMiddleware issue a real cookie, exactly like a browser
would. TestClient persists cookies across requests, so `auth_client` stays
logged in for the whole test.

PROJECT LAYOUT
--------------
Matches the actual layout:

    backend/
      src/
        server/
          DataBaseClient.py
          database_schema.py
          inventory_server_config.py
          InventoryServer.py
        tests/
          test_backend_api.py   <- this file

Run from `backend/src` (so `server` resolves as a top-level package):
    uv run pytest tests/test_backend_api.py -v

Needs `httpx` (TestClient) and `python-multipart` (file uploads) as
dependencies -- add them with:
    uv add --dev httpx python-multipart

Also double check `LoginStatus.SUCCESS` against your real enum -- any status
value other than USER_NOT_FOUND/PASSWORD_INVALID makes the real /login route
succeed, so swap in whatever your enum actually calls its "OK" member.
"""

import sqlite3
from unittest.mock import patch

import cv2 as cv
import numpy as np
import pytest
from fastapi.testclient import TestClient

from server.InventoryServer import InventoryServer
from server.database_schema import CheckoutType, LoginStatus, UserPrivileges


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_db():
  """Patch DataBaseClient everywhere InventoryServer.py uses it.

  `patch(...)` replaces the class with a MagicMock; every `DataBaseClient()`
  call in the server returns the *same* mock instance (`mock_cls.return_value`),
  so tests configure behavior once via e.g. `mock_db.get_items....return_value`.
  """
  with patch("server.InventoryServer.DataBaseClient") as mock_cls:
    instance = mock_cls.return_value
    instance.connect.return_value = True
    yield instance


@pytest.fixture
def media_dir(tmp_path):
  d = tmp_path / "media"
  d.mkdir()
  return d


@pytest.fixture
def app(mock_db, media_dir):
  server = InventoryServer(media_path=str(media_dir), session_timeout_min=60.0)
  return server.app


@pytest.fixture
def client(app):
  return TestClient(app)


@pytest.fixture
def auth_client(client, mock_db):
  """A TestClient that has already logged in and carries a session cookie."""
  mock_db.authenticate_user.return_value = (
    LoginStatus.SUCCESS,
    {"id": 1, "user_name": "alice", "user_privileges": "OWNER"},
  )
  resp = client.post("/login", json={"username": "alice", "password": "secret"})
  assert resp.status_code == 200
  mock_db.reset_mock(
    return_value=False
  )  # clear call history, keep return_value/side_effect config
  mock_db.connect.return_value = True
  return client


def _fake_png_bytes(width=20, height=20):
  img = np.zeros((height, width, 3), dtype=np.uint8)
  ok, buf = cv.imencode(".png", img)
  assert ok
  return buf.tobytes()


# ---------------------------------------------------------------------------
# Auth guard -- every protected route must 401 without a session
# ---------------------------------------------------------------------------

PROTECTED_ENDPOINTS = [
  ("get", "/media/somefile.png"),
  ("post", "/checkout_item"),
  ("post", "/return_item"),
  ("get", "/items"),
  ("post", "/get_item"),
  ("post", "/add_item"),
  ("post", "/update_item"),
  ("post", "/delete_item"),
  ("post", "/add_storage"),
  ("post", "/update_storage"),
  ("post", "/delete_storage"),
  ("get", "/storage?id=1"),
  ("post", "/storage_items"),
  ("get", "/storage_locations"),
  ("get", "/item_types"),
  ("post", "/add_item_type"),
  ("post", "/update_item_type"),
  ("post", "/delete_item_type"),
  ("get", "/me"),
  ("post", "/user_privilege"),
  ("get", "/users"),
  ("post", "/add_user"),
  ("post", "/delete_user"),
  ("post", "/update_user_privilege"),
  ("post", "/update_user_password"),
  # NOTE: /image_upload is excluded -- FastAPI validates the required
  # `avatar` file *before* the route body runs, so it 422s rather than
  # 401s without a file attached. It gets its own auth test below.
]


@pytest.mark.parametrize("method,path", PROTECTED_ENDPOINTS)
def test_requires_login(client, method, path):
  resp = client.get(path) if method == "get" else client.post(path, json={})
  assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /login, /logout
# ---------------------------------------------------------------------------


class TestLogin:
  def test_login_success(self, client, mock_db):
    mock_db.authenticate_user.return_value = (
      LoginStatus.SUCCESS,
      {"id": 1, "user_name": "alice", "user_privileges": "OWNER"},
    )
    resp = client.post("/login", json={"username": "alice", "password": "secret"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "Login successful"}
    assert "session" in resp.cookies
    mock_db.log_user_login.assert_called_once_with("alice", LoginStatus.SUCCESS)

  def test_login_user_not_found(self, client, mock_db):
    mock_db.authenticate_user.return_value = (LoginStatus.USER_NOT_FOUND, None)
    resp = client.post("/login", json={"username": "ghost", "password": "x"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "User not found"

  def test_login_invalid_password(self, client, mock_db):
    mock_db.authenticate_user.return_value = (LoginStatus.PASSWORD_INVALID, None)
    resp = client.post("/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_logout_clears_session(auth_client):
  resp = auth_client.post("/logout")
  assert resp.status_code == 200
  assert resp.json() == {"message": "Logged out"}
  # session is gone -> protected routes should reject again
  resp2 = auth_client.get("/items")
  assert resp2.status_code == 401


# ---------------------------------------------------------------------------
# /setup
# ---------------------------------------------------------------------------


class TestSetup:
  def test_get_setup_required_when_no_users(self, client, mock_db):
    mock_db.get_all_inventory_users_as_dict_list.return_value = []
    resp = client.get("/setup")
    assert resp.status_code == 200
    assert resp.json() == {"setup_required": True}

  def test_get_setup_not_required_when_users_exist(self, client, mock_db):
    mock_db.get_all_inventory_users_as_dict_list.return_value = [{"id": 1}]
    resp = client.get("/setup")
    assert resp.json() == {"setup_required": False}

  def test_post_setup_creates_owner(self, client, mock_db):
    mock_db.get_all_inventory_users_as_dict_list.return_value = []
    mock_db.add_inventory_user.return_value = 1
    resp = client.post("/setup", json={"username": "admin", "password": "pw"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "Admin user created"}
    mock_db.add_inventory_user.assert_called_once_with(
      user_name="admin", user_password="pw", user_privileges=UserPrivileges.OWNER
    )

  def test_post_setup_rejected_when_already_complete(self, client, mock_db):
    mock_db.get_all_inventory_users_as_dict_list.return_value = [{"id": 1}]
    resp = client.post("/setup", json={"username": "admin", "password": "pw"})
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# /me, /user_privilege, /users, /add_user, /delete_user,
# /update_user_privilege, /update_user_password
# ---------------------------------------------------------------------------


class TestMe:
  def test_me_success(self, auth_client, mock_db):
    mock_db.get_inventory_user_as_dict.return_value = {
      "id": 1,
      "user_name": "alice",
      "user_privileges": "OWNER",
    }
    resp = auth_client.get("/me")
    assert resp.status_code == 200
    assert resp.json() == {"id": 1, "username": "alice", "user_privileges": "OWNER"}

  def test_me_not_found(self, auth_client, mock_db):
    mock_db.get_inventory_user_as_dict.return_value = None
    resp = auth_client.get("/me")
    assert resp.status_code == 404


def test_user_privilege_found(auth_client, mock_db):
  mock_db.get_inventory_user_as_dict.return_value = {"user_privileges": "ADMIN"}
  resp = auth_client.post("/user_privilege", json={"user": "bob"})
  assert resp.status_code == 200
  assert resp.json() == {"privilege": "ADMIN"}


def test_user_privilege_not_found(auth_client, mock_db):
  mock_db.get_inventory_user_as_dict.return_value = None
  resp = auth_client.post("/user_privilege", json={"user": "ghost"})
  assert resp.status_code == 404


def test_users_list(auth_client, mock_db):
  mock_db.get_all_inventory_users_as_dict_list.return_value = [
    {"id": 1, "user_name": "alice"}
  ]
  resp = auth_client.get("/users")
  assert resp.status_code == 200
  assert resp.json() == [{"id": 1, "user_name": "alice"}]


def test_add_user(auth_client, mock_db):
  mock_db.add_inventory_user.return_value = 42
  resp = auth_client.post(
    "/add_user", json={"username": "bob", "password": "pw", "privilege": "USER"}
  )
  assert resp.status_code == 200
  assert resp.json() == {"message": "42"}
  mock_db.add_inventory_user.assert_called_once_with(
    user_name="bob", user_password="pw", user_privileges="USER"
  )


def test_delete_user(auth_client, mock_db):
  resp = auth_client.post("/delete_user", json={"username": "bob"})
  assert resp.status_code == 200
  assert resp.json() == {"status": "success"}
  mock_db.delete_inventory_user.assert_called_once_with("bob")


def test_update_user_privilege(auth_client, mock_db):
  resp = auth_client.post(
    "/update_user_privilege", json={"username": "bob", "privilege": "ADMIN"}
  )
  assert resp.status_code == 200
  mock_db.update_inventory_user_privileges.assert_called_once_with("bob", "ADMIN")


def test_update_user_password(auth_client, mock_db):
  resp = auth_client.post(
    "/update_user_password", json={"username": "bob", "password": "newpw"}
  )
  assert resp.status_code == 200
  mock_db.update_inventory_user_password.assert_called_once_with("bob", "newpw")


# ---------------------------------------------------------------------------
# /items, /get_item, /checkout_item, /return_item
# ---------------------------------------------------------------------------


def test_items_list_sanitizes_none_and_nan(auth_client, mock_db):
  mock_db.get_all_inventory_items_as_dict_list.return_value = [
    {"id": 1, "name": "Widget", "description": None, "color": float("nan")}
  ]
  resp = auth_client.get("/items")
  assert resp.status_code == 200
  assert resp.json() == [{"id": 1, "name": "Widget", "description": "", "color": ""}]


def test_get_item_found(auth_client, mock_db):
  mock_db.get_inventory_item_as_dict.return_value = {"id": 1, "name": "Widget"}
  resp = auth_client.post("/get_item", json={"itemId": 1})
  assert resp.status_code == 200
  assert resp.json() == {"id": 1, "name": "Widget"}
  mock_db.get_inventory_item_as_dict.assert_called_once_with(1)


def test_get_item_not_found(auth_client, mock_db):
  mock_db.get_inventory_item_as_dict.return_value = None
  resp = auth_client.post("/get_item", json={"itemId": 999})
  assert resp.status_code == 404


def test_checkout_item(auth_client, mock_db):
  resp = auth_client.post("/checkout_item", json={"itemId": 7})
  assert resp.status_code == 200
  assert resp.json() == {"message": "Item 7 checked out"}
  mock_db.update_inventory_item_checkout_status.assert_called_once_with(
    7, "alice", CheckoutType.BORROW
  )


def test_return_item(auth_client, mock_db):
  resp = auth_client.post("/return_item", json={"itemId": 7})
  assert resp.status_code == 200
  assert resp.json() == {"message": "Item 7 returned"}
  mock_db.update_inventory_item_checkout_status.assert_called_once_with(
    7, "alice", CheckoutType.RETURN
  )


# ---------------------------------------------------------------------------
# /add_item, /update_item, /delete_item
# ---------------------------------------------------------------------------


def test_add_item(auth_client, mock_db):
  mock_db.add_inventory_item.return_value = 5
  payload = {"name": "Widget", "description": "A widget"}
  resp = auth_client.post("/add_item", json=payload)
  assert resp.status_code == 200
  assert resp.json() == {"message": "5"}
  mock_db.add_inventory_item.assert_called_once_with(payload)


def test_update_item_strips_unknown_fields_and_coerces_blank_ints_to_none(
  auth_client, mock_db
):
  resp = auth_client.post(
    "/update_item",
    json={"id": 3, "name": "Updated", "location": "", "not_a_real_field": "x"},
  )
  assert resp.status_code == 200
  assert resp.json() == {"status": "item updated"}
  mock_db.update_inventory_item.assert_called_once_with(
    {"name": "Updated", "location": None}, 3
  )


def test_delete_item(auth_client, mock_db):
  resp = auth_client.post("/delete_item", json={"itemId": 3})
  assert resp.status_code == 200
  assert resp.json() == {"status": "success"}
  mock_db.delete_inventory_item.assert_called_once_with(3)


# ---------------------------------------------------------------------------
# /add_storage, /update_storage, /delete_storage, /storage, /storage_items,
# /storage_locations
# ---------------------------------------------------------------------------


def test_add_storage(auth_client, mock_db):
  mock_db.add_storage_location.return_value = 9
  resp = auth_client.post("/add_storage", json={"name": "Shelf A"})
  assert resp.status_code == 200
  assert resp.json() == {"message": "9"}


def test_update_storage(auth_client, mock_db):
  resp = auth_client.post("/update_storage", json={"id": 9, "name": "Shelf B"})
  assert resp.status_code == 200
  mock_db.update_storage_location.assert_called_once_with({"name": "Shelf B"}, 9)


def test_delete_storage(auth_client, mock_db):
  resp = auth_client.post("/delete_storage", json={"id": 9})
  assert resp.status_code == 200
  mock_db.delete_storage_location.assert_called_once_with(9)


def test_get_storage_found(auth_client, mock_db):
  mock_db.get_storage_location.return_value = {
    "id": 9,
    "name": "Shelf A",
    "capacity": float("nan"),
  }
  resp = auth_client.get("/storage", params={"id": 9})
  assert resp.status_code == 200
  assert resp.json() == {"id": 9, "name": "Shelf A", "capacity": ""}


def test_get_storage_takes_first_row_when_list_returned(auth_client, mock_db):
  mock_db.get_storage_location.return_value = [{"id": 9, "name": "Shelf A"}]
  resp = auth_client.get("/storage", params={"id": 9})
  assert resp.status_code == 200
  assert resp.json() == {"id": 9, "name": "Shelf A"}


@pytest.mark.parametrize("empty_value", [None, []])
def test_get_storage_not_found(auth_client, mock_db, empty_value):
  mock_db.get_storage_location.return_value = empty_value
  resp = auth_client.get("/storage", params={"id": 999})
  assert resp.status_code == 404


def test_storage_items(auth_client, mock_db):
  mock_db.get_storage_items.return_value = [{"id": 1, "name": "Widget", "notes": None}]
  resp = auth_client.post("/storage_items", json={"id": 9})
  assert resp.status_code == 200
  assert resp.json() == [{"id": 1, "name": "Widget", "notes": ""}]


def test_storage_locations(auth_client, mock_db):
  mock_db.get_all_storage_locations_as_dict_list.return_value = [
    {"id": 9, "name": "Shelf A"}
  ]
  resp = auth_client.get("/storage_locations")
  assert resp.status_code == 200
  assert resp.json() == [{"id": 9, "name": "Shelf A"}]


# ---------------------------------------------------------------------------
# /item_types, /add_item_type, /update_item_type, /delete_item_type
# ---------------------------------------------------------------------------


def test_item_types_list(auth_client, mock_db):
  mock_db.get_all_item_types_as_dict_list.return_value = [{"id": 1, "name": "Tool"}]
  resp = auth_client.get("/item_types")
  assert resp.status_code == 200
  assert resp.json() == [{"id": 1, "name": "Tool"}]


class TestAddItemType:
  def test_success(self, auth_client, mock_db):
    mock_db.add_item_type.return_value = 4
    resp = auth_client.post("/add_item_type", json={"name": "Tool"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "4"}

  def test_blank_name_rejected(self, auth_client, mock_db):
    resp = auth_client.post("/add_item_type", json={"name": "   "})
    assert resp.status_code == 400
    mock_db.add_item_type.assert_not_called()

  def test_duplicate_name_conflicts(self, auth_client, mock_db):
    mock_db.add_item_type.side_effect = sqlite3.IntegrityError()
    resp = auth_client.post("/add_item_type", json={"name": "Tool"})
    assert resp.status_code == 409


class TestUpdateItemType:
  def test_success(self, auth_client, mock_db):
    resp = auth_client.post("/update_item_type", json={"id": 4, "name": "Tool v2"})
    assert resp.status_code == 200
    mock_db.update_item_type.assert_called_once_with(4, "Tool v2")

  def test_blank_name_rejected(self, auth_client, mock_db):
    resp = auth_client.post("/update_item_type", json={"id": 4, "name": ""})
    assert resp.status_code == 400

  def test_duplicate_name_conflicts(self, auth_client, mock_db):
    mock_db.update_item_type.side_effect = sqlite3.IntegrityError()
    resp = auth_client.post("/update_item_type", json={"id": 4, "name": "Tool"})
    assert resp.status_code == 409


def test_delete_item_type(auth_client, mock_db):
  resp = auth_client.post("/delete_item_type", json={"id": 4})
  assert resp.status_code == 200
  mock_db.delete_item_type.assert_called_once_with(4)


# ---------------------------------------------------------------------------
# /image_upload
# ---------------------------------------------------------------------------


class TestImageUpload:
  def test_requires_login(self, client):
    files = {"avatar": ("test.png", _fake_png_bytes(), "image/png")}
    resp = client.post("/image_upload", files=files)
    assert resp.status_code == 401

  def test_upload_success_saves_image_and_thumbnail(self, auth_client, media_dir):
    files = {"avatar": ("test.png", _fake_png_bytes(), "image/png")}
    with patch("server.InventoryServer.MEDIA_DEFAULT_PATH", str(media_dir)):
      resp = auth_client.post("/image_upload", files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Image saved"
    image_hash = body["image"]
    assert (media_dir / f"{image_hash}.png").exists()
    assert (media_dir / f"thumbnail_{image_hash}.png").exists()

  def test_upload_rejects_undecodable_file(self, auth_client, media_dir):
    files = {"avatar": ("bad.png", b"this is not an image", "image/png")}
    with patch("server.InventoryServer.MEDIA_DEFAULT_PATH", str(media_dir)):
      resp = auth_client.post("/image_upload", files=files)
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /media/{filename}
# ---------------------------------------------------------------------------


class TestServeMedia:
  def test_found(self, auth_client, media_dir):
    (media_dir / "logo.png").write_bytes(b"fake-image-bytes")
    resp = auth_client.get("/media/logo.png")
    assert resp.status_code == 200
    assert resp.content == b"fake-image-bytes"

  def test_not_found(self, auth_client):
    resp = auth_client.get("/media/missing.png")
    assert resp.status_code == 404
