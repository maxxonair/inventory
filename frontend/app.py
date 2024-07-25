"""

Inventory frontend main application

"""
import numpy as np
import pandas as pd
import altair as alt
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

# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# ---- Backend imports
from backend.DataBaseClient import DataBaseClient
from backend.database_config import database_host
from backend.camera_server.camera_app import CameraServer
from backend.database_config import (qr_iden_str,
                                     qr_id_iden_str,
                                     qr_msg_delimiter)
# ---- Frontend imports
from frontend.frontend_config import (inventory_page_title,
                                      inventory_main_window_title,
                                      main_table_header_options,
                                      html_content_embed_camera_stream)


def add_item_action():
  info('Start action: add item')


def checkout_item_action():
  info('Start action: checkout item')


def return_item_action():
  info('Start action: return item')


# Create global handle for the camera server running in a background
# process
camera_process = None

# Create camera server instance
camera_server = CameraServer()


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
  client = DataBaseClient(host=database_host)
  # -----------------------------------------------------------------------
  # Pull inventory data from database
  # -----------------------------------------------------------------------
  inventory_df = client.get_inventory_as_df()

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
  state.item_name = ""
  state.item_details = ""

  # Function to change grab the item data for the ID from a currently read
  # QR code from the database and update the respective fields
  def update_item(*args):
    message = str(camera_server.get_decoded_msg())
    valid, id = parse_qr_message(message)
    if valid:
      item_data_df = client.get_inventory_item_as_df(id)
      item_name = item_data_df.iloc[0]['item_name']
      date_added = item_data_df.iloc[0]['date_added']
      manufacturer = item_data_df.iloc[0]['manufacturer']
      state.item_name = f'{item_name} [ID {id}]'
      state.item_details = f'Manufacturer: {
          manufacturer} \n || Date added: {date_added}'
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
    with vuetify.VCard():
      vuetify.VCardTitle("Add Inventory Item")
      with vuetify.VCardText():
        vuetify.VBtn("Take me back", click="$router.back()")

  # --- Checkout inventory
  with RouterViewLayout(server, "/checkout inventory item"):
    with vuetify.VCard():
      vuetify.VCardTitle("Checkout Inventory Item - Under Construction")
      with vuetify.VCardText():
        vuetify.VBtn("Take me back", click="$router.back()")
      # Embed camera stream in this sub-page
      with vuetify.VCard():
        html.Div(html_content_embed_camera_stream)

  # --- Return inventory
  with RouterViewLayout(server, "/return inventory item"):
    with vuetify.VCard():
      vuetify.VCardTitle("Return Inventory Item - Under Construction")
      with vuetify.VCardText():
        vuetify.VBtn("Take me back", click="$router.back()")
      with vuetify.VCard(classes="ma-5", max_width="550px", elevation=5):
        vuetify.VCardTitle("[Inventory]")
        vuetify.VCardSubtitle("Item Name: {{ item_name }}")
        vuetify.VCardText("{{ item_details }}")
      with vuetify.VCardText():
        vuetify.VBtn("Get item code", click=update_item)
      # Embed camera stream in this sub-page
      with vuetify.VCard():
        html.Div(html_content_embed_camera_stream)

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
