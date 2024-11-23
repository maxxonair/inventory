"""

Main application launcher

"""
from trame.app import get_server
import logging
from logging import info, warning, error, debug
from multiprocessing import Process, Manager

import asyncio
from signal import SIGINT, SIGTERM
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Class imports
from backend.CameraServer import CameraServer
from frontend.FrontendApplication import FrontendApplication
from backend.DataBaseClient import DataBaseClient

# --- Config imports
from backend.database_config import database_host, INVENTORY_DB_NAME

# camera_process = None
# ui_process = None

# Create Trame server
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller
state.trame__title = "inventory"

# Init default field for the parsed item ID (used by both camera server and
# UI)
state.parsed_item_id = None

# -----------------------------------------------------------------------
# -- FRONTEND SERVER
# -----------------------------------------------------------------------
# --- Create camera server instance
ui_server = FrontendApplication(server, state, ctrl)


def update_id(id: int):
  """
  Set item id and upate UI
  """
  global server, state, ctrl, ui_server
  state.parsed_item_id = id
  ui_server.populate_item_from_id(id)


# -----------------------------------------------------------------------
# -- CAMERA SERVER
# -----------------------------------------------------------------------
# --- Create camera server instance
camera_server = CameraServer(update_id)


def do_cleanup_event_loop(loop):
  """
  Clean up event loop by first stopping and then closing the loop.#

  This function is intended to be a callback for SIGNINT and SIGTERM events
  """
  info('SIGINT received. Stopping Event Loop')
  loop.stop()
  loop.close()


def main():
  """
  Main function to run and handle all components of this application:
   * The database client
   * The camera server
   * The UI server (aka frontend application)

  """
  global server, state, ctrl, ui_server, camera_server
  # -----------------------------------------------------------------------
  # -- START ALL THREADS
  # -----------------------------------------------------------------------
  # Create event loop
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)

  # ---- HANDLE SIGINT/SIGTERM PROCESSES ----
  # Set callbacks to handle sigint and sigterm events -> stop and close
  # event loop
  for signal in [SIGINT, SIGTERM]:
    loop.add_signal_handler(signal, do_cleanup_event_loop, loop)

  # ---- CHECK DATABASE CONNECTION ----
  # Check if database server is running by trying to locate the inventory
  # database
  if not DataBaseClient(database_host).is_database(INVENTORY_DB_NAME):
    raise RuntimeError('DATABASE NOT FOUND. Could not find inventory database')

  try:
    # ---- SET OBSERVER FOR QR MESSAGE ----
    class UpdateUIOnChange(FileSystemEventHandler):
      def on_modified(self, event):
        # Read item ID from file
        with open((Path(__file__).parent / 'temp' / 'qr').resolve(), "r") as qr_file:
          message = qr_file.readline().strip()

        # If file contains a message -> update the server state
        if message:
          item_id = int(message)
          loop.call_soon_threadsafe(update_id, item_id)

    # Create and start file watcher to monitor saved qr messages
    observer = Observer()
    print((Path(__file__).parent / 'temp' / 'qr').resolve())
    observer.schedule(
        UpdateUIOnChange(),
        (Path(__file__).parent / 'temp' / 'qr').resolve(),
        recursive=False
    )
    observer.start()

    # ---- START APPLICATION ----

    loop.run_until_complete(asyncio.gather(
        camera_server.run(), ui_server.run()))
  finally:
    error('Error in process. Closing')
    loop.close()


if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  # Start main application
  main()
