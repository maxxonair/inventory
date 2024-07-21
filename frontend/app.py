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
from trame.widgets import vuetify, router
from trame.app import get_server
import sys
import os
import logging
from logging import info

# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# ---- Backend imports
from backend.DataBaseClient import DataBaseClient
from backend.database_config import database_host

# ---- Frontend imports
from frontend.frontend_config import (inventory_page_title,
                                      inventory_main_window_title,
                                      main_table_header_options)


def add_item_action():
  info('Start action: add item')


def checkout_item_action():
  info('Start action: checkout item')


def return_item_action():
  info('Start action: return item')


def main():
  # -----------------------------------------------------------------------
  # Camera setup
  # -----------------------------------------------------------------------
  # TODO: Launch camera server in background thread

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
        # Embed the live camera feed
        vuetify.VImg(src="http://localhost:5000/video_feed",
                     classes="my-4", style="width: 100%; height: auto;")
        vuetify.VBtn("Take me back", click="$router.back()")

  # --- Checkout inventory
  with RouterViewLayout(server, "/checkout inventory item"):
    with vuetify.VCard():
      vuetify.VCardTitle("Checkout Inventory Item - Under Construction")
      with vuetify.VCardText():
        vuetify.VBtn("Take me back", click="$router.back()")

  # --- Return inventory
  with RouterViewLayout(server, "/return inventory item"):
    with vuetify.VCard():
      vuetify.VCardTitle("Return Inventory Item - Under Construction")
      with vuetify.VCardText():
        vuetify.VBtn("Take me back", click="$router.back()")

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


if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)
  main()
