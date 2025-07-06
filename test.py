r"""
Installation requirements:
    pip install trame trame-vuetify trame-router
"""

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets.vuetify import VImg, VRow
from trame.ui.router import RouterViewLayout
from trame.widgets import vuetify, router
import asyncio
import base64
from pathlib import Path
import cv2 as cv
from signal import SIGINT, SIGTERM


def encode_image_from_path(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def encode_image(cv_image):
    # Convert the OpenCV image (NumPy array) to bytes
  _, buffer = cv.imencode('.jpg', cv_image)
  image_bytes = buffer.tobytes()

  # Encode the bytes to base64
  return base64.b64encode(image_bytes).decode('utf-8')


# Default path to image will be displayed when no image path is available
# or loading failed
image_not_found_path = Path(
    "/home/mrx/Documents/inventory/frontend/data/no_image_available.jpg")

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

state.image_src = f"data:image/png;base64,{
    encode_image_from_path(image_not_found_path)}"
state.stop_camera_server = False
state.image_refresh_rate_hz = 300

camera = cv.VideoCapture(0)


async def run_camera():
  while not state.stop_camera_server:
    await asyncio.sleep(1 / state.image_refresh_rate_hz)
    success, frame = camera.read()
    if success:
      state.image_src = f"data:image/png;base64,{encode_image(frame)}"
    else:
      print('[WRN] Failed to grab frame')
    state.flush()


@ctrl.add("on_server_stop")
def cleanup():
  camera.release()
# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------


# Home route
with RouterViewLayout(server, "/"):
  with VRow():
    VImg(src=("image_src",),
         max_width="400px",
         classes="mb-5")

# Main page content
with SinglePageWithDrawerLayout(server) as layout:
  layout.title.set_text("Multi-Page demo")

  with layout.toolbar:
    # Switch to control theme
    vuetify.VSwitch(
        v_model="$vuetify.theme.dark",
        hide_detials=True,
        dense=True,
        hint='Theme',
    )

  with layout.content:
    with vuetify.VContainer():
      router.RouterView()

  # add router buttons to the drawer
  with layout.drawer:
    with vuetify.VList(shaped=True, v_model=("selectedRoute", 0)):
      vuetify.VSubheader("Routes")

      with vuetify.VListItem(to="/"):
        with vuetify.VListItemIcon():
          vuetify.VIcon("mdi-home")
        with vuetify.VListItemContent():
          vuetify.VListItemTitle("Home")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def do_cleanup_event_loop(loop):
  """
  Clean up event loop by first stopping and then closing the loop.#

  This function is intended to be a callback for SIGNINT and SIGTERM events
  """
  print('SIGINT received.')
  print('Releasing camera')
  camera.release()
  print('Stopping Event Loop')
  loop.stop()
  loop.close()


async def run():
  task = server.start(exec_mode='task')
  return


def main():
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)

  # ---- HANDLE SIGINT/SIGTERM PROCESSES ----
  # Set callbacks to handle sigint and sigterm events -> stop and close
  # event loop
  for signal in [SIGINT, SIGTERM]:
    loop.add_signal_handler(signal, do_cleanup_event_loop, loop)

  # ---- START APPLICATION ----

  loop.run_until_complete(asyncio.gather(
      run(), run_camera()))


if __name__ == "__main__":
  main()
