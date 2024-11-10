"""

Main application launcher

"""
from trame.app import get_server
import logging
from logging import info, warning, error, debug
from multiprocessing import Process, Manager
import multiprocessing
import sys
import signal
import asyncio

# --- Class imports
from backend.CameraServer import CameraServer
from frontend.FrontendApplication import FrontendApplication

# --- Config imports
from backend.database_config import database_host

camera_process = None
ui_process = None

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# Init default field for the parsed item ID (used by both camera server and
# UI)
state.parsed_item_id = None


def on_exit():
  """
  Callback to handle graceful exiting all servers and clients when the main
  application is closed.

  """
  info('[!] Exiting inventory application [!]')
  # Exit camera server
  try:
    camera_process.join()
  except:
    warning(f'Failed to exit camera server!')

  # Exit frontend server
  try:
    ui_process.join()
  except:
    warning(f'Failed to exit UI server!')

  sys.exit(0)


@ state.change("parsed_item_id")
def on_item_id_change(query, **kwargs):
  print(f'+++ >> {state.parsed_item_id}')


def main():
  """
  Main function to run and handle all components of this application:
   * The database client
   * The camera server
   * The UI server (aka frontend application)

  """
  global server, state, ctrl
  # -----------------------------------------------------------------------
  # -- FRONTEND SERVER
  # -----------------------------------------------------------------------
  # --- Create camera server instance
  frontend_server = FrontendApplication(server, state, ctrl)
  # -----------------------------------------------------------------------
  # -- CAMERA SERVER
  # -----------------------------------------------------------------------
  # --- Create camera server instance
  camera_server = CameraServer(state)

  ui_task = frontend_server.start_server()
  # -----------------------------------------------------------------------
  # -- START ALL THREADS
  # -----------------------------------------------------------------------
  loop = asyncio.get_event_loop()
  loop.run_until_complete(asyncio.gather(ui_task, camera_server.run()))

  # # TODO Add check if database server is running
  # # Start the camera server in a background thread
  # camera_process = Process(target=camera_server.run)
  # camera_process.start()
  # # Start the camera server in a background thread
  # ui_process = Process(target=frontend_server.start_server)
  # ui_process.start()

  # # -----------------------------------------------------------------------
  # # -- HANDLE SIGINT/SIGTERM PROCESSES
  # # -----------------------------------------------------------------------
  # # Handle SIGINT
  # signal.signal(signal.SIGINT, on_exit)
  # # Handle termination SIGTERM
  # signal.signal(signal.SIGTERM, on_exit)


if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  # Start main application
  main()
