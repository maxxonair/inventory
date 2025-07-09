"""Launch all required backend servers

Function to simplify launching all required backend servers in one go

"""
from logging import info, warning, error
import asyncio
import signal

from backend.InventoryServer import InventoryServer
from backend.CameraServer import CameraServer

should_exit = asyncio.Event()

async def shutdown(loop):
    info('SIGINT received. Shutting down...')
    should_exit.set()  # triggers the await to finish
  
async def main():
  # Create event loop
  loop = asyncio.get_event_loop()
  asyncio.set_event_loop(loop)
  stop_event = asyncio.Event()

  # ---- HANDLE SIGINT/SIGTERM PROCESSES ----
  # Signal handler
  for sig in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop)))

  # Crate servers 
  camera_server = CameraServer()
  inventory_server = InventoryServer()
  
  # ---- START APPLICATION ----
  server_tasks = [
    asyncio.create_task(camera_server.run(), name="CameraServer"),
    asyncio.create_task(inventory_server.run(), name="InventoryServer")
  ]

  # Wait for shutdown signal
  await stop_event.wait()
  info("Shutdown signal received, cancelling tasks...")

  for task in server_tasks:
    task.cancel()

  await asyncio.gather(*server_tasks, return_exceptions=True)
  info("All tasks cancelled. Exiting.")
  
if __name__ == "__main__":
  try:
      asyncio.run(main())
  except KeyboardInterrupt:
      info("KeyboardInterrupt caught in main")