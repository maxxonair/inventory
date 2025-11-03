"""[Inventory] Printer Server


For debugging run as a module with

$ uv run -m backend.PrinterServer

"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from logging import info, error
import asyncio
import requests

from .PrinterClient import PrinterClient
from .printer_config import PRINTER_SERVER_PORT, PRINTER_SERVER_IP

DEFAULT_INVENTORY_HOST = "192.168.1.194"
DEFAULT_INVENTORY_PORT = 5001


class PrinterServer:
  def __init__(self):
    self.app = Flask(__name__)
    # Enable CORS
    CORS(self.app, supports_credentials=True)

    self.printer_client = PrinterClient()
    self.register_with_inventory()
    # Routes
    self.configure_routes()

  def register_with_inventory(self):
    printer_server_url = f"http://{PRINTER_SERVER_IP}:{PRINTER_SERVER_PORT}"
    try:
      res = requests.post(
        f"http://{DEFAULT_INVENTORY_HOST}:{DEFAULT_INVENTORY_PORT}/register_printer",
        json={"url": printer_server_url},
      )
      print(f"Register response: {res.status_code} -> {res.text}")
    except Exception as e:
      error(f"Failed to register printer: {e}")
      exit(1)

  def configure_routes(self):
    @self.app.route("/print_label", methods=["POST"])
    def print_label():
      """Print item QR label"""
      data = request.get_json()
      item_id = int(data.get("itemId"))
      print(f"Print label for item with ID {item_id}")

      # Issue label print job
      self.printer_client.print_qr_label_from_id(item_id)

      return jsonify({"status": "success"}), 200

  async def run(self, host: str = PRINTER_SERVER_IP, port: int = PRINTER_SERVER_PORT):
    """Run the server

    This function is to run the printer server in a separate thread
    """

    def start_flask():
      self.app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

    # Run the Flask app in a separate thread and return it as an asyncio
    # task
    return await asyncio.to_thread(start_flask)

  async def stop(self):
    info("Stopping Printer Server...")


if __name__ == "__main__":
  """Allows to run the server directly as module
  """
  server = PrinterServer()
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(asyncio.gather(server.run()))
