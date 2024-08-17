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
frontend_server = None

# TODO check if these variables are of value and delete otherwise
dummy_id = multiprocessing.Value('d', 0.0)  # 'd' is for double (float)
condition = multiprocessing.Condition()

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
    frontend_server.join()
  except:
    warning(f'Failed to exit frontend server!')
    
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
  camera_server = CameraServer(dummy_id, condition)
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
  db_client_process = Process(target=frontend_server.start_server)
  db_client_process.start()
  
  # -----------------------------------------------------------------------
  # -- HANDLE SIGINT/SIGTERM PROCESSES
  # -----------------------------------------------------------------------
  # Handle SIGINT
  signal.signal(signal.SIGINT, on_exit)
  # Handle termination SIGTERM
  signal.signal(signal.SIGTERM, on_exit)
  
if __name__=="__main__":
  # Initialize logging
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)
  
  # Start main application
  main()