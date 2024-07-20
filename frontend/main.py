"""

Inventory front end main

"""
import numpy as np
import pandas as pd
import altair as alt
from itertools import cycle
from trame.widgets import vuetify, vega
from trame.ui.vuetify import SinglePageLayout
from trame.app import get_server
import sys
import os

# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from backend.DataBaseClient import DataBaseClient
from backend.database_config import database_host

# -----------------------------------------------------------------------------
# ---- SETUP
# -----------------------------------------------------------------------------

INVENTORY_TITLE = "B.I.G Material Library"


# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# --------------------------------------------------------------------------------
# Database connection
# --------------------------------------------------------------------------------
# Create a DatabaseClient instance and connect to the inventory database
client = DataBaseClient(host=database_host)
# --------------------------------------------------------------------------------
# Making dataframe
# --------------------------------------------------------------------------------
np.random.seed(4)
INVENTORY_DF = None


def fetch_data(samples=15):
  global INVENTORY_DF
  INVENTORY_DF = client.get_inventory_as_df()
  return INVENTORY_DF


fetch_data()

# --------------------------------------------------------------------------------
# Preparing table
# --------------------------------------------------------------------------------
header_options = {"item_name": {"sortable": False}}
headers, rows = vuetify.dataframe_to_grid(INVENTORY_DF, header_options)

table = {
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

# --------------------------------------------------------------------------------
# Describing chart
# --------------------------------------------------------------------------------


# @state.change("selection")
# def selection_change(selection=[], **kwargs):
#   global INVENTORY_DF
#   selected_df = pd.DataFrame(selection)

#   # Chart
#   chart_data = INVENTORY_DF.loc[
#       :, ["date_time_naive", "item_name", "item_description", "item_class"]
#   ].assign(source="total")

#   if not selected_df.empty:
#     selected_data = selected_df.loc[
#         :, ["date_time_naive", "item_name", "item_description", "item_class"]
#     ].assign(source="selection")
#     chart_data = pd.concat([chart_data, selected_data])

#   chart_data = pd.melt(
#       chart_data,
#       id_vars=["date_time_naive", "source"],
#       var_name="item",
#       value_name="quantity",
#   )
#   chart = (
#       alt.Chart(chart_data)
#       .mark_bar()
#       .encode(
#           x=alt.X("item:O"),
#           y=alt.Y("sum(quantity):Q", stack=False),
#           color=alt.Color("source:N", scale=alt.Scale(
#               domain=["total", "selection"])),
#       )
#   ).properties(width="container", height=100)

#   ctrl.fig_update(chart)


# --------------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
  layout.title.set_text(INVENTORY_TITLE)
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
    with vuetify.VRow(classes="justify-center ma-6"):
      fig = vega.Figure(classes="ma-2", style="width: 100%;")
      ctrl.fig_update = fig.update
    vuetify.VDataTable(**table)

# -----------------------------------------------------------------------------
# Start server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
  server.start()
