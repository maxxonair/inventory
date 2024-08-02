"""
Frontend parameter file

"""
from pathlib import Path

# -------------------------------------------------------------------------
# ---- SETUP
# -------------------------------------------------------------------------
inventory_page_title = "B.I.G Material Library"

inventory_main_window_title = "B.I.G Material Library"

main_table_header_options = {"item_name": {"sortable": False}}

media_directory = './database/media'

# Flag to enable/disable the login function. Disabling for debugging only!
# If disabled the user will be set to the default user without prompting
# the login page
enableLogin = False

# Host IP for the frontend server
frontend_host_ip = "192.168.1.194"

# Default port for the frontend server
frontend_host_port = 8080

# -------------------------------------------------------------------------
# ---- CAMERA INTERFACE
# -------------------------------------------------------------------------
# Create HTML snipped to embed camera live stream from flask server
html_content_embed_camera_stream = """
<div>
    <img crossorigin="anonymous" src="http://127.0.0.1:5000/video_feed" width="70%">
</div>
"""

# Create HTML snipped to embed camera live stream from flask server
html_content_embed_camera_stream_large = """
<div>
    <img crossorigin="anonymous" src="http://127.0.0.1:5000/video_feed" width="85%">
</div>
"""

# Default path to image will be displayed when no image path is available
# or loading failed
image_not_found_path = Path("frontend/data/no_image_available.jpg")
