
import sys
import os

# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from backend.camera_server.camera_app import *
import signal
import threading
from threading import Thread
import time
from multiprocessing import Process

camera_thread = Thread()
camera_process = None


def handle_exit(signal, frame):
  global camera_thread
  print('Exiting camera server')
  camera_process.join()
  exit(0)


def main():
  var = 1
  while True:
    var += 1
    print(f'Count #{var}')
    time.sleep(1)


if __name__ == "__main__":
  # camera_thread = start_camera_stream()

  camera_process = Process(target=run_camera_server)
  camera_process.start()

  # Handle SIGINT
  signal.signal(signal.SIGINT, handle_exit)
  # Handle termination SIGTERM
  signal.signal(signal.SIGTERM, handle_exit)

  main()
