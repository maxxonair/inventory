"""

Main application launcher

"""

import logging
from logging import info, warning, error, debug
from multiprocessing import Process, Manager
import multiprocessing
import sys
import signal

# --- Class imports
from backend.DataBaseClient import DataBaseClient
from backend.CameraServer import CameraServer
from frontend.FrontendApplication import FrontendApplication

# --- Config imports
from backend.database_config import database_host

camera_process = None
ui_process = None


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


def main():
  """
  Main function to run and handle all components of this application:
   * The database client
   * The camera server
   * The UI server (aka frontend application)

  """
  # -----------------------------------------------------------------------
  # --- Create database client instance
  # Create a DatabaseClient instance and connect to the inventory database
  db_client = DataBaseClient(host=database_host)
  # --- Create camera server instance
  camera_server = CameraServer()
  # --- Create camera server instance
  frontend_server = FrontendApplication(db_client=db_client,
                                        camera_server=camera_server)

  # TODO Add check if database server is running
  # -----------------------------------------------------------------------
  # -- CAMERA SERVER
  # -----------------------------------------------------------------------
  # Start the camera server in a background thread
  camera_process = Process(target=camera_server.run)
  camera_process.start()
  # -----------------------------------------------------------------------
  # -- FRONTEND SERVER
  # -----------------------------------------------------------------------
  # Start the camera server in a background thread
  ui_process = Process(target=frontend_server.start_server)
  ui_process.start()

  # -----------------------------------------------------------------------
  # -- HANDLE SIGINT/SIGTERM PROCESSES
  # -----------------------------------------------------------------------
  # Handle SIGINT
  signal.signal(signal.SIGINT, on_exit)
  # Handle termination SIGTERM
  signal.signal(signal.SIGTERM, on_exit)


if __name__ == "__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)

  # Start main application
  main()
