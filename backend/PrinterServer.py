"""                 [Inventory] Printer Server 


For debugging run as a module with 

$ uv run -m backend.PrinterServer

"""
from flask import Flask, request, jsonify,  session
from flask_cors import CORS
from flask_session import Session
from logging import info
import asyncio

from backend.PrinterClient import PrinterClient

# --- CONSTANTS ----
PRINTER_SEVER_IP = "127.0.0.1"
PRINTER_SERVER_PORT = 5100

class PrinterServer:
  def __init__(self):
    """Await docstring generation..."""
    self.app = Flask(__name__)
    # Enable CORS
    CORS(self.app, supports_credentials=True)  
    Session(self.app)

    self.printer_client = PrinterClient()

    # Routes
    self.configure_routes()

  def configure_routes(self):

    @self.app.route('/print_label', methods=['POST'])
    def print_label():
      """Print item label 

      """
      if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
      data = request.get_json()
      item_id = int(data.get('itemId'))
      print(f'Print label for item with ID {item_id}')

      # Issue label print job
      self.printer_client.print_qr_label_from_id(item_id)

      return jsonify({'status': 'success'}), 200
  
  async def run(self, host: str = PRINTER_SEVER_IP,
                port: int = PRINTER_SERVER_PORT):
    """Run the server

    This function is to run the printer server in a separate thread
    """
    def start_flask():
      self.app.run(host=host,
                   port=port,
                   debug=False,
                   use_reloader=False,
                   threaded=True)
    # Run the Flask app in a separate thread and return it as an asyncio
    # task
    return await asyncio.to_thread(start_flask)

  async def stop(self):
    info("Stopping Inventory Server...")


if __name__ == '__main__':
  """Allows to run the server directly as module
  """
  server = PrinterServer()
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(asyncio.gather(
      server.run()))
