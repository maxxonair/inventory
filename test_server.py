from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_session import Session
from logging import info, error, warning, debug
import mariadb
import pandas as pd

from backend.InventoryUser import InventoryUser

MEDIA_DEFAULT_PATH = "/home/mrx/Documents/inventory/database/media/"

MEDIA_DEFAULT_URL = "http://127.0.0.1:5000/media/"

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
  def __init__(self, host: str = DEFAULT_DB_HOST, port: int = 46123, media_path: str = MEDIA_DEFAULT_PATH):
    self.app = Flask(__name__)
    CORS(self.app)  # Enable CORS

    # Set path to load media files from
    self.media_path = media_path

    # In-memory storage
    # self.users = [{"id": 1, "name": "romi"}, {"id": 2, "name": "peter"}]
    # self.next_id = 3

    self.connection_config = {
        'user': 'inventory_user',
        'password': 'inventory24',
        'host': host,
        'port': port,
        'database': 'inventory',
        'connect_timeout': 0
    }

    try:
      # Establishing the connection with the database server
      self.connection = mariadb.connect(**self.connection_config)

      # Perform database operations
      self.cursor = self.connection.cursor()
      self.cursor.execute("SELECT DATABASE()")

      info("[x] Connected to the inventory database")
    except mariadb.Error as e:
      error('')
      raise RuntimeError(f"Error connecting to MariaDB: {e}")

    # Routes
    self.configure_routes()

  def configure_routes(self):
    @self.app.route('/media/<filename>')
    def serve_image(filename):
      return send_from_directory(self.media_path, filename)

    @self.app.route('/users', methods=['GET'])
    def get_users():
      return jsonify(self.users)

    @self.app.route('/users', methods=['POST'])
    def add_user():
      data = request.get_json()
      name = data.get('name')
      new_user = {"id": self.next_id, "name": name}
      self.users.append(new_user)
      self.next_id += 1
      return jsonify(new_user), 201

    @self.app.route('/items')
    def get_items():
      data_dict = self.get_all_inventory_items_as_dict_list()
      return jsonify(data_dict)

    @self.app.route('/login', methods=['POST'])
    def login():
      data = request.json
      is_user_exists, inventoryUser = self.get_inventory_user_as_object(
          data['username'])
      if not is_user_exists:
        return jsonify({'error': 'User not found'}), 401
      if not inventoryUser.is_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

      self.session['user'] = data['username']
      return jsonify({'message': 'Login successful'})

    @self.app.route('/me')
    def me():
      if 'user' in self.session:
        return jsonify({'user': self.session['user']})
      return jsonify({'error': 'Not logged in'}), 401

  def run(self, **kwargs):
    self.app.run(**kwargs)

  def exec_sql_cmd(self, sql, values: list):
    """
    Generic execute SQL command defined by sql qery and its accompanying 
    values

    """
    # Execute the UPDATE statement
    self.cursor.execute(sql, values)

    # Commit the transaction
    self.connection.commit()

  def get_all_inventory_items_as_dict_list(self) -> list:
    """
    Return all content from a database in a pandas dataframe
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    data_list_out = df.to_dict('records')

    # TODO remove this after file names are saved correctly
    for dict_idx in range(len(data_list_out)):
      data_list_out[dict_idx]['item_image'] = str(data_list_out[dict_idx]['item_image']).replace(
          MEDIA_DEFAULT_PATH, MEDIA_DEFAULT_URL)
      debug(data_list_out[dict_idx]['item_image'])

    debug(f'Inventory data {df}')

    return data_list_out

  def get_inventory_user_as_object(self, user_name: str):
    """
    Return a specific inventory user identified by its user_name 
    as a InventoryUser object
    """
    valid = False
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = %s"

    # Execute the query
    self.exec_sql_cmd(query, (user_name,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    if len(rows) == 1:
      valid = True

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create InventoryItem instance
    inventoryUser = InventoryUser('', '')

    # Populate all fields from the database export
    inventoryUser.populate_from_df(
        user_data_df=pd.DataFrame(rows, columns=columns))
    return valid, inventoryUser


if __name__ == '__main__':
  server = InventoryServer()
  server.run(debug=True)
