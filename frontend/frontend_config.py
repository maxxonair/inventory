"""
Parameter file configuring the UI application

"""
from pathlib import Path

# -------------------------------------------------------------------------
# ---- SETUP
# -------------------------------------------------------------------------
inventory_page_title = "Inventory Library"

inventory_main_window_title = "Inventory Library"

main_table_header_options = {"item_name": {"sortable": False}}

# All columns in this list will NOT be shown in the main table
main_table_drop_cols = ['item_description',
                        'manufacturer_contact',
                        'date_added',
                        'item_image']

# Directory where media files (e.g. item images) corresponding to database
# items will be stored
media_directory = './database/media'

# Host IP for the frontend server
frontend_host_ip = "192.168.1.194"

# Default port for the frontend server
frontend_host_port = 8080

# -------------------------------------------------------------------------
# ---- DEBUG FLAGS
# -------------------------------------------------------------------------

# Flag to enable/disable the login function. Disabling for debugging only!
# If disabled the user will be set to the default user without prompting
# the login page
# [!] Note: Currently if login is disabled the log-in will be skipped and
#     the user will automatically be logged in with full root access.
enable_login = True

# Flag to run frontend in debug mode
# Server will only be hosted to local host. frontend_host_ip/frontend_host_port
# will not be used.
enable_debug_run = False

# Flag to disable column filtering from the raw data base export
# If True all columns that are in the backend database will be displayed in
# the GUI
disable_main_table_col_filter = False

# TODO add data base table display column selection to this config

# -------------------------------------------------------------------------
# ---- CAMERA INTERFACE
# -------------------------------------------------------------------------
# Create HTML snipped to embed camera live stream from flask server
# TODO parameterize camera server IP and port
html_content_embed_camera_stream = """
<div>
    <img crossorigin="anonymous" src="http://127.0.0.1:5000" width="70%">
</div>
"""

# Create HTML snipped to embed camera live stream from flask server
html_content_embed_camera_stream_large = """
<div>
    <img crossorigin="anonymous" src="http://127.0.0.1:5000" width="100%">
</div>
"""

# Default path to image will be displayed when no image path is available
# or loading failed
image_not_found_path = Path("frontend/data/no_image_available.jpg")
