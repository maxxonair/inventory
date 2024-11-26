
from trame.widgets import vuetify as vuetify, vega, router, html
from trame.widgets.vuetify import (VBtn, VSpacer, VTextField, VCardText, VIcon,
                                   VCol, VRow, VContainer, VImg, VCardTitle,
                                   VCard, VList, VListItem,
                                   VListItemTitle, VTooltip
                                   )
from trame.widgets.vuetify import (VListItemContent, VListItemIcon)
from trame.ui.vuetify2 import VAppLayout
from trame.widgets import vuetify2
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.ui.router import RouterViewLayout
from io import StringIO
from multiprocessing import Process, Manager, Pipe, Value
import time
import asyncio
import cv2 as cv
import base64
import hashlib
from pathlib import Path
from logging import info, error, warning, debug
import logging
import sys
import pandas as pd
import os
from datetime import datetime

# --------------------------------------------------------------------------
#                           [Inventory Imports]
# --------------------------------------------------------------------------
# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# ---- Backend imports
from backend import (CameraServer,
                     PrinterClient,
                     InventoryUser,
                     UserPrivileges,
                     database_host,
                     InventoryItem,
                     DataBaseClient)

# ---- Frontend imports
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

  # Time to display VAlert messages
  delay_success_messages_s = 2
  delay_warning_messages_s = 20

  # -----------------------------------------------------------------------------
  #                 [INIT]
  # -----------------------------------------------------------------------------
  def __init__(self, server, state, ctrl, camera_server: CameraServer):
    # -----------------------------------------------------------------------
    # Main application server
    # ---------------------------------------------------------------------
    self.server = server
    self.state = state
    self.ctrl = ctrl

    # Add camera server - This is used to capture item images
    self.camera_server = camera_server

    # Create server.state members
    self.state.dummy_id = 0
    self.state.qr_message = None
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

    # If true show the camera feed in the Checkout Item section
    self.state.show_checkout_camera_feed = False
    # If true show the camera feed in the return Item section
    self.state.show_return_camera_feed = False
    # If true show the camera feed in the Inventory overview section
    self.state.show_inventory_camera_feed = False
    # If true show the camera feed in the add item section
    self.state.show_add_camera_feed = False

    # Flag, True if the user is logged-in, False otheriwse
    self.state.logged_in = False

    # Note: if show_home_item_image is True, show_home_camera must be false!
    self.state.show_home_camera = False
    self.state.show_home_item_image = True

    self.state.show_modify_item_alert_success = False
    self.state.modify_item_alert_text_success = ''

    self.state.show_modify_item_alert_warning = False
    self.state.modify_item_alert_text_warning = ''

    self.state.show_add_item_alert_success = False
    self.state.add_item_alert_text_success = ''

    self.state.show_add_item_alert_warning = False
    self.state.add_item_alert_text_warning = ''

    self.state.show_checkout_alert_success = False
    self.state.checkout_alert_text_success = ''

    self.state.show_checkout_alert_warning = False
    self.state.checkout_alert_text_warning = ''

    self.state.show_return_alert_success = False
    self.state.return_alert_text_success = ''

    self.state.show_return_alert_warning = False
    self.state.return_alert_text_warning = ''

    # Temporary array to store the captured item image
    self.display_img = None

    # Tooltip text shown for the come camera button
    self.state.home_tooltip_text = "Open Camera"

    self.state.time_str = ''
    self.state.inventory_csv_string = ''
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
      # Store a full copy of the inventory in the state
      # TODO: Find a smarter way to do this
      db_client = DataBaseClient(database_host)

      # Convert DataFrame to CSV format as string
      csv_buffer = StringIO()
      db_client.get_inventory_as_df().to_csv(csv_buffer, index=False)
      self.state.inventory_csv_string = csv_buffer.getvalue()

      time_now = datetime.now()
      self.state.time_str = time_now.strftime("%d_%m_%Y__%H_%M_%S")

      filtered_df = filter_inventory_df(self.state.query)
      headers, rows = vuetify.dataframe_to_grid(
          filtered_df, main_table_header_options)
      self.state.headers = headers
      self.state.rows = rows

    self.state.query = ""
    update_table()

    def delete_inventory_item(*args):
      """
      Callback function to delete the currently selected inventory item
      """
      # Only delete item if one is selected
      if self.state.item_id is not None:
          # Create a DatabaseClient instance and connect to the inventory database
        db_client = DataBaseClient(host=database_host)
        # Command: DELETE item from inventory
        db_client.delete_inventory_item(int(self.state.item_id))

        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        # Update the table view
        update_table()
        self.display_success('Item deleted successfully', 'modify_item')

    def update_inventory_item(*args):
      """
      Callback function to update the currently selected inventory item
      """
      valid_data, inventoryItem = self.read_item_user_input_to_object()

      if valid_data:

        # Create a DatabaseClient instance and connect to the inventory database
        db_client = DataBaseClient(host=database_host)
        info(f'[x] Update inventory item: {
             inventoryItem.item_name} - image path {inventoryItem.item_image}')

        # Update the item in the database
        db_client.update_inventory_item(inventory_item=inventoryItem,
                                        id=self.state.item_id)

        # TODO: This currently needs to be called after
        #       db_client.update_inventory_item because the image file path
        #       is not properly set by read_item_user_input_to_object()
        # Update item image
        self.update_item_image_last_captured_image()

        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        # Update the table view
        update_table()
        self.display_success('Item updated successfully', 'modify_item')
      else:
        error('Adding Inventory item failed. Invalid user inputs')
        self.display_warning('Item update failed!', 'modify_item')

    def add_inventory_item(*args):
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
        if self.display_img is not None:
          cam_img_bytes = self.display_img.tobytes()
          hash_object = hashlib.sha256(cam_img_bytes)
          hash_hex = hash_object.hexdigest()

          img_path = Path(media_directory) / f'{hash_hex}.png'

          # Save item image to file
          cv.imwrite(img_path, self.display_img)

          # Update image path in InventoryItem instance
          inventoryItem.set_img_path(img_path)

        # Create a temporary DatabaseClient instance and connect to the
        # inventory database
        db_client = DataBaseClient(host=database_host)
        # Add item to database
        temp_id = db_client.add_inventory_item(inventoryItem)

        if temp_id == -1:
          # Fetching ID failed -> don't update state variable
          warning('Fetched ID of created item invalid.')
        else:
          # Update ID in state
          self.state.item_id = temp_id

        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        # Print QR code label
        if not self.print_label_from_id():
          self.display_warning(
              'Item added to inventory. Failed to connect to printer', 'add_item')
        else:
          self.display_success(
              'Item added successfully!', 'add_item')

        update_table()
      else:
        self.display_warning(
            'Adding item failed! Invalid user inputs', 'add_item')
        error('Adding Inventory item failed. Invalid user inputs')

      self.state.flush()

    def checkout_item(*args):

      ret = self.inventory_item.set_checked_out(self.state.username)

      if ret:
          # Create a DatabaseClient instance and connect to the inventory database
        db_client = DataBaseClient(host=database_host)
        # Update checkout status in database
        db_client.update_inventory_item_checkout_status(id=self.state.item_id,
                                                        inventory_item=self.inventory_item)
        # Update the dataframe so the table reflects the updated DB state
        self.update_inventory_df()

        update_table()
        self.state.is_checked_out = 1
        self.state.check_out_poc = self.state.username
        self.state.check_out_date = self.inventory_item.check_out_date
        self._update_checkout_status()

        self.display_success('Item checked-out successful!', 'checkout')
      else:
        self.display_warning(
            'Item checked-out failed. No User set!', 'checkout')
        warning('Updating checkout status failed. No user set.')

      self.state.flush()

    def checkin_item(*args):

      self.inventory_item.set_checked_in(self.state.username)
      # Create a DatabaseClient instance and connect to the inventory database
      db_client = DataBaseClient(host=database_host)
      # Update checkout status in database
      db_client.update_inventory_item_checkout_status(id=self.state.item_id,
                                                      inventory_item=self.inventory_item)
      # Update the dataframe so the table reflects the updated DB state
      self.update_inventory_df()

      update_table()
      self.state.is_checked_out = 0
      self._update_checkout_status()
      self.display_success('Item returned successfully!', 'return')

    # -----------------------------------------------------------------------
    # -- GUI
    # -----------------------------------------------------------------------

    # Prepare table elements and configuration
    headers, rows = vuetify.dataframe_to_grid(self.inventory_df,
                                              main_table_header_options)
    main_table_config = {
        "headers": ("headers", headers),
        "items": ("rows", rows),
        # Link selection callback function
        "v_model": ("selection", []),
        "search": ("query", ""),
        "classes": "elevation-1 ma-4",
        "multi_sort": True,
        "dense": True,
        # Only allow a single row to be selected at the time
        "single_select": True,
        "item_key": "id",
    }

    # --- INVENTORY [HOME] ---
    with RouterViewLayout(self.server, "/", clicked=self.update_inventory_df, v_if="logged_in"):
      with vuetify.VContainer(fluid=True):
        # --- main row to contain all elements of this page
        with VRow():
          # --- inventory item data and image
          with VCol():
            # --- row containing the control buttons and the item image
            with VRow():
              # --- control button column ---
              with VCol(style="width: 30px; min-width: 30px; max-width: 30px;"):

                with VRow(v_if="logged_in", style="margin-bottom: 16px;"):
                  with vuetify2.VTooltip('Confirm Modification', bottom=True):
                    with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                      with VBtn('',
                                click=update_inventory_item,
                                outlined=True,
                                icon=True,
                                v_if="enable_privilege_mod_item",
                                v_bind='attrs',
                                v_on='on'
                                ):
                        VIcon('mdi-swap-horizontal', color='primary')
                with VRow(v_if="logged_in", style="margin-bottom: 16px;"):
                  with vuetify2.VTooltip('Delete Item', bottom=True):
                    with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                      with VBtn('',
                                click=delete_inventory_item,
                                outlined=True,
                                icon=True,
                                v_if="enable_privilege_delete_item",
                                v_bind='attrs',
                                v_on='on'):
                        VIcon('mdi-trash-can-outline', color='primary')
                with VRow(v_if="logged_in", style="margin-bottom: 16px;"):
                  with vuetify2.VTooltip(bottom=True):
                    vuetify2.Template("{{ home_tooltip_text }}")
                    with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                      with VBtn('',
                                click=self.handle_home_camera_action,
                                outlined=True,
                                disabled=False,
                                icon=True,
                                v_if="enable_privilege_mod_item",
                                v_bind='attrs',
                                v_on='on'):
                        VIcon('mdi-camera', color='primary')
                with VRow(v_if="show_home_camera", style="margin-bottom: 16px;"):
                  with vuetify2.VTooltip(bottom=True):
                    vuetify2.Template("Switch-off Camera")
                    with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                      with VBtn('',
                                click=self.switch_off_home_camera,
                                outlined=True,
                                disabled=False,
                                icon=True,
                                v_if="enable_privilege_mod_item",
                                v_bind='attrs',
                                v_on='on'):
                        VIcon('mdi-camera-off', color='primary')
                with VRow(v_if="logged_in", style="margin-bottom: 16px;"):
                  with vuetify2.VTooltip('Print Item Label', bottom=True):
                    with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                      with VBtn('',
                                click=self.print_label_from_id,
                                icon=True,
                                outlined=True,
                                v_bind='attrs',
                                v_on='on'):
                        VIcon("mdi-cloud-print", color='primary')

              # --- item image ---
              with VCol(style="width: 300px; min-width: 60px; max-width: 400px;"):

                vuetify.VAlert("{{ modify_item_alert_text_success }}",
                               type="success", v_if="show_modify_item_alert_success")
                vuetify.VAlert("{{ modify_item_alert_text_warning }}",
                               type="warning", v_if="show_modify_item_alert_warning")

                VImg(
                    src=("image_src",),
                    max_width="400px",
                    classes="mb-5",
                    v_if="show_home_item_image")
                # Embed camera stream in this sub-page
                html.Div(html_content_embed_camera_stream,
                         v_if="show_home_camera")

            # --- inventory item meta data
            with VRow(v_if="logged_in"):
              with VCol(style="width: 300px; min-width: 60px; max-width: 600px;"):
                fig_item = vega.Figure(classes="ma-2", style="width: 100%;")
                self.ctrl.view_update = fig_item.update
                with vuetify.VContainer(fluid=True):
                  VTextField(
                      v_model=("item_name", ""),
                      label="Item Name",
                      placeholder="Enter item name",
                      prepend_icon="mdi-rename-box-outline"
                  )
                  VTextField(
                      v_model=("item_description", ""),
                      label="Item Description",
                      placeholder="Enter item description",
                      prepend_icon="mdi-image-text"
                  )
                  VTextField(
                      v_model=("item_tags", ""),
                      label="Tags",
                      placeholder="Enter item tags",
                      prepend_icon="mdi-tag"
                  )
                  VTextField(
                      v_model=("item_manufacturer", ""),
                      label="Manufacturer",
                      placeholder="Enter item manufacturer",
                      prepend_icon="mdi-anvil"
                  )
                  VTextField(
                      v_model=("item_manufacturer_details", ""),
                      label="Manufacturer Details",
                      placeholder="Enter item manufacturer details",
                      prepend_icon="mdi-anvil"
                  )
                  VCardText(
                      "Check out status: {{ checkout_status_summary }}")

          # --- inventory table
          with VCol():
            with VRow():
              # TODO Add refined search option
              VBtn('Refined search - Under Construction')
            with VRow(classes="justify-center ma-6", v_if="logged_in"):
              fig = vega.Figure()
              self.ctrl.fig_update = fig.update
              vuetify.VDataTable(**main_table_config,
                                 v_if="logged_in",
                                 # Set default 20 items per page
                                 items_per_page=20,
                                 # Hide select check boxes
                                 show_select=True)
              # Add callback function to select items
              # click_row=on_row_click)

    # --- ADD IVENTORY ITEM ---
    with RouterViewLayout(self.server, "/add inventory item", v_if="enable_privilege_add_item"):
      with vuetify.VContainer(fluid=True, v_if="logged_in"):
        with VRow():
          # with VCol(style="width: 300px; min-width: 150px; max-width: 600px;"):
          with VCol():
            VCardTitle("Add Inventory Item")

            # ++ Controls
            with VCardText():
              with vuetify2.VTooltip('Add Inventory Item', bottom=True):
                with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                  with VBtn('',
                            click=add_inventory_item,
                            outlined=True,
                            icon=True,
                            v_bind='attrs',
                            v_on='on'):
                    VIcon("mdi-archive-plus", color='primary')
              with vuetify2.VTooltip('Open Camera', bottom=True):
                with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                  with VBtn('',
                            click=self.add_show_camera_feed,
                            outlined=True,
                            icon=True,
                            v_bind='attrs',
                            v_on='on'):
                    VIcon("mdi-camera", color='primary')

            vuetify.VAlert("{{ add_item_alert_text_success }}",
                           type="success", v_if="show_add_item_alert_success")
            vuetify.VAlert("{{ add_item_alert_text_warning }}",
                           type="warning", v_if="show_add_item_alert_warning")

            with VCol():
              with VRow():
                VImg(
                    src=("image_src",), max_width="400px", classes="mb-5")
            with VCol(style="width: 300px; min-width: 60px; max-width: 600px;"):
              with VRow():
                VTextField(
                    v_model=("item_name", ""),
                    label="Item Name",
                    placeholder="Enter item name",
                    prepend_icon="mdi-rename-box-outline"
                )
              with VRow():
                VTextField(
                    v_model=("item_description", ""),
                    label="Item Description",
                    placeholder="Enter item description",
                    prepend_icon="mdi-image-text"
                )
              with VRow():
                VTextField(
                    v_model=("item_tags", ""),
                    label="Tags",
                    placeholder="Enter item tags",
                    prepend_icon="mdi-tag"
                )
              with VRow():
                VTextField(
                    v_model=("item_manufacturer", ""),
                    label="Manufacturer",
                    placeholder="Enter Manufacturer",
                    prepend_icon="mdi-anvil"
                )
              with VRow():
                VTextField(
                    v_model=("item_manufacturer_details", ""),
                    label="Manufacturer Contact Details",
                    placeholder="Enter Manufacturer Details",
                    prepend_icon="mdi-anvil"
                )
          with VCol(v_if="show_add_camera_feed"):
            with VRow(align='center', justify='center'):
              with VCardText("Place Item in Front of the Camera!"):
                with vuetify2.VTooltip('Capture Image', bottom=True):
                  with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                    with VBtn('',
                              click=self.capture_image,
                              outlined=True,
                              icon=True,
                              x_large=True,
                              v_bind='attrs',
                              v_on='on'):
                      VIcon("mdi-camera", color='primary')
            with VRow():
              html.Div(html_content_embed_camera_stream_large)

    # --- CHECK-OUT INVENTORY ITEM ---
    with RouterViewLayout(self.server, "/checkout inventory item"):
      with vuetify.VContainer(fluid=True):
        with VRow(v_if="logged_in"):
          fig_item = vega.Figure(classes="ma-2", style="width: 100%;")
          self.ctrl.view_update = fig_item.update
          with VCol():
            VCardTitle("Check-out Inventory Item")

            with VCardText():
              with vuetify2.VTooltip('Open Camera', bottom=True):
                with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                  with VBtn('',
                            outlined=True,
                            click=self.checkout_show_camera_feed,
                            icon=True,
                            v_bind='attrs',
                            v_on='on'):
                    VIcon("mdi-qrcode-scan", color='primary')
              with vuetify2.VTooltip('Check-out Item', bottom=True):
                with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                  with VBtn('',
                            outlined=True,
                            block=(self.state.is_checked_out == False),
                            click=checkout_item,
                            icon=True,
                            v_bind='attrs',
                            v_on='on'):
                    VIcon("mdi-cart-check", color='primary')

              vuetify.VAlert("{{ checkout_alert_text_success }}",
                             type="success", v_if="show_checkout_alert_success")
              vuetify.VAlert("{{ checkout_alert_text_warning }}",
                             type="warning", v_if="show_checkout_alert_warning")

            with VRow(tyle="margin-top: 10px;"):
              with VCol():
                VImg(
                    src=("image_src",), max_width="400px", classes="mb-5")
            with VCol(style="width: 300px; min-width: 60px; max-width: 600px;"):
              with VRow():
                VTextField(
                    v_model=("item_name", ""),
                    label="Item Name",
                    placeholder="Enter item name",
                    prepend_icon="mdi-rename-box-outline",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_description", ""),
                    label="Item Description",
                    placeholder="Enter item description",
                    prepend_icon="mdi-image-text",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_tags", ""),
                    label="Tags",
                    placeholder="Enter item tags",
                    prepend_icon="mdi-tag",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_manufacturer", ""),
                    label="Manufacturer",
                    placeholder="Enter Manufacturer",
                    prepend_icon="mdi-anvil",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_manufacturer_details", ""),
                    label="Manufacturer Contact Details",
                    placeholder="Enter Manufacturer Details",
                    prepend_icon="mdi-anvil",
                    disabled=True
                )
          with VCol():
            with VRow(v_if="show_checkout_camera_feed", style="margin-top: 10px;"):
              VCardText("Place QR label in Front of the Camera!")
              # Embed camera stream in this sub-page
              html.Div(html_content_embed_camera_stream)

    # --- RETURN INVENTORY ITEM ---
    with RouterViewLayout(self.server, "/return inventory item"):
      with vuetify.VContainer(fluid=True):
        with VRow(v_if="logged_in"):
          fig_item2 = vega.Figure(classes="ma-2", style="width: 100%;")
          self.ctrl.view_update = fig_item2.update
          with VCol():
            VCardTitle("Return Inventory Item")

            with VCardText():
              with vuetify2.VTooltip('Open Camera', bottom=True):
                with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                  with VBtn('',
                            outlined=True,
                            click=self.return_show_camera_feed,
                            icon=True,
                            v_bind='attrs',
                            v_on='on'):
                    VIcon("mdi-qrcode-scan", color='primary')
              with vuetify2.VTooltip('Return Item', bottom=True):
                with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                  with VBtn('',
                            outlined=True,
                            click=checkin_item,
                            icon=True,
                            v_bind='attrs',
                            v_on='on'):
                    VIcon("mdi-cart-check", color='primary')

            vuetify.VAlert("{{ return_alert_text_success }}",
                           type="success", v_if="show_return_alert_success")
            vuetify.VAlert("{{ return_alert_text_warning }}",
                           type="warning", v_if="show_return_alert_warning")

            with VRow(tyle="margin-top: 20px;"):
              with VCol():
                VImg(
                    src=("image_src",), max_width="400px", classes="mb-5")
            with VCol(style="width: 300px; min-width: 60px; max-width: 600px;"):
              with VRow():
                VTextField(
                    v_model=("item_name", ""),
                    label="Item Name",
                    placeholder="Enter item name",
                    prepend_icon="mdi-rename-box-outline",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_description", ""),
                    label="Item Description",
                    placeholder="Enter item description",
                    prepend_icon="mdi-image-text",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_tags", ""),
                    label="Tags",
                    placeholder="Enter item tags",
                    prepend_icon="mdi-tag",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_manufacturer", ""),
                    label="Manufacturer",
                    placeholder="Enter Manufacturer",
                    prepend_icon="mdi-anvil",
                    disabled=True
                )
              with VRow():
                VTextField(
                    v_model=("item_manufacturer_details", ""),
                    label="Manufacturer Contact Details",
                    placeholder="Enter Manufacturer Details",
                    prepend_icon="mdi-anvil",
                    disabled=True
                )
          with VCol():
            with VRow(v_if="show_return_camera_feed", style="margin-top: 10px;"):
              VCardText("Place QR label in Front of the Camera!")
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
        # ---- BEBUG -> LOG IN DISABLED ----
        # Force logged in state with debug user
        self.state.username = 'debugger'
        self.state.logged_in = True
        # Give full owner priveleges
        # TODO revisit this
        self.state.enable_privilege_add_item = True
        self.state.enable_privilege_delete_item = True
        self.state.enable_privilege_mod_item = True
        self.state.enable_privilege_settings = True

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

        # Switch to control theme
        vuetify.VSwitch(
            v_model="$vuetify.theme.dark",
            hide_detials=True,
            dense=True,
            hint='Theme'
        )

        # Button Export database to file (.csv)
        with vuetify2.VTooltip('Export Database to csv', bottom=True, v_if="logged_in"):
          with vuetify2.Template(v_slot_activator="{ on, attrs }"):
            with VBtn("",
                      disabled=False,
                      outlined=True,
                      icon=True,
                      click="utils.download('inventory.csv', inventory_csv_string, 'text/csv')",
                      v_bind='attrs',
                      v_on='on'):
              VIcon('mdi-file-export', color='primary')

        # INDICATOR -> Current User
        with VCard(classes="mx-5", max_height="50px",
                   outlined=True):
          with VCardText("User: {{ username }} "):
            VIcon('mdi-card-account-details', color='secondary')

        # Log-out Button
        with vuetify2.VTooltip('Log Out', bottom=True, v_if="logged_in"):
          with vuetify2.Template(v_slot_activator="{ on, attrs }"):
            with VBtn("",
                      click=self.logout,
                      outlined=True,
                      icon=True,
                      v_bind='attrs',
                      v_on='on'):
              VIcon('mdi-logout', color='primary')

      with layout.content:
        with vuetify.VContainer():
          router.RouterView()

      # add router buttons to the drawer
      with layout.drawer:
        with vuetify.VList(shaped=True, v_if="logged_in", v_model=("selectedRoute", 0)):
          # vuetify.VSubheader("Inventory Actions")

          with VListItem(to="/", clicked=self.update_inventory_df):
            with VListItemIcon():
              VIcon("mdi-home", color='primary')
            with VListItemContent():
              VListItemTitle("Inventory", clicked=self.update_inventory_df)

          with VListItem(to="/add inventory item",
                         clicked=self.update_inventory_df,
                         v_if="enable_privilege_add_item"):
            with VListItemIcon():
              VIcon("mdi-archive-plus", v_if="logged_in", color='primary')
            with VListItemContent():
              VListItemTitle("Add Item", v_if="logged_in")

          with VListItem(to="/checkout inventory item"):
            with VListItemIcon():
              VIcon("mdi-check", v_if="logged_in", color='primary')
            with VListItemContent():
              VListItemTitle("Checkout Item", v_if="logged_in")

          with VListItem(to="/return inventory item"):
            with VListItemIcon():
              VIcon("mdi-arrow-right", v_if="logged_in", color='primary')
            with VListItemContent():
              VListItemTitle("Return Item", v_if="logged_in")

          with VListItem(to="/settings",
                         v_if="enable_privilege_add_item"):
            with VListItemIcon():
              VIcon("mdi-cog", v_if="logged_in", color='primary')
            with VListItemContent():
              VListItemTitle("Settings", v_if="logged_in")

    # -----------------------------------------------------------------------
    # Internal Callbacks
    # -----------------------------------------------------------------------

    @ self.state.change("query")
    def on_query_change(query, **kwargs):
      update_table()

    @ self.state.change("modify_item_alert_text_success")
    def on_query_change(query, **kwargs):
      if self.state.modify_item_alert_text_success:
        self.state.show_modify_item_alert_success = True

    @ self.state.change("modify_item_alert_text_warning")
    def on_query_change(query, **kwargs):
      if self.state.modify_item_alert_text_warning:
        self.state.show_modify_item_alert_warning = True

    @ self.state.change("add_item_alert_text_success")
    def on_query_change(query, **kwargs):
      if self.state.add_item_alert_text_success:
        self.state.show_add_item_alert_success = True

    @ self.state.change("add_item_alert_text_warning")
    def on_query_change(query, **kwargs):
      if self.state.add_item_alert_text_warning:
        self.state.show_add_item_alert_warning = True

    @ self.state.change("checkout_alert_text_success")
    def on_query_change(query, **kwargs):
      if self.state.checkout_alert_text_success:
        self.state.show_checkout_alert_success = True

    @ self.state.change("checkout_alert_text_warning")
    def on_query_change(query, **kwargs):
      if self.state.checkout_alert_text_warning:
        self.state.show_checkout_alert_warning = True

    @ self.state.change("return_alert_text_success")
    def on_query_change(query, **kwargs):
      if self.state.return_alert_text_success:
        self.state.show_return_alert_success = True

    @ self.state.change("return_alert_text_warning")
    def on_query_change(query, **kwargs):
      if self.state.return_alert_text_warning:
        self.state.show_return_alert_warning = True

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
          self.state.item_id = current_id

          # Populate state data with item information
          self.populate_item_from_id(current_id)

          # Create a DatabaseClient instance and connect to the inventory database
          db_client = DataBaseClient(host=database_host)
          # Save a complete and global copy of this item
          self.inventory_item.populate_from_df(
              item_data_df=db_client.get_inventory_item_as_df(current_id))

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

  def hide_all_alerts(self):
    """
    Function: Hide all VAlert fields
    """
    self.state.show_modify_item_alert_success = False
    self.state.show_modify_item_alert_warning = False
    self.state.show_add_item_alert_success = False
    self.state.show_add_item_alert_warning = False
    self.state.show_checkout_alert_success = False
    self.state.show_checkout_alert_warning = False
    self.state.show_return_alert_success = False
    self.state.show_return_alert_warning = False
    self._reset_all_alert_messages()
    self.state.flush()

  def _reset_all_alert_messages(self):
    self.state.modify_item_alert_text_success = ''
    self.state.add_item_alert_text_success = ''
    self.state.checkout_alert_text_success = ''
    self.state.return_alert_text_success = ''
    self.state.modify_item_alert_text_warning = ''
    self.state.add_item_alert_text_warning = ''
    self.state.checkout_alert_text_warning = ''
    self.state.return_alert_text_warning = ''

  def display_success(self, message: str, section: str):
    """
    Function to display a success message within a section displayed as a VAlert
    """
    info(f'[Alert] display success < {message} > in section [{section}]')

    async def countdown_to_hide():
      await asyncio.sleep(self.delay_success_messages_s)
      self.hide_all_alerts()

    if section == 'modify_item':
      self.state.modify_item_alert_text_success = message
    elif section == 'add_item':
      self.state.add_item_alert_text_success = message
    elif section == 'checkout':
      self.state.checkout_alert_text_success = message
    elif section == 'return':
      self.state.return_alert_text_success = message
    else:
      error('[Display SUCCESS Alerts] Invalid section selected!')
    self.state.flush()

    # Start counter until alert is hidden again
    asyncio.create_task(countdown_to_hide())

  def display_warning(self, message: str, section: str):
    """
    Function to warning a success message within a section displayed as a VAlert
    """
    info(f'[Alert] display warning < {message} > in section [{section}]')

    async def countdown_to_hide():
      await asyncio.sleep(self.delay_warning_messages_s)
      self.hide_all_alerts()

    if section == 'modify_item':
      self.state.modify_item_alert_text_warning = message
    elif section == 'add_item':
      self.state.add_item_alert_text_warning = message
    elif section == 'checkout':
      self.state.checkout_alert_text_warning = message
    elif section == 'return':
      self.state.return_alert_text_warning = message
    else:
      error('[Display WARNING Alerts] Invalid section selected!')
    self.state.flush()

    # Start counter until alert is hidden again
    asyncio.create_task(countdown_to_hide())

  def checkout_show_camera_feed(self):
    """
    If camera feed NOT shown -> show camera feed
    If camera feed shown -> hide camera feed
    """
    self.state.show_checkout_camera_feed = not self.state.show_checkout_camera_feed

  def return_show_camera_feed(self):
    """
    If camera feed NOT shown -> show camera feed
    If camera feed shown -> hide camera feed
    """
    self.state.show_return_camera_feed = not self.state.show_return_camera_feed

  def inventory_show_camera_feed(self):
    """
    If camera feed NOT shown -> show camera feed
    If camera feed shown -> hide camera feed
    """
    self.state.show_inventory_camera_feed = not self.state.show_inventory_camera_feed

  def add_show_camera_feed(self):
    """
    If camera feed NOT shown -> show camera feed
    If camera feed shown -> hide camera feed
    """
    self.state.show_add_camera_feed = not self.state.show_add_camera_feed

  def update_inventory_df(self):
    """
    Update DataFrame that holds the compolete Inventory content

    """
    debug('Update Inventory Data')
    # Create a DatabaseClient instance and connect to the inventory database
    db_client = DataBaseClient(host=database_host)
    self.inventory_df = db_client.get_inventory_as_df()

    # Reset checkout alert visibility
    self.hide_all_alerts()

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

  def populate_item_from_id(self, id: int, is_update_from_qr_scan: bool = False):
    """
    Callback function to be called when scanning a QR code from an existing
    Inventory item.
    * Call the database to collect the inventory data corresponding to this
      ID
    * Populate server.state variables with the collected data

    """
    if is_update_from_qr_scan:
      # If update from QR scan show alert in both sections
      self.display_success(f'QR scanned -> ID {id}', section='checkout')
      self.display_success(f'QR scanned -> ID {id}', section='return')

    info(f'Load item from id {id}')
    # Create a DatabaseClient instance and connect to the inventory database
    db_client = DataBaseClient(host=database_host)
    # Get data for scanned item from database
    item_data_df = db_client.get_inventory_item_as_df(id)

    # Only proceed if item is found in the database
    if not item_data_df.empty:
      # [!] Make sure the global inventory_item is synchronized with the latest
      #     data grab
      self.inventory_item = db_client.get_inventory_item_as_object(id)

      self.state.item_id = id

      # Handle loading and encoding image from media data
      # Only update images that contain a valid path
      if Path(str(item_data_df.iloc[0]['item_image'])).name != 'inventory':
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
      self.state.update({"item_name": f'{item_data_df.iloc[0]["item_name"]}'})
      self.state.item_manufacturer = f'{item_data_df.iloc[0]['manufacturer']}'
      self.state.item_manufacturer_details = f'{
          item_data_df.iloc[0]['manufacturer_contact']}'
      is_checkout_temp = (
          f'{item_data_df.iloc[0]['is_checked_out']}')
      self.state.check_out_date = f'{item_data_df.iloc[0]['check_out_date']}'
      self.state.check_out_poc = f'{item_data_df.iloc[0]['check_out_poc']}'
      self.state.date_added = f'{item_data_df.iloc[0]['date_added']}'
      self.state.item_description = f'{
          item_data_df.iloc[0]['item_description']}'
      self.state.item_tags = f'{item_data_df.iloc[0]['item_tags']}'
      self._update_checkout_status()
      # Handle cases where for whichever reason the checkout status is set
      # to None
      if is_checkout_temp == 'None':
        self.state.is_checked_out = 0
      else:
        self.state.is_checked_out = int(is_checkout_temp)

      # Flush state and update UI
      self.state.flush()
      self.ctrl.view_update()
    else:
      warning(f'ITEM NOT FOUND in the database! ID = {id}')

  def _update_checkout_status(self):
    if self.state.is_checked_out == 1:
      self.state.checkout_status_summary = f' Item is CHECKED-OUT by {self.state.check_out_poc} since {
          self.state.check_out_date}'
    else:
      self.state.checkout_status_summary = ' Item has not been checked out.'
    self.state.flush()

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
    try:
      # Get last recorded frame from the camera
      self.display_img = self.camera_server.get_last_frame()
      info(f'IMAGE CAPTURED ---  {self._getdatetime()}')

      # Encode recorded frame to display it in UI
      self.state.image_src = f"data:image/png;base64,{
          self.encode_image(self.display_img)}"
    except:
      warning('[capture_image] Capturing image failed.')

  def print_label_from_id(self) -> bool:
    """
    Callback to print the label for the currently selected Item
    """
    client = PrinterClient()
    print_success = False
    if self.state.item_id is not None:
      print_success = client.print_qr_label_from_id(int(self.state.item_id))

    return print_success

  def _getdatetime(self) -> str:
    """
    Get current datetime as string fromat: %d/%m/%Y %H:%M:%S
    """
    time_now = datetime.now()
    return time_now.strftime("%d/%m/%Y %H:%M:%S")

  def update_item_image_last_captured_image(self):
    """
    Take the latest captured image and set it as the currently selected items
    image
    """
    if self.display_img is not None:

      # Create hash of image data array
      cam_img_bytes = self.display_img .tobytes()
      hash_object = hashlib.sha256(cam_img_bytes)
      hash_hex = hash_object.hexdigest()

      self.state.item_image_path = (
          Path(media_directory) / f'{hash_hex}.png').absolute().as_posix()

      # Save item image to file
      cv.imwrite(self.state.item_image_path, self.display_img)

      # Update the path in the database
      if self.state.item_id is not None:
        # Create a DatabaseClient instance and connect to the inventory
        # database
        info(
            f'[+] Set {self.state.item_id} item image path to {self.state.item_image_path}')
        db_client = DataBaseClient(host=database_host)
        db_client.update_inventory_item_image_path(self.state.item_id,
                                                   self.state.item_image_path)
      else:
        warning(f'Attempt to save image while display_img was None!')

  def switch_off_home_camera(self, *args):
    """
    Callback function to switch off the camera in the home section without
    action

    """
    # Flip visibility static image <-> camera live feed
    self.state.show_home_camera = (not self.state.show_home_camera)
    self.state.show_home_item_image = (not self.state.show_home_item_image)
    self.state.flush()

  def handle_home_camera_action(self, *args):
    """
    Handle actions when the camera button is pressed on the Home page:
    * If static image is shown -> switch to camera feed
    * If camera feed is on -> Capture image and switch back to static image

    """
    if self.state.show_home_item_image:
      # CASE - Item image is displayed -> Switch to camera feed
      # Switch visibility states of static image and camera feed
      self.state.home_tooltip_text = "Capture Image"
    elif self.state.show_home_camera:
      # CASE - Camera feed is displayed -> Capture image and switch back to
      # static image display
      self.state.home_tooltip_text = "Open Camera"
      # Capture image
      self.capture_image()
    else:
      error(f'Inconsistent image display state: image flag {
            self.state.show_home_item_image} / camera flag {self.state.show_home_camera}')

    # Flip visibility static image <-> camera live feed
    self.state.show_home_camera = (not self.state.show_home_camera)
    self.state.show_home_item_image = (not self.state.show_home_item_image)
    self.state.flush()

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
    # Create a DatabaseClient instance and connect to the inventory database
    db_client = DataBaseClient(host=database_host)
    valid_user, inventoryUser = db_client.get_inventory_user_as_object(
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

  async def run(self):
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
      task = self.server.start(thread=True,
                               open_browser=True,
                               disable_logging=True,
                               timeout=0,
                               exec_mode='task')
    else:
      task = self.server.start(open_browser=False,
                               host=frontend_host_ip,
                               port=frontend_host_port,
                               disable_logging=True,
                               timeout=0,
                               exec_mode='task')
    return task


# Function to allow running the frontend in isolation
if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  app = FrontendApplication()
  app.start_server()
