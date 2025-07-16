"""                 [Inventory] Inventory Server 


For debugging run as a module with 

$ uv run -m backend.InventoryServer

"""
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_session import Session
from logging import info, error, debug
import mariadb
import pandas as pd
from datetime import timedelta
import asyncio
import sys
import os

from backend.InventoryUser import InventoryUser
from backend.DataBaseClient import DataBaseClient
from backend.InventoryItem import InventoryItem

from backend import (inventory_server_ip,
                     inventory_server_port)

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# TODO move constants
MEDIA_DEFAULT_PATH = "/home/mrx/Documents/inventory/database/media/"

DEFAULT_DB_HOST = '127.0.0.1'

# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = 'inventory'

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_TABLE_NAME = 'inventory'

# [CONSTANT] Name of the table in INVENTORY_DB_NAME database to store the
#            Inventory users
INVENTORY_USER_TABLE_NAME = 'inventory_user'


class InventoryServer:
  def __init__(self, 
               host: str = DEFAULT_DB_HOST, 
               port: int = 46123, 
               media_path: str = MEDIA_DEFAULT_PATH,
               session_timeout_min: float = 60.0):
    """Await docstring generation..."""
    self.app = Flask(__name__)
    self.app.secret_key = 'super-secret'
    self.app.config['SESSION_TYPE'] = 'filesystem'
    CORS(self.app, supports_credentials=True)  # Enable CORS
    Session(self.app)
    
    self.app.permanent_session_lifetime = timedelta(minutes=session_timeout_min)

    # Set path to load media files from
    self.media_path = media_path
    
    # Create a database client instance. The client will handle all interaction 
    # with the database server.
    self.db = DataBaseClient(host=host, port=port)

    # Routes
    self.configure_routes()

  def configure_routes(self):

    @self.app.route('/media/<filename>')
    def serve_image(filename):
      """Serve requested image from the media directory
      """
      return send_from_directory(self.media_path, filename)

    @self.app.route('/users', methods=['GET'])
    def get_users():
      if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
      return jsonify(self.users)

    @self.app.route('/checkout_item', methods=['POST'])
    def checkout_item():
      if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
      data = request.json
      self.db.update_inventory_item_checkout_status(int(data['itemId']), session['user'], 1)
      return jsonify({'message': f'Item {data['itemId']} checked out'})

    @self.app.route('/return_item', methods=['POST'])
    def return_item():
      if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
      data = request.json
      self.db.update_inventory_item_checkout_status(int(data['itemId']), session['user'], 0)
      return jsonify({'message': f'Item {data['itemId']} checked out'})

    @self.app.route('/items')
    def get_items():
      if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
      data_dict = self.db.get_all_inventory_items_as_dict_list()
      return jsonify(data_dict)

    @self.app.route('/login', methods=['POST'])
    def login():
      data = request.json
      is_user_exists, inventoryUser = self.db.get_inventory_user_as_object(
          data['username'])
      # TODO demote to debug message
      print(f'Log in attempt: {data['username']} -> {is_user_exists}')
      if not is_user_exists:
        return jsonify({'error': 'User not found'}), 401
      if not inventoryUser.is_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

      # Login valid -> Create a session cookie for this user 
      session['user'] = data['username']
      return jsonify({'message': 'Login successful'})

    @self.app.route('/add_item', methods=['POST'])
    def add_item():
      if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
      data = request.json
      new_id = self.db.add_inventory_item(inventory_item=InventoryItem(
          name=data['item_name'], 
          manufacturer=data['item_manufacturer'], 
          details=data['item_details'],
          item_type=data['item_type'],
          number_items=int(data['item_num']),
          image=data['image_name']))
      return jsonify({'message': f'{new_id}'}), 200

    @self.app.route('/logout', methods=['POST'])
    def logout(self):
      print('Log out user')
      session.clear()
      return jsonify({'message': 'Logged out'})
    
    @self.app.route('/capture_image', methods=['POST'])
    def capture_image():
      if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
      

    @self.app.route('/me')
    def me():
      # !TODO! somehow this returns 200 even if the user is logged out. 
      # Safeguarded by the frontend for now, but needs to be checked.
      if 'user' in session:
        return jsonify({'user': session['user']})
      return jsonify({'error': 'Not logged in'}), 401
    
    @self.app.route('/qr', methods=['POST'])
    def qr():
      data = request.get_json()
      id = data.get('id')
      print(f'QR with ID {id} scanned')
      
      return jsonify({'status': 'success'}), 200

  async def run(self, host: str = inventory_server_ip,
                port: int = inventory_server_port):
    """Run the server

    This function is to run the inventory server in a separate thread
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
  server = InventoryServer()
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(asyncio.gather(
      server.run()))
