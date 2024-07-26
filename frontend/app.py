"""

Inventory frontend main application

"""
import numpy as np
import pandas as pd
import altair as alt
import cv2 as cv
from pathlib import Path
from itertools import cycle
from trame.widgets import vuetify, vega
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.ui.router import RouterViewLayout
from trame.widgets import vuetify, router, html
from trame.app import get_server
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
from backend.camera_server.camera_app import CameraServer
from backend.InventoryItem import InventoryItem
from backend.database_config import (qr_iden_str,
                                     qr_id_iden_str,
                                     qr_msg_delimiter)
# ---- Frontend imports
from frontend.frontend_config import (inventory_page_title,
                                      inventory_main_window_title,
                                      main_table_header_options,
                                      html_content_embed_camera_stream,
                                      html_content_embed_camera_stream_large,
                                      media_directory)

# --------------------------------------------------------------------------
#                       [Global Variables]
# --------------------------------------------------------------------------

# Create global handle for the camera server running in a background
# process
camera_process = None

# Create camera server instance
camera_server = CameraServer()

# --------------------------------------------------------------------------


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
  sys.exit(0)


def parse_qr_message(msg: str):
  """
  Test function to get the decoded QR message from the camera server
  print it to the terminal
  """
  is_msg_valid = False
  item_id = -1

  # First check if all substring identifier are contained in the message
  if qr_iden_str in msg and qr_id_iden_str in msg and qr_msg_delimiter in msg:
    try:
      # Remove all identifier strings and convert to integer
      # Step 1: Split the test_str using the delimiter
      parts = msg.split(qr_msg_delimiter)

      # Step 2: Remove qr_iden_str and qr_id_iden_str, extract the numerical part
      remaining_str = parts[1].replace(qr_id_iden_str, '')

      # Step 3: Convert the remaining part to an integer
      item_id = int(remaining_str)
      is_msg_valid = True
    except:
      warning('Parsing QR code message failed. ')

  return is_msg_valid, item_id


def main():
  global camera_thread, camera_server
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

  server = get_server(client_type="vue2")
  state, ctrl = server.state, server.controller

  state.trame__title = inventory_main_window_title
  state.menu_items = ["add item", "checkout item", "return item"]
  # -----------------------------------------------------------------------
  # Database connection
  # -----------------------------------------------------------------------
  # Create a DatabaseClient instance and connect to the inventory database
  db_client = DataBaseClient(host=database_host)
  # -----------------------------------------------------------------------
  # Pull inventory data from database
  # -----------------------------------------------------------------------
  inventory_df = db_client.get_inventory_as_df()

  # -----------------------------------------------------------------------
  # Preparing table
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
  state.item_image = None
  state.item_image_path = None

  # Function to change grab the item data for the ID from a currently read
  # QR code from the database and update the respective fields
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
      if img_path.exists():
        info(f'Load image file {img_path.absolute().as_posix()}')
        encoded_image = base64.b64encode(img_path.read_bytes()).decode("utf-8")
        state.item_image = f"data:image/png;base64,{encoded_image}"
        state.item_image_path = img_path.absolute().as_posix()
      else:
        warning(f'Failed to locate media file {
                img_path.absolute().as_posix()}')
        state.item_image = None

      # Update state
      state.item_name = f'{item_name} | Inventory ID {id}'
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
  # -----------------------------------------------------------------------
  # Preparing table
  # -----------------------------------------------------------------------

  headers, rows = vuetify.dataframe_to_grid(inventory_df,
                                            main_table_header_options)
  main_table_config = {
      "headers": ("headers", headers),
      "items": ("rows", rows),
      "v_model": ("selection", []),
      "search": ("query", ""),
      "classes": "elevation-1 ma-4",
      "multi_sort": True,
      "dense": True,
      "show_select": True,
      "single_select": False,
      "item_key": "id",
  }

  # -----------------------------------------------------------------------
  # GUI
  # -----------------------------------------------------------------------

  with RouterViewLayout(server, "/"):
    with vuetify.VRow(classes="justify-center ma-6"):
      fig = vega.Figure(classes="ma-2", style="width: 100%;")
      ctrl.fig_update = fig.update
    vuetify.VDataTable(**main_table_config)

  # --- Add inventory
  with RouterViewLayout(server, "/add inventory item"):
    with vuetify.VContainer(fluid=True):
      with vuetify.VRow():
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
          # Display the item image
          if state.item_image is not None:
            html.Img(src=state.item_image, alt="{{ item_name }}",
                     style="width: 100%; max-width: 300px;")

  # --- Checkout inventory
  with RouterViewLayout(server, "/checkout inventory item"):
    with vuetify.VContainer(fluid=True):
      with vuetify.VRow():
        with vuetify.VCol():
          vuetify.VCardTitle("Checkout Inventory Item - Under Construction")
          with vuetify.VCardText():
            vuetify.VBtn("Get item code", click=update_item)
            vuetify.VBtn("Check-out this item")  # Calback TODO
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
          html.Img(src=state.item_image_path, v_if=True)

  # --- Return inventory
  with RouterViewLayout(server, "/return inventory item"):
    with vuetify.VContainer(fluid=True):
      with vuetify.VRow():
        with vuetify.VCol():
          vuetify.VCardTitle("Return Inventory Item - Under Construction")
          with vuetify.VCardText():
            vuetify.VBtn("Get item code", click=update_item)
            vuetify.VBtn("Return this item")  # Callback TODO
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
          if state.item_image is not None:
            html.Img(src=state.item_image, alt="{{ item_name }}",
                     style="width: 100%; max-width: 300px;")

  # Main page content
  with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text(inventory_page_title)
    with layout.toolbar:
      vuetify.VSpacer()
      vuetify.VTextField(
          v_model=("query",),
          placeholder="Search",
          dense=True,
          hide_details=True,
          prepend_icon="mdi-magnify",
      )

    with layout.content:
      with vuetify.VContainer():
        router.RouterView()

    # add router buttons to the drawer
    with layout.drawer:
      with vuetify.VList(shaped=True, v_model=("selectedRoute", 0)):
        vuetify.VSubheader("Inventory Actions")

        with vuetify.VListItem(to="/"):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-home")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Inventory")

        with vuetify.VListItem(to="/add inventory item"):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-plus")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Add Inventory Item")

        with vuetify.VListItem(to="/checkout inventory item"):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-check")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Checkout Inventory Item")

        with vuetify.VListItem(to="/return inventory item"):
          with vuetify.VListItemIcon():
            vuetify.VIcon("mdi-arrow-right")
          with vuetify.VListItemContent():
            vuetify.VListItemTitle("Return Inventory Item")

  # -----------------------------------------------------------------------
  # Callbacks
  # -----------------------------------------------------------------------
  @ state.change("query")
  def on_query_change(query, **kwargs):
    update_table()

  # -----------------------------------------------------------------------
  # Start server
  # -----------------------------------------------------------------------
  server.start()

  # Close camera thread
  camera_process.join()


if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  main()
