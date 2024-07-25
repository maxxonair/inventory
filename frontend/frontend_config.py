"""
Frontend parameter file

"""


# -------------------------------------------------------------------------
# ---- SETUP
# -------------------------------------------------------------------------
inventory_page_title = "B.I.G Material Library"

inventory_main_window_title = "B.I.G Material Library"

main_table_header_options = {"item_name": {"sortable": False}}


# -------------------------------------------------------------------------
# ---- CAMERA INTERFACE
# -------------------------------------------------------------------------
# Create HTML snipped to embed camera live stream from flask server
html_content_embed_camera_stream = """
<div>
    <img crossorigin="anonymous" src="http://127.0.0.1:5000/video_feed" width="50%">
</div>
"""
