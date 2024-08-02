"""

Inventory frontend main application

"""
import numpy as np
import pandas as pd
import altair as alt
import cv2 as cv
from pathlib import Path
# from itertools import cycle
from trame.widgets import vuetify, vega, router, html
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.ui.router import RouterViewLayout
from trame.app import get_server
from flask import Flask, send_from_directory
import sys
import os
import logging
from logging import info, warning
from multiprocessing import Process
import signal
import base64
import hashlib

# --------------------------------------------------------------------------
#                           [Inventory Imports]
# --------------------------------------------------------------------------
# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# ---- Backend imports
from backend.DataBaseClient import DataBaseClient
from backend.database_config import database_host
from backend.camera_server.CameraServer import CameraServer
from backend.InventoryItem import InventoryItem

# ---- Frontend imports

# Import configuration parameters
from frontend.frontend_config import (inventory_page_title,
                                      inventory_main_window_title,
                                      main_table_header_options,
                                      frontend_host_ip,
                                      frontend_host_port,
                                      html_content_embed_camera_stream,
                                      html_content_embed_camera_stream_large,
                                      media_directory,
                                      image_not_found_path,
                                      enableLogin)

# Import frontend utility functions
from frontend.util import parse_qr_message

# --------------------------------------------------------------------------
#                       [Global Variables]
# --------------------------------------------------------------------------

# Create global handle for the camera server running in a background
# process
camera_process = None

# Create camera server instance
camera_server = CameraServer()

# Create global handle for the camera server running in a background
# process
image_process = None

# Initialize variable to hold the complete inventory in a dataframe
inventory_df = []

with open(image_not_found_path, "rb") as image_file:
  encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
# -----------------------------------------------------------------------
# Database connection
# -----------------------------------------------------------------------
# Create a DatabaseClient instance and connect to the inventory database
db_client = DataBaseClient(host=database_host)

# TODO to be removed when user database is in place
# Dummy credentials for demonstration purposes
VALID_USERNAME = "romi"
VALID_PASSWORD = "pass"


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
# -----------------------------------------------------------------------
# Main application server
# -----------------------------------------------------------------------


server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# Initialize the Flask app
flask_app = Flask(__name__)

state = server.state

# Create server.state members
state.item_name = ""
state.item_description = ""
state.item_tags = ""
state.item_manufacturer = ""
state.item_manufacturer_details = ""
state.is_checked_out = ""
state.check_out_date = ""
state.check_out_poc = ""
state.date_added = ""
state.checkout_status_summary = ""
state.item_image_path = (Path("./frontend/data") /
                         'no_image_available.jpg').absolute().as_posix()

state.image_src = f"data:image/png;base64,{encode_image(image_not_found_path)}"

# Server.state members to track log in status
state.logged_in = False
state.error_message = ""
# Initialize state variables
state.username = ""
state.password = ""

local_image_dir = ''
# --------------------------------------------------------------------------
# Add a route to serve the local image file


@flask_app.route('/media/<path:filename>')
def media(filename):
  return send_from_directory(local_image_dir, filename)


def on_server_exit():
  """
  Callback to handle graceful exiting everything when the main application
  is closed.

  """
  info('Exiting Application ...')
  # Exit camera server
  try:
    camera_process.join()
  except:
    warning(f'Failed to exit camera server!')
  # Exit image server
  try:
    image_process.join()
  except:
    warning(f'Failed to exit image server!')
  sys.exit(0)

  # Function to encode image to base64


# -------------------------------------------------------------------------
#                       UI callback functions
# -------------------------------------------------------------------------
def update_inventory_df():
  info('Update Inventory Data')  # TODO move to debug message
  global inventory_df

  inventory_df = db_client.get_inventory_as_df()

  # -- Remove columns that should not be displayed
  inventory_df = inventory_df.drop('item_image', axis=1)
  inventory_df = inventory_df.drop('manufacturer_contact', axis=1)

  # Rename columns for a more user friendly table view
  inventory_df = inventory_df.rename(columns={'item_name': 'Item',
                                              'item_description': 'Description',
                                              'manufacturer': 'Manufacturer',
                                              'is_checked_out': 'Checked-Out',
                                              'check_out_date': 'Checkout Date',
                                              'check_out_poc': 'Checked-Out By',
                                              'date_added': 'Date Added',
                                              'item_tags': 'Tags'})


def update_item(*args):
  """
  Callback function to be called when scanning a QR code from an existing
  Inventory item.
  The function handles the following activies:
  * Get the decoded QR message from the camera server
  * Parse the message to retrieve the ID
  * Call the database to collect the inventory data corresponding to this
    ID
  * Populate server.state variables with the collected data

  """

  message = str(camera_server.get_decoded_msg())
  valid, id = parse_qr_message(message)
  if valid:
    populate_item_from_id(id)


def populate_item_from_id(id: int):
  """
  Callback function to be called when scanning a QR code from an existing
  Inventory item.
   * Call the database to collect the inventory data corresponding to this
     ID
   * Populate server.state variables with the collected data

  """
  # Get data for scanned item from database
  item_data_df = db_client.get_inventory_item_as_df(id)

  # Extract item data from Dataframe
  item_name = item_data_df.iloc[0]['item_name']
  date_added = item_data_df.iloc[0]['date_added']
  manufacturer = item_data_df.iloc[0]['manufacturer']
  manufacturer_contact = item_data_df.iloc[0]['manufacturer_contact']
  is_checked_out = item_data_df.iloc[0]['is_checked_out']
  check_out_date = item_data_df.iloc[0]['check_out_date']
  check_out_poc = item_data_df.iloc[0]['check_out_poc']
  item_image = item_data_df.iloc[0]['item_image']
  item_description = item_data_df.iloc[0]['item_description']
  item_tags = item_data_df.iloc[0]['item_tags']

  # Handle loading and encoding image from media data
  img_path = Path(str(item_image))
  info(f'Image file path {img_path.absolute().as_posix()}')
  if img_path.exists():
    print(f'Load image file -> {img_path.absolute().as_posix()}')

    state.item_image_path = img_path.absolute().as_posix()
    try:
      # encode_image(img_path.absolute().as_posix())
      state.image_src = f"data:image/png;base64,{
          encode_image(state.item_image_path)}"
    except:
      warning(f'Encoding image url failed for path {state.item_image_path}')

  else:
    warning(f'Failed to locate media file {
            img_path.absolute().as_posix()}')
    state.item_image_path = image_not_found_path
    state.image_src = f"data:image/png;base64,{
        encode_image(image_not_found_path)}"

  # Update state
  state.item_name = f'{item_name}'
  state.item_manufacturer = f'{manufacturer}'
  state.item_manufacturer_details = f'{manufacturer_contact}'
  state.is_checked_out = f'{is_checked_out}'
  state.check_out_date = f'{check_out_date}'
  state.check_out_poc = f'{check_out_poc}'
  state.date_added = f'{date_added}'
  state.item_description = f'{item_description}'
  state.item_tags = f'{item_tags}'
  if is_checked_out:
    state.checkout_status_summary = f'This item is checked out since {
        check_out_date} by {check_out_poc}'
  else:
    state.checkout_status_summary = ' This item has not been checked out.'


def add_inventory_item(*args):
  """
  Handle sequence of actions to add a new item to the Inventory:
  * Check input validity
  * Take image of the item and save file to media
  * Create InventoryItem and add to the database
  * Print bar code sticker

  """
  valid_inputs = True

  # Check input validity
  if state.item_name == "" or state.item_name is None:
    valid_inputs = False

  # Create item and add to database
  if valid_inputs:
    cam_img = camera_server.get_last_frame()
    cam_img_bytes = cam_img.tobytes()
    hash_object = hashlib.sha256(cam_img_bytes)
    hash_hex = hash_object.hexdigest()

    img_path = Path(media_directory) / f'{hash_hex}.png'

    # Save item image to file
    cv.imwrite(img_path, cam_img)

    # Create inventory item
    inventoryItem = InventoryItem(
        item_name=str(state.item_name),
        item_description=str(state.item_description),
        manufacturer=str(state.manufacturer),
        manufacturer_contact=str(state.item_manufacturer_details),
        item_tags=str(state.item_tags),
        item_image_path=img_path)

    # Add item to database
    db_client.add_inventory_item(inventory_item=inventoryItem)


def login(username, password):
  """
  Dummy login callback -> compare user input against static credentials

  TODO -> to be replaced by user database interface
  """
  if username == VALID_USERNAME and password == VALID_PASSWORD:
    state.logged_in = True
    state.error_message = ""
  else:
    state.error_message = "Invalid credentials. Please try again."


def logout(*args):
  """
  Callback function to log out current user
  """
  state.user_name = ''
  state.password = ''
  state.logged_in = False


@state.change("selection")
def selection_change(selection=[], **kwargs):
  global inventory_df
  selected_df = pd.DataFrame(selection)

  if not selected_df.empty:
    if len(selected_df["id"].tolist()) == 1:
      current_id = selected_df["id"].tolist()[0]
      # Print the ID(s) of the selected row(s)
      info(f'Select item with ID: {current_id}')
      populate_item_from_id(current_id)
    elif len(selected_df["id"].tolist()) == 1:
      TODO = True
      # TODO add callback to empty item state variables if no item
      #      is actively selected by the user


# -------------------------------------------------------------------------


def main():
  """
  Main function to start the Inventory application
  """
  # Set global variables for this function
  global camera_thread, camera_server, server, encoded_image, inventory_df
  # -----------------------------------------------------------------------
  # Camera Server
  # -----------------------------------------------------------------------
  # Start the camera server in a background thread
  camera_process = Process(target=camera_server.run)
  camera_process.start()

  # Handle SIGINT
  signal.signal(signal.SIGINT, on_server_exit)
  # Handle termination SIGTERM
  signal.signal(signal.SIGTERM, on_server_exit)
  # -----------------------------------------------------------------------
  # Trame setup
  # -----------------------------------------------------------------------
  state.trame__title = inventory_main_window_title
  state.menu_items = ["add item", "checkout item", "return item"]
  # -----------------------------------------------------------------------
  # Pull inventory data from database
  # -----------------------------------------------------------------------
  update_inventory_df()

  # -----------------------------------------------------------------------
  # Table functions table
  # -----------------------------------------------------------------------

  def filter_inventory_df(query):
    if not query:
      return inventory_df
    query = query.lower()
    filtered_df = inventory_df[inventory_df.astype(str).apply(
        lambda x: x.str.lower().str.contains(query).any(axis=1))]
    return filtered_df

  def update_table():
    filtered_df = filter_inventory_df(state.query)
    headers, rows = vuetify.dataframe_to_grid(
        filtered_df, main_table_header_options)
    state.headers = headers
    state.rows = rows

  state.query = ""
  update_table()

  # -----------------------------------------------------------------------
  # Preparing table
  # -----------------------------------------------------------------------

  headers, rows = vuetify.dataframe_to_grid(inventory_df,
                                            main_table_header_options)
  main_table_config = {
      "headers": ("headers", headers),
      "items": ("rows", rows),
      "v_model": ("selection", []),  # Link selection callback function
      "search": ("query", ""),
      "classes": "elevation-1 ma-4",
      "multi_sort": True,
      "dense": True,
      "show_select": True,
      "single_select": True,  # Only allow a single row to be selected at the time
      "item_key": "id",
  }

  # -----------------------------------------------------------------------
  # GUI
  # -----------------------------------------------------------------------
  # --- Inventory [HOME]
  with RouterViewLayout(server, "/", clicked=update_inventory_df):
    with vuetify.VContainer(fluid=True):
      with vuetify.VRow(classes="justify-center ma-6", v_if="logged_in"):
        fig = vega.Figure(classes="ma-2", style="width: 100%;")
        ctrl.fig_update = fig.update
        vuetify.VDataTable(**main_table_config, v_if="logged_in")
      with vuetify.VRow(v_if="logged_in"):
        with vuetify.VCol():
          vuetify.VCardTitle("Inventory Item")
          with vuetify.VCardText():
            vuetify.VBtn("Update Item")  # TODO add callback
            vuetify.VBtn("Delete Item")  # TODO add callback
          vuetify.VTextField(
              v_model=("item_name", ""),
              label="Item Name",
              placeholder="Enter item name"
          )
          vuetify.VTextField(
              v_model=("item_description", ""),
              label="Item Description",
              placeholder="Enter item description"
          )
          vuetify.VTextField(
              v_model=("item_tags", ""),
              label="Tags",
              placeholder="Enter item tags"
          )
          vuetify.VTextField(
              v_model=("item_manufacturer", ""),
              label="Manufacturer",
              placeholder="Enter item name"
          )
          vuetify.VTextField(
              v_model=("item_manufacturer_details", ""),
              label="Manufacturer Contact Details",
              placeholder="Enter item name"
          )
        with vuetify.VCol():
          with vuetify.VCard(classes="ma-5", max_width="350px", elevation=2):
            fig = vega.Figure(classes="ma-2", style="width: 100%;")
            ctrl.fig_update = fig.update
            vuetify.VImg(
                src=("image_src",),
                max_width="400px",
                classes="mb-5")

  # --- Add inventory
  with RouterViewLayout(server, "/add inventory item"):
    with vuetify.VContainer(fluid=True):
      with vuetify.VRow(v_if="logged_in"):
        with vuetify.VCol():
          vuetify.VCardTitle("Add Inventory Item - Under Construction")
          vuetify.VCardText("Place the item in front of the camera!")
          with vuetify.VCardText():
            vuetify.VBtn("Add item to Inventory", click=add_inventory_item)
          vuetify.VTextField(
              v_model=("item_name", ""),
              label="Item Name",
              placeholder="Enter item name"
          )
          vuetify.VTextField(
              v_model=("item_description", ""),
              label="Item Description",
              placeholder="Enter item description"
          )
          vuetify.VTextField(
              v_model=("item_tags", ""),
              label="Tags",
              placeholder="Enter item tags"
          )
          vuetify.VTextField(
              v_model=("item_manufacturer", ""),
              label="Manufacturer",
              placeholder="Enter item name"
          )
          vuetify.VTextField(
              v_model=("item_manufacturer_details", ""),
              label="Manufacturer Contact Details",
              placeholder="Enter item name"
          )

        with vuetify.VCol():
          # Embed camera stream in this sub-page
          html.Div(html_content_embed_camera_stream_large)

  # --- Checkout inventory
  with RouterViewLayout(server, "/checkout inventory item"):
    with vuetify.VContainer(fluid=True):
      with vuetify.VRow(v_if="logged_in"):
        with vuetify.VCol():
          vuetify.VCardTitle(
              "Checkout Inventory Item - Under Construction")

          with vuetify.VAppBar(elevation=2):
            vuetify.VBtn("Get item code", click=update_item)
            vuetify.VSpacer()
            vuetify.VBtn("Check-out this item")  # Calback TODO

          with vuetify.VCard(classes="ma-5", max_width="350px", elevation=2):
            vuetify.VImg(
                src=("image_src",), max_width="400px", classes="mb-5")

          with vuetify.VCard(classes="ma-5", max_width="550px", elevation=2):
            vuetify.VCardTitle("Inventory")
            vuetify.VCardText("Item Name: {{ item_name }}")
            vuetify.VCardText(
                "Item Description: {{ item_description }}")
            vuetify.VCardText(
                "Manufacturer: {{ item_manufacturer }}")
            vuetify.VCardText(
                "Manufacturer Details: {{ item_manufacturer }}")
            vuetify.VCardText(
                "In Inventory since {{ date_added }}")
            vuetify.VCardText(
                "Check out status: {{ checkout_status_summary }}")

        with vuetify.VCol():
          # Embed camera stream in this sub-page
          html.Div(html_content_embed_camera_stream, v_if="logged_in")

  # --- Return inventory
  with RouterViewLayout(server, "/return inventory item"):
    with vuetify.VContainer(fluid=True):
      with vuetify.VRow(v_if="logged_in"):
        with vuetify.VCol():
          vuetify.VCardTitle("Return Inventory Item - Under Construction")
          with vuetify.VCardText():
            vuetify.VBtn("Get item code", click=update_item)
            vuetify.VBtn("Return this item")  # Callback TODO

          with vuetify.VCard(classes="ma-5", max_width="350px", elevation=2):
            vuetify.VImg(
                src=("image_src",), max_width="400px", classes="mb-5")

          with vuetify.VCard(classes="ma-5", max_width="550px", elevation=5):
            vuetify.VCardTitle("Inventory")
            vuetify.VCardText("Item Name: {{ item_name }}")
            vuetify.VCardText("Item Description: {{ item_description }}")
            vuetify.VCardText("Manufacturer: {{ item_manufacturer }}")
            vuetify.VCardText("Manufacturer Details: {{ item_manufacturer }}")
            vuetify.VCardText("In Inventory since {{ date_added }}")
            vuetify.VCardText(
                "Check out status: {{ checkout_status_summary }}")
        with vuetify.VCol():
          # Embed camera stream in this sub-page
          html.Div(html_content_embed_camera_stream)

  # Main page content
  with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text(inventory_page_title)

    if enableLogin:
      # Login form
      with layout.content:
        with vuetify.VCard(max_width="400px", v_if="!logged_in", outlined=True, classes="mx-auto mt-10"):
          with vuetify.VCardTitle():
            vuetify.VCardTitle("Login")
          with vuetify.VCardText():
            vuetify.VTextField(label="Username", v_model="username")
            vuetify.VTextField(
                label="Password", v_model="password", type="password")
          vuetify.VSpacer()
          vuetify.VBtn("Login", click=lambda: login(
              state.username, state.password), block=True)
          vuetify.VSpacer()
          vuetify.VCardText(v_if="error_message",
                            classes="red--text text-center")
    else:
      state.username = VALID_USERNAME
      state.logged_in = True

    with layout.toolbar:
      vuetify.VSpacer()
      vuetify.VTextField(
          v_model=("query",),
          placeholder="Search Inventory Item",
          dense=True,
          v_if="logged_in",
          hide_details=True,
          prepend_icon="mdi-magnify",
      )
      vuetify.VSpacer()
      vuetify.VBtn("Log out", v_if="logged_in", click=logout)

    with layout.content:
      with vuetify.VContainer():
        router.RouterView()

    # add router buttons to the drawer
    with layout.drawer:
      with vuetify.VList(shaped=True, v_if="logged_in", v_model=("selectedRoute", 0)):
        vuetify.VSubheader("Inventory Actions")

        with vuetify.VListItem(to="/", clicked=update_inventory_df):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-home")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Inventory", clicked=update_inventory_df)

        with vuetify.VListItem(to="/add inventory item", clicked=update_inventory_df):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-plus", v_if="logged_in")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Add Inventory Item", v_if="logged_in")

        with vuetify.VListItem(to="/checkout inventory item"):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-check", v_if="logged_in")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Checkout Inventory Item", v_if="logged_in")

        with vuetify.VListItem(to="/return inventory item"):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-arrow-right", v_if="logged_in")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Return Inventory Item", v_if="logged_in")

  # -----------------------------------------------------------------------
  # Callbacks
  # -----------------------------------------------------------------------
  @ state.change("query")
  def on_query_change(query, **kwargs):
    update_table()

  # -----------------------------------------------------------------------
  # Start server
  # -----------------------------------------------------------------------
  server.start(host=frontend_host_ip,
               port=frontend_host_port)

  # Close camera thread
  camera_process.join()


if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  # Start main application
  main()
