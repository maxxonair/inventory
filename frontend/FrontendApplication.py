from trame.app import get_server
from trame.widgets import vuetify, vega, router, html
from trame.widgets.vuetify import (VBtn, VSpacer, VTextField, VCardText, VIcon,
                                   VCol, VRow, VContainer, VImg, VCardTitle,
                                   VCard, VList, VListItemIcon, VListItem,
                                   VListItemTitle, VListItemContent
                                   )
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.ui.router import RouterViewLayout

from multiprocessing import Process, Manager, Pipe, Value
import time
import cv2 as cv
import base64
import hashlib
import multiprocessing
from pathlib import Path
from logging import info, error, warning, debug
import logging
import sys
import pandas as pd
import os

# --------------------------------------------------------------------------
#                           [Inventory Imports]
# --------------------------------------------------------------------------
# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# ---- Backend imports
from backend.DataBaseClient import DataBaseClient
from backend.database_config import database_host
from backend.InventoryItem import InventoryItem
from backend.InventoryUser import InventoryUser, UserPrivileges
from backend.CameraServer import CameraServer

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
                                      enableLogin,
                                      enableRunForDebug,
                                      disableDatabaseColumnFilter)


class FrontendApplication:

  # -----------------------------------------------------------------------------
  #                 [INIT]
  # -----------------------------------------------------------------------------
  def __init__(self, db_client: DataBaseClient, camera_server: CameraServer = None):
    # -----------------------------------------------------------------------
    # Main application server
    # -----------------------------------------------------------------------
    self.server = get_server(client_type="vue2")
    self.state, self.ctrl = self.server.state, self.server.controller

    # Create server.state members
    self.state.selected_item_id = None
    self.state.dummy_id = 0
    self.state.parsed_item_id = None
    self.state.item_name = ""
    self.state.item_description = ""
    self.state.item_tags = ""
    self.state.item_manufacturer = ""
    self.state.item_manufacturer_details = ""
    self.state.is_checked_out = ""
    self.state.check_out_date = ""
    self.state.check_out_poc = ""
    self.state.date_added = ""
    self.state.checkout_status_summary = ""
    self.state.item_image_path = (Path("./frontend/data") /
                                  'no_image_available.jpg').absolute().as_posix()

    self.state.image_src = f"data:image/png;base64,{
        self.encode_image_from_path(image_not_found_path)}"
    self.state.display_img_src = f"data:image/png;base64,{
        self.encode_image_from_path(image_not_found_path)}"

    self.state.scan_bt_color = 'primary'

    # Server.state members to track log in status
    self.state.logged_in = False
    self.state.error_message = ""

    # Initialize state variables
    self.state.username = ""
    self.state.password = ""
    self.state.privileges = UserPrivileges.GUEST.value

    # Initialize user privilege action flags
    self.state.enable_privilege_add_item = False
    self.state.enable_privilege_delete_item = False
    self.state.enable_privilege_mod_item = False
    self.state.enable_privilege_settings = False

    self.state.logged_in = False
    self.state.show_img_swap_page = False

    local_image_dir = ''

    self.db_client = db_client

    # -----------------------------------------------------------------------
    # -- TRAME WINDOW SETUP
    # -----------------------------------------------------------------------
    self.state.trame__title = inventory_main_window_title
    self.state.menu_items = ["add item", "checkout item", "return item"]
    # -----------------------------------------------------------------------
    # -- PULL INVENTORY DATA
    # -----------------------------------------------------------------------
    self.update_inventory_df()

    # -----------------------------------------------------------------------
    # -- TABLE FUNCTIONS
    # -----------------------------------------------------------------------

    def filter_inventory_df(query):
      """
      Filter invetory dataframe by user search query

      """
      if not query:
        return self.inventory_df
      else:
        query = query.lower()
        filtered_df = self.inventory_df[self.inventory_df.astype(str).apply(
            lambda x: x.str.lower().str.contains(query).any(axis=1))]
        return filtered_df

    def update_table():
      """
      Update the table view
      """
      filtered_df = filter_inventory_df(self.state.query)
      headers, rows = vuetify.dataframe_to_grid(
          filtered_df, main_table_header_options)
      self.state.headers = headers
      self.state.rows = rows

    self.state.query = ""
    update_table()

    def delete_inventory_item(self, *args):
      """
      Callback function to delete the currently selected inventory item
      """
      # Only delete item if one is selected
      if self.state.selected_item_id is not None:
        # Command: DELETE item from inventory
        db_client.delete_inventory_item(int(self.state.selected_item_id))

        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        # Update the table view
        update_table()

    def update_inventory_item(self, *args):
      """
      Callback function to update the currently selected inventory item
      """
      valid_data, inventoryItem = self.read_item_user_input_to_object()

      if valid_data:

        print(f'[update_inventory_item] -- {inventoryItem.manufacturer}')

        # Update the item in the database
        db_client.update_inventory_item(inventory_item=inventoryItem,
                                        id=self.state.selected_item_id)

        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        # Update the table view
        update_table()
      else:
        error('Adding Inventory item failed. Invalid user inputs')

    def add_inventory_item(self, *args):
      """
      Handle sequence of actions to add a new item to the Inventory:
      * Check input validity
      * Take image of the item and save file to media
      * Create InventoryItem and add to the database
      * Print bar code sticker

      """

      valid_data, inventoryItem = self.read_item_user_input_to_object()

      if valid_data:
        # If an image has been captured
        # -> Save image to file
        # -> Update image path in item data
        if display_img is not None:
          cam_img_bytes = display_img.tobytes()
          hash_object = hashlib.sha256(cam_img_bytes)
          hash_hex = hash_object.hexdigest()

          img_path = Path(media_directory) / f'{hash_hex}.png'

          # Save item image to file
          cv.imwrite(img_path, display_img)

          # Update image path in InventoryItem instance
          inventoryItem.set_img_path(img_path)

        # Add item to database
        db_client.add_inventory_item(inventoryItem)

        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        update_table()
      else:
        # TODO Add error field to show in UI
        error('Adding Inventory item failed. Invalid user inputs')

    def checkout_item(*args):

      ret = self.inventory_item.set_checked_out(self.state.username)

      if ret:
        # Update checkout status in database
        db_client.update_inventory_item_checkout_status(id=self.state.parsed_item_id,
                                                        inventory_item=self.inventory_item)
        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        update_table()
      else:
        warning('Updating checkout status failed. No Point of Contact provided')

    def checkin_item(self, *args):

      self.inventory_item.set_checked_in(self.state.username)

      # Update checkout status in database
      db_client.update_inventory_item_checkout_status(id=self.state.parsed_item_id,
                                                      inventory_item=self.inventory_item)
      # Update the dataframe so the table reflects the updated DB state
      self.update_inventory_df()

      update_table()
    # -----------------------------------------------------------------------
    # -- GUI
    # -----------------------------------------------------------------------

    # Prepare table elements and configuration
    headers, rows = vuetify.dataframe_to_grid(self.inventory_df,
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

    # --- Inventory [HOME]
    with RouterViewLayout(self.server, "/", clicked=self.update_inventory_df):
      with vuetify.VContainer(fluid=True):
        with VRow(classes="justify-center ma-6", v_if="logged_in"):
          fig = vega.Figure(classes="ma-2", style="width: 100%;")
          self.ctrl.fig_update = fig.update
          vuetify.VDataTable(**main_table_config, v_if="logged_in")
        with VRow(v_if="logged_in"):
          with VCol():
            with VRow(v_if="logged_in", style="margin-bottom: 16px;"):
              VIcon('mdi-swap-horizontal',
                    v_if="enable_privilege_mod_item")
              VBtn("Update Item",
                   click=update_inventory_item,
                   v_if="enable_privilege_mod_item")
            with VRow(v_if="logged_in", style="margin-bottom: 16px;"):
              VIcon('mdi-trash-can-outline',
                    v_if="enable_privilege_delete_item")
              VBtn("Delete Item",
                   click=delete_inventory_item,
                   v_if="enable_privilege_delete_item")
            with VRow(v_if="logged_in"):
              fig_item = vega.Figure(classes="ma-2", style="width: 100%;")
              self.ctrl.view_update = fig_item.update
              with vuetify.VContainer(fluid=True):
                VTextField(
                    v_model=("item_name", ""),
                    label="Item Name",
                    placeholder="Enter item name"
                )
                VTextField(
                    v_model=("item_description", ""),
                    label="Item Description",
                    placeholder="Enter item description"
                )
                VTextField(
                    v_model=("item_tags", ""),
                    label="Tags",
                    placeholder="Enter item tags"
                )
                VTextField(
                    v_model=("item_manufacturer", ""),
                    label="Manufacturer",
                    placeholder="Enter item name",
                )
                VTextField(
                    v_model=("item_manufacturer_details", ""),
                    label="Manufacturer Details",
                    placeholder="Enter item name"
                )
          with VCol():
            VImg(
                src=("image_src",),
                max_width="400px",
                classes="mb-5")

          with VRow(v_if="logged_in"):
            VBtn("Change image",
                 click=self.switch_show_img_change,
                 v_if="enable_privilege_mod_item")
          with VRow(v_if="show_img_swap_page"):
            with VCard(classes="ma-5", v_if="show_img_swap_page",
                       max_width="350px", elevation=2):
              fig = vega.Figure(classes="ma-2", style="width: 100%;")
              self.ctrl.fig_update = fig.update
              VCardText("Current Item Image")
              VImg(
                  src=("image_src",),
                  max_width="400px",
                  classes="mb-5")
              with vuetify.VAppBar(elevation=0):
                VIcon("mdi-arrow-up-bold-box", size=35, left=False)
                VBtn("Change Current Image",
                     click=self.update_item_image_with_capture)
                VIcon("mdi-arrow-up-bold-box", size=35, left=True)
              VCardText("Captured Image")
              VImg(
                  src=("display_img_src",),
                  max_width="400px",
                  classes="mb-5")
            with VCol(v_if="show_img_swap_page"):
              VCardText("Camera stream")
              VCardText("Place the item in front of the camera!")
              # Embed camera stream in this sub-page
              html.Div(html_content_embed_camera_stream)
              with VRow(v_if="show_img_swap_page", style="margin-top: 10px;"):
                VIcon('mdi-camera-plus-outline', left=False)
                VBtn("Capture Image",
                     click=self.capture_image,
                     variant='outlined')
                VIcon('mdi-camera-plus-outline', left=True)

    # --- Add inventory
    with RouterViewLayout(self.server, "/add inventory item", v_if="enable_privilege_add_item"):
      with vuetify.VContainer(fluid=True):
        with VRow(v_if="logged_in"):
          with VCol():
            # TODO Update title
            VCardTitle("Add Inventory Item - Under Construction")
            VCardText("Place the item in front of the camera!")
            with VCardText():
              VBtn("Add item to Inventory", click=add_inventory_item)
              VBtn("Capture Image", click=self.capture_image)
            VTextField(
                v_model=("item_name", ""),
                label="Item Name",
                placeholder="Enter item name"
            )
            VTextField(
                v_model=("item_description", ""),
                label="Item Description",
                placeholder="Enter item description"
            )
            VTextField(
                v_model=("item_tags", ""),
                label="Tags",
                placeholder="Enter item tags"
            )
            VTextField(
                v_model=("item_manufacturer", ""),
                label="Manufacturer",
                placeholder="Enter Manufacturer"
            )
            VTextField(
                v_model=("item_manufacturer_details", ""),
                label="Manufacturer Contact Details",
                placeholder="Enter Manufacturer Details"
            )
            # Display captured frames
            VCardText("Item image")
            VImg(
                src=("display_img_src",),
                max_width="600px",
                classes="mb-5")

          with VCol():
            # Embed camera stream in this sub-page
            html.Div(html_content_embed_camera_stream_large)

    # --- Checkout inventory
    with RouterViewLayout(self.server, "/checkout inventory item"):
      with vuetify.VContainer(fluid=True):
        with VRow(v_if="logged_in"):
          fig_item = vega.Figure(classes="ma-2", style="width: 100%;")
          self.ctrl.view_update = fig_item.update
          with VCol():
            VCardTitle(
                "Checkout Inventory Item")

            VBtn("Check-out this item", click=checkout_item)

            with VCard(classes="ma-5", max_width="350px", elevation=2):
              VImg(
                  src=("image_src",), max_width="400px", classes="mb-5")

            with VCard(classes="ma-5", max_width="550px", elevation=2):
              VCardTitle("Inventory")
              VCardText("Item Name: {{ item_name }}")
              VCardText(
                  "Item Description: {{ item_description }}")
              VCardText(
                  "Manufacturer: {{ item_manufacturer }}")
              VCardText(
                  "Manufacturer Details: {{ item_manufacturer_details }}")
              VCardText(
                  "In Inventory since {{ date_added }}")
              VCardText(
                  "Check out status: {{ checkout_status_summary }}")

          with VCol():
            with VRow(v_if="logged_in", style="margin-top: 10px;"):
              VIcon('mdi-qrcode-scan', left=True, size=35)
              VCardText("Place the item QR code in front of the camera!")
            # Embed camera stream in this sub-page
            html.Div(html_content_embed_camera_stream, v_if="logged_in")

    # --- Return inventory
    with RouterViewLayout(self.server, "/return inventory item"):
      with vuetify.VContainer(fluid=True):
        with VRow(v_if="logged_in"):
          with VCol():
            # TODO Update title
            VCardTitle("Return Inventory Item - Under Construction")

            VBtn("Return this item", click=checkin_item)

            with VCard(classes="ma-5", max_width="350px", elevation=2):
              VImg(
                  src=("image_src",), max_width="400px", classes="mb-5")

            with VCard(classes="ma-5", max_width="550px", elevation=5):
              VCardTitle("Inventory")
              VCardText("Item Name: {{ item_name }}")
              VCardText("Item Description: {{ item_description }}")
              VCardText("Manufacturer: {{ item_manufacturer }}")
              VCardText(
                  "Manufacturer Details: {{ item_manufacturer_details }}")
              VCardText("In Inventory since {{ date_added }}")
              VCardText(
                  "Check out status: {{ checkout_status_summary }}")
          with VCol():
            VCardText("Place the item QR code in front of the camera!")
            # Embed camera stream in this sub-page
            html.Div(html_content_embed_camera_stream)

    # --- Settings
    with RouterViewLayout(self.server, "/settings"):
      with vuetify.VContainer(fluid=True):
        with VRow(v_if="logged_in"):
          with VCol():
            # TODO Update title
            VCardTitle("Settings - Under Construction")

    # Main page content
    with SinglePageWithDrawerLayout(self.server) as layout:
      layout.title.set_text(inventory_page_title)
      if enableLogin:
        # Login form
        with layout.content:
          with VCard(max_width="400px", v_if="!logged_in", outlined=True,
                     classes="mx-auto mt-10"):
            with VCardTitle():
              VCardTitle("Login")
            with VCardText():
              VTextField(label="Username", v_model="username")
              VTextField(
                  label="Password", v_model="password", type="password")
            VSpacer()
            VBtn("Login", click=lambda: self.login(
                self.state.username, self.state.password), block=True)
            VSpacer()
            VCardText("{{ error_message }}",
                      classes="red--text text-center")
      else:
        # Debug option - Log in disabled
        # Force logged in state with debug user
        self.state.username = self.VALID_USERNAME
        self.state.logged_in = True

      with layout.toolbar:
        VSpacer()
        VTextField(
            v_model=("query",),
            placeholder="Search Inventory Item",
            dense=False,
            v_if="logged_in",
            hide_details=True,
            prepend_icon="mdi-magnify",
        )
        VSpacer()
        vuetify.VSwitch(
            v_model="$vuetify.theme.dark",
            hide_detials=True,
            dense=True,
        )

        VBtn("CSV Export", v_if="logged_in")  # TODO Callback to be added
        with VCard(classes="ma-5"):
          with VRow(v_if="logged_in"):
            with VCol():
              VIcon('mdi-account', left=False, size=45)
            with VCol():
              VCardText("{{ username }}")

        VBtn("Log out", v_if="logged_in", click=self.logout)

      with layout.content:
        with vuetify.VContainer():
          router.RouterView()

      # add router buttons to the drawer
      with layout.drawer:
        with vuetify.VList(shaped=True, v_if="logged_in", v_model=("selectedRoute", 0)):
          vuetify.VSubheader("Inventory Actions")

          with VListItem(to="/", clicked=self.update_inventory_df):
            with VListItemIcon():
              VIcon("mdi-home")
            with VListItemContent():
              VListItemTitle("Inventory", clicked=self.update_inventory_df)

          with VListItem(to="/add inventory item",
                         clicked=self.update_inventory_df,
                         v_if="enable_privilege_add_item"):
            with VListItemIcon():
              VIcon("mdi-plus", v_if="logged_in")
            with VListItemContent():
              VListItemTitle("Add Inventory Item", v_if="logged_in")

          with VListItem(to="/checkout inventory item"):
            with VListItemIcon():
              VIcon("mdi-check", v_if="logged_in")
            with VListItemContent():
              VListItemTitle("Checkout Inventory Item", v_if="logged_in")

          with VListItem(to="/return inventory item"):
            with VListItemIcon():
              VIcon("mdi-arrow-right", v_if="logged_in")
            with VListItemContent():
              VListItemTitle("Return Inventory Item", v_if="logged_in")

          with VListItem(to="/settings",
                         v_if="enable_privilege_add_item"):
            with VListItemIcon():
              VIcon("mdi-cog", v_if="logged_in")
            with VListItemContent():
              VListItemTitle("Settings", v_if="logged_in")

    # -----------------------------------------------------------------------
    # Internal Callbacks
    # -----------------------------------------------------------------------
    @ self.state.change("query")
    def on_query_change(query, **kwargs):
      update_table()

    @ self.state.change('item_name')
    def update_item_textfields(**kwargs):
      self.ctrl.view_update()

    @ self.state.change("selection")
    def selection_change(selection=[], **kwargs):
      """
      Callback function that is called every time the user selects an item in
      the main table
      """
      selected_df = pd.DataFrame(selection)

      if not selected_df.empty:
        if len(selected_df["id"].tolist()) == 1:
          current_id = selected_df["id"].tolist()[0]
          info(f'Select item with ID: {current_id}')

          # Update state data ID
          self.state.selected_item_id = current_id

          # Populate state data with item information
          self.populate_item_from_id(current_id)

          # Save a complete and global copy of this item
          self.inventory_item.populate_from_df(
              item_data_df=self.db_client.get_inventory_item_as_df(current_id))

        elif len(selected_df["id"].tolist()) == 1:
          TODO = True
          # TODO add callback to empty item state variables if no item
          #      is actively selected by the user
  # -----------------------------------------------------------------------------
  #                 [FUNCTIONS]
  # -----------------------------------------------------------------------------

  def encode_image_from_path(self, image_path):
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')

  def encode_image(self, cv_image):
      # Convert the OpenCV image (NumPy array) to bytes
    _, buffer = cv.imencode('.jpg', cv_image)
    image_bytes = buffer.tobytes()

    # Encode the bytes to base64
    return base64.b64encode(image_bytes).decode('utf-8')
  # -------------------------------------------------------------------------
  #   UI CALLBACK FUNCTIONS
  # -------------------------------------------------------------------------

  def update_inventory_df(self):
    """
    Update DataFrame that holds the compolete Inventory content

    """
    debug('Update Inventory Data')

    self.inventory_df = self.db_client.get_inventory_as_df()

    if not disableDatabaseColumnFilter:
      # -- Remove columns that should not be displayed
      self.inventory_df = self.inventory_df.drop('item_image', axis=1)
      self.inventory_df = self.inventory_df.drop(
          'manufacturer_contact', axis=1)

      # Rename columns for a more user friendly table view
      self.inventory_df = self.inventory_df.rename(columns={'item_name': 'Item',
                                                            'item_description': 'Description',
                                                            'manufacturer': 'Manufacturer',
                                                            'is_checked_out': 'Checked-Out',
                                                            'check_out_date': 'Checkout Date',
                                                            'check_out_poc': 'Checked-Out By',
                                                            'date_added': 'Date Added',
                                                            'item_tags': 'Tags'})

  def populate_item_from_id(self, id: int):
    """
    Callback function to be called when scanning a QR code from an existing
    Inventory item.
    * Call the database to collect the inventory data corresponding to this
      ID
    * Populate server.state variables with the collected data

    """
    # Get data for scanned item from database
    item_data_df = self.db_client.get_inventory_item_as_df(id)

    # [!] Make sure the global inventory_item is synchronized with the latest
    #     data grab
    self.inventory_item = self.db_client.get_inventory_item_as_object(id)

    # Handle loading and encoding image from media data
    img_path = Path(str(item_data_df.iloc[0]['item_image']))
    info(f'Image file path {img_path.absolute().as_posix()}')

    if img_path.exists():
      self.state.item_image_path = img_path.absolute().as_posix()
      try:
        # encode_image_from_path(img_path.absolute().as_posix())
        self.state.image_src = f"data:image/png;base64,{
            self.encode_image_from_path(self.state.item_image_path)}"
      except:
        self.state.image_src = f"data:image/png;base64,{
            self.encode_image_from_path(image_not_found_path)}"
        warning(f'Encoding image url failed for path {
                self.state.item_image_path}')

    else:
      warning(f'Failed to locate media file {
              img_path.absolute().as_posix()}')
      self.state.item_image_path = image_not_found_path
      self.state.image_src = f"data:image/png;base64,{
          self.encode_image_from_path(image_not_found_path)}"

    # Update state
    self.state.item_name = f'{item_data_df.iloc[0]["item_name"]}'
    self.state.item_manufacturer = f'{item_data_df.iloc[0]['manufacturer']}'
    self.state.item_manufacturer_details = f'{
        item_data_df.iloc[0]['manufacturer_contact']}'
    self.state.is_checked_out = f'{item_data_df.iloc[0]['is_checked_out']}'
    self.state.check_out_date = f'{item_data_df.iloc[0]['check_out_date']}'
    self.state.check_out_poc = f'{item_data_df.iloc[0]['check_out_poc']}'
    self.state.date_added = f'{item_data_df.iloc[0]['date_added']}'
    self.state.item_description = f'{item_data_df.iloc[0]['item_description']}'
    self.state.item_tags = f'{item_data_df.iloc[0]['item_tags']}'

    if self.state.is_checked_out:
      self.state.checkout_status_summary = f'This item is checked out since {
          self.state.check_out_date} by {self.state.check_out_poc}'
    else:
      self.state.checkout_status_summary = ' This item has not been checked out.'

    print(f'--- {self.state.item_name}')

  def read_item_user_input_to_object(self):
    """
    Compile the user input for the selected inventory item into a
    InventoryItem instance

    Returns:
    valid_data - Flag True if compiled data set is valid (User inputs are valid)
    inventoryItem - InventoryItem instance populated with user inputs
    """
    valid_data = True
    # Initialize empty InventoryItem
    inventoryItem = InventoryItem(item_name="")

    # Check input validity
    if self.state.item_name == "" or self.state.item_name is None:
      warning('No item name defined. Current user input is invalid.')
      valid_data = False

    # Create item and add to database
    if valid_data:
      # Create inventory item
      inventoryItem.item_name = str(self.state.item_name)
      inventoryItem.item_description = str(self.state.item_description)
      inventoryItem.manufacturer = str(self.state.item_manufacturer)
      inventoryItem.manufacturer_contact = str(
          self.state.item_manufacturer_details)
      inventoryItem.item_tags = str(self.state.item_tags)
      inventoryItem.set_img_path(Path(self.state.item_image_path))

    return valid_data, inventoryItem

  def capture_image(self):
    """
    Callback function to capture an image of an inventory item before adding
    it to the database
    """
    global display_img
    try:
      display_img = self.camera_server.get_last_frame()

      self.state.display_img_src = f"data:image/png;base64,{
          self.encode_image(display_img)}"
    except:
      warning('[capture_image] Capturing image failed.')

  def update_item_image_with_capture(self):
    """
    Take the latest captured image and set it as the currently selected items
    image
    """

    if self.state.display_img_src is not None:
      self.state.image_src = self.state.display_img_src

      cam_img_bytes = display_img.tobytes()
      hash_object = hashlib.sha256(cam_img_bytes)
      hash_hex = hash_object.hexdigest()

      img_path = Path(media_directory) / f'{hash_hex}.png'
      self.state.item_image_path = img_path.absolute().as_posix()

      # Save item image to file
      cv.imwrite(img_path, display_img)

      try:
        # encode_image_from_path(img_path.absolute().as_posix())
        self.state.image_src = f"data:image/png;base64,{
            self.encode_image_from_path(self.state.item_image_path)}"
      except:
        self.state.image_src = f"data:image/png;base64,{
            self.encode_image_from_path(image_not_found_path)}"
        warning(f'Encoding image url failed for path {
                self.state.item_image_path}')

      # Update the path in the database
      if self.state.selected_item_id is not None:
        self.db_client.update_inventory_item_image_path(self.state.selected_item_id,
                                                        img_path.absolute().as_posix())

  def switch_show_img_change(self, *args):
    if self.state.show_img_swap_page:
      self.state.show_img_swap_page = False
      info('Show image swap')
    else:
      self.state.show_img_swap_page = True
      info('Hide image swap')

  def logout(self, *args):
    """
    Callback function to log out current user
    """
    self.state.user_name = ''
    self.state.password = ''
    self.state.logged_in = False
    self.state.error_message = ''

  def login(self, username, password):
    """
    Callback function to interface with the inventory user database table:
     * Check user name is a Inventory user
     * Check user password matches

     / If not both of the above show the correct error message
     / If both of the above set logged_in to True and assign privileges

    """
    valid_user, inventoryUser = self.db_client.get_inventory_user_as_object(
        username)

    if not valid_user:
      self.state.error_message = "User name not found"
    elif inventoryUser.is_password(password):
      self.state.logged_in = True
      self.state.error_message = ""
      info(f'[x] User {username} with {UserPrivileges(
          inventoryUser.user_privileges)} logged in')
      self.state.privileges = inventoryUser.user_privileges

      # Manage user exposure corresponding to privileges
      self.state.enable_privilege_add_item = False
      self.state.enable_privilege_delete_item = False
      self.state.enable_privilege_mod_item = False
      self.state.enable_privilege_settings = False

      if inventoryUser.user_privileges == UserPrivileges.REPORTER.value:
        self.state.enable_privilege_add_item = False
        self.state.enable_privilege_delete_item = False
        self.state.enable_privilege_mod_item = False
      elif inventoryUser.user_privileges == UserPrivileges.DEVELOPPER.value:
        self.state.enable_privilege_add_item = True
        self.state.enable_privilege_delete_item = False
        self.state.enable_privilege_mod_item = True
      elif inventoryUser.user_privileges == UserPrivileges.MAINTAINER.value:
        self.state.enable_privilege_add_item = True
        self.state.enable_privilege_delete_item = True
        self.state.enable_privilege_mod_item = True
        self.state.enable_privilege_settings = True
      elif inventoryUser.user_privileges == UserPrivileges.OWNER.value:
        self.state.enable_privilege_add_item = True
        self.state.enable_privilege_delete_item = True
        self.state.enable_privilege_mod_item = True
        self.state.enable_privilege_settings = True

    else:
      self.state.error_message = "Invalid credentials, please try again"

  def start_server(self):
    """
    Main function to start the inventory frontend server

    --> From API for server.start() :

    Start the server by listening to the provided port or using the port, 
    -p command line argument. If the server is already starting or started, 
    any further call will be skipped.

    When the exec_mode=”main” or “desktop”, the method will be blocking. 
    If exec_mode=”task”, the method will return a scheduled task. If 
    exec_mode=”coroutine”, the method will return a coroutine which will 
    need to be scheduled by the user.

    Parameters:

        port  A port number to listen to. When 0 is provided the system will 
        use a random open port.

        thread  If the server run in a thread which means we should disable 
        interuption listeners

        open_browser  
        Should we open the system browser with app url. 
        Using the server command line argument is similar to setting it 
        o False.

        show_connection_info  
        hould we print connection URL at startup?

        disable_logging  
        Ask wslink to disable logging

        backend  
        aiohttp by default but could be generic or tornado. 
        This can also be set with the environment variable TRAME_BACKEND. 
        Defaults to 'aiohttp'.

        exec_mode  
        main/desktop/task/coroutine specify how the start 
        function should work

        timeout  
        How much second should we wait before automatically 
        stopping the server when no client is connected. Setting it to 0 
        will disable such auto-shutdown.

        host  The 
        hostname used to bind the server. This can also be set 
        with the environment variable TRAME_DEFAULT_HOST. Defaults to 
        'localhost'.

        **kwargs 

        Keyword arguments for capturing optional parameters for wslink 
        server and/or desktop browser

    """
    # --- Start server ---
    if enableRunForDebug:
      self.server.start(thread=True,
                        open_browser=True,
                        disable_logging=True,
                        timeout=0)
    else:
      self.server.start(open_browser=False,
                        host=frontend_host_ip,
                        port=frontend_host_port,
                        disable_logging=True,
                        timeout=0)


# Function to allow running the frontend in isolation
if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  app = FrontendApplication(db_client=DataBaseClient(host=database_host))
  app.start_server()
