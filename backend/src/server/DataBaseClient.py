"""Client interface to the sqllite database used to store inventory data.

Provides functions to connect to the database, query and modify inventory data,
and manage inventory users. The database schema is defined in the
inventory_config.py file and is initialised if it does not exist when the
client connects to the database.

"""

import sqlite3
from logging import info, warning, debug, error
import pandas as pd
from datetime import datetime
from pathlib import Path
import cv2 as cv

from server.database_config import (
  INVENTORY_REGISTRY_TABLE_NAME,
  INVENTORY_LOGIN_TABLE_NAME,
  INVENTORY_CHECKOUT_TABLE_NAME,
  INVENTORY_STORAGE_LOCATIONS_TABLE_NAME,
  INVENTORY_USER_TABLE_NAME,
  LoginStatus,
  CheckoutType,
)
from server.InventoryUser import InventoryUser, UserPrivileges

# --- CONSTANTS ---

# Compile query to create inventory table
INVENTORY_REGISTRY_TABLE_QUERY = f"CREATE TABLE IF NOT EXISTS {
  INVENTORY_REGISTRY_TABLE_NAME
} ( id INTEGER PRIMARY KEY AUTOINCREMENT,"
INVENTORY_REGISTRY_TABLE_QUERY += "name VARCHAR(255) NOT NULL,"
INVENTORY_REGISTRY_TABLE_QUERY += "image VARCHAR(1055),"
INVENTORY_REGISTRY_TABLE_QUERY += "description VARCHAR(1055) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "manufacturer VARCHAR(255),"
INVENTORY_REGISTRY_TABLE_QUERY += "details VARCHAR(1055),"
INVENTORY_REGISTRY_TABLE_QUERY += "is_checked_out INTEGER,"
INVENTORY_REGISTRY_TABLE_QUERY += "check_out_date VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "check_out_poc VARCHAR(1055) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "date_added VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "tags VARCHAR(1055) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "location INTEGER ,"
INVENTORY_REGISTRY_TABLE_QUERY += "item_type VARCHAR(1055) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "manufacturer_link VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "project VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "manufacturer_location VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "color VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "material VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "product_use VARCHAR(255) ,"
INVENTORY_REGISTRY_TABLE_QUERY += "number_items INTEGER )"

INVENTORY_STORAGE_LOCATIONS_TABLE_QUERY = f"CREATE TABLE IF NOT EXISTS {
  INVENTORY_STORAGE_LOCATIONS_TABLE_NAME
} ( id INTEGER PRIMARY KEY AUTOINCREMENT,"
INVENTORY_STORAGE_LOCATIONS_TABLE_QUERY += "name VARCHAR(255) NOT NULL,"
INVENTORY_STORAGE_LOCATIONS_TABLE_QUERY += "description VARCHAR(1055) ,"
INVENTORY_STORAGE_LOCATIONS_TABLE_QUERY += "date_added VARCHAR(255) ,"
INVENTORY_STORAGE_LOCATIONS_TABLE_QUERY += "tags VARCHAR(1055) )"

# Compile query to create inventory table to store login events
INVENTORY_LOGIN_TABLE_QUERY = f"CREATE TABLE IF NOT EXISTS {
  INVENTORY_LOGIN_TABLE_NAME
} ( id INTEGER PRIMARY KEY AUTOINCREMENT,"
INVENTORY_LOGIN_TABLE_QUERY += "user VARCHAR(255) NOT NULL,"
INVENTORY_LOGIN_TABLE_QUERY += "status INTEGER ,"
INVENTORY_LOGIN_TABLE_QUERY += "date VARCHAR(255) )"

# Compile query to create inventory table to store checkout events
# checkout - Status (direction) of the checkout.
#            checkout = 1 means item was checked out,
#            checkout = 0 means item was returned
INVENTORY_CHECKOUT_TABLE_QUERY = f"CREATE TABLE IF NOT EXISTS {
  INVENTORY_CHECKOUT_TABLE_NAME
} ( id INTEGER PRIMARY KEY AUTOINCREMENT,"
INVENTORY_CHECKOUT_TABLE_QUERY += "user VARCHAR(255) NOT NULL,"
INVENTORY_CHECKOUT_TABLE_QUERY += "item_id INTEGER ,"
INVENTORY_CHECKOUT_TABLE_QUERY += "checkout INTEGER ,"
INVENTORY_CHECKOUT_TABLE_QUERY += "date VARCHAR(255) )"


class DataBaseClient:
  def __init__(self, host: str = None, port: int = None):
    """Initialise database client and connect to the database server"""
    # Establishing the connection with the database server
    # TODO set database path
    if not Path("./db/inventory.db").exists():
      warning("Inventory database not found. Initialising new database.")
      Path("./db/inventory.db").parent.mkdir(parents=True, exist_ok=True)
    self.connection = sqlite3.connect("./db/inventory.db")
    self.cursor = self.connection.cursor()
    self.init_inventory_db()

  def connect(self) -> bool:
    """Connect to the database server and ensure that the inventory database

    Returns:
        bool: True if connection was successful, False otherwise
    """

    # -- Ensure that inventory registry table exists --
    if not self.is_table(INVENTORY_REGISTRY_TABLE_NAME):
      error(f" {INVENTORY_REGISTRY_TABLE_NAME} table not found.")
      exit(1)
    else:
      info(f"[x] {INVENTORY_REGISTRY_TABLE_NAME} table found.")

    # -- Ensure that inventory storage locations table exists --
    if not self.is_table(INVENTORY_STORAGE_LOCATIONS_TABLE_NAME):
      error(f" {INVENTORY_STORAGE_LOCATIONS_TABLE_NAME} table not found.")
      exit(1)
    else:
      info(f"[x] {INVENTORY_STORAGE_LOCATIONS_TABLE_NAME} table found.")

    # -- Ensure that inventory user table exists --
    if not self.is_table(INVENTORY_USER_TABLE_NAME):
      error(f" {INVENTORY_USER_TABLE_NAME} table not found.")
      exit(1)
    else:
      info(f"[x] {INVENTORY_USER_TABLE_NAME} table found.")
    return True

  def close_connection(self):
    """Close database connection"""
    try:
      self.connection.close()
    except Exception as e:
      error(f"Failed to close database connection: {e}")

  def init_inventory_db(self):
    """Initialise inventory database and tables if they don't exist

    Returns:
        _type_: _description_
    """
    info("Initialising inventory database:")

    # -- Ensure that inventory tables exists --
    self._init_table(INVENTORY_REGISTRY_TABLE_NAME, INVENTORY_REGISTRY_TABLE_QUERY)
    self._init_table(
      INVENTORY_STORAGE_LOCATIONS_TABLE_NAME, INVENTORY_STORAGE_LOCATIONS_TABLE_QUERY
    )
    self._init_table(INVENTORY_LOGIN_TABLE_NAME, INVENTORY_LOGIN_TABLE_QUERY)
    self._init_table(INVENTORY_CHECKOUT_TABLE_NAME, INVENTORY_CHECKOUT_TABLE_QUERY)

    user = InventoryUser(
      user_name="admin",
      user_password="admin",
      user_privileges=UserPrivileges.OWNER,
    )
    if self._init_table(INVENTORY_USER_TABLE_NAME, user.get_sql_query_table_for_user()):
      # If user table was just created, add default admin user
      info("First time setup: Adding default admin")
      info("Username: admin")
      info("Password: admin")
      self.add_inventory_user(user)

  # -----------------------------------------------------------------------
  #                        [LIST & SEARCH]
  # -----------------------------------------------------------------------
  def _init_table(self, table_name: str, query: str) -> bool:
    """
    Initialise table

    Args:
        table_name (str): Name of the table to initialise

    Returns:
        bool: True if table was created, False if table already existed.
    """
    if not self.is_table(table_name):
      warning(f" {table_name} table not found.")
      self.create_inventory_table(query)
      info(f"|-> Created table: {table_name}")
      return True
    else:
      info(f"[x] {table_name} does already exist.")
      return False

  def list_tables(self):
    """
    Return a list of all tables
    """
    self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    db_list = []
    for databases in self.cursor:
      db_list.append(databases[0])
    return db_list

  def is_table(self, table_name: str) -> bool:
    """
    Check if table of given name exists. If so return True, False
    otherwise

    """
    table_list = self.list_tables()
    for element in table_list:
      if element == str(table_name):
        return True
    return False

  def show_inventory_content(self):
    """
    Debug function: Print all content of the inventory table
    """
    df = self.get_inventory_as_df()
    info(df)

  def get_inventory_as_df(self):
    """
    Return all content from a database in a pandas dataframe
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_REGISTRY_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    return df

  def get_inventory_item_as_df(self, item_id):
    """
    Return a specific inventory item identified by its ID from a database
    in a pandas dataframe
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_REGISTRY_TABLE_NAME} WHERE id = ?"

    # Execute the query
    self.exec_sql_cmd(query, (item_id,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    info(f"Inventory data {df}")

    return df

  def get_inventory_item_as_dict(self, item_id) -> dict:
    """
    Return a specific inventory item identified by its ID from a database
    as a dictionary
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_REGISTRY_TABLE_NAME} WHERE id = ?"

    # Execute the query
    self.exec_sql_cmd(query, (item_id,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    item_dict = df.to_dict("records")

    return item_dict[0]

  # ------------------------------------------------------------------------
  #                        [MODIFY]
  # ------------------------------------------------------------------------

  def create_database(self, database_name: str):
    """
    Create database
    """
    query = f"CREATE DATABASE `{database_name}`;"
    self.cursor.execute(query)

  def create_inventory_table(self, query: str):
    """
    Create inventory table

    Args:
        query (str): SQL query to create the inventory table
    """
    # Execute query
    self.cursor.execute(query)

    # Commit the transaction
    self.connection.commit()

  def _get_last_inserted_id(self) -> int:
    """
    Returns the ID of the most recent added item
    """
    return self.cursor.lastrowid

  def add_inventory_item(self, inventory_item_dict: dict) -> id:
    """
    Create row in INVENTORY_TABLE_NAME


    returns ID of the created inventory item
    """
    # --- Construct the SQL INSERT statement

    # Pre-construct set each value statement
    set_clause = ", ".join([f"{column}" for column in list(inventory_item_dict.keys())])

    # Create series of ? that matches the number of values in
    # list(inventory_item_dict.values())
    value_clause = ", ".join(["?" for column in list(inventory_item_dict.values())])

    sql = f"INSERT INTO {INVENTORY_REGISTRY_TABLE_NAME} ( {set_clause} ) VALUES ( {value_clause} )"

    # Prepare the data to update
    values = list(inventory_item_dict.values())

    self.exec_sql_cmd(sql, values)

    return self._get_last_inserted_id()

  def add_storage_location(self, storage_location_dict: dict) -> int:
    """
    Create row in INVENTORY_STORAGE_LOCATIONS_TABLE_NAME


    returns ID of the created storage location
    """
    # --- Construct the SQL INSERT statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
      [f"{column}" for column in list(storage_location_dict.keys())]
    )

    # Create series of ? that matches the number of values in
    value_clause = ", ".join(["?" for column in list(storage_location_dict.values())])

    sql = f"INSERT INTO {INVENTORY_STORAGE_LOCATIONS_TABLE_NAME} ( {set_clause} ) VALUES ( {value_clause} )"

    # Prepare the data to update
    values = list(storage_location_dict.values())

    self.exec_sql_cmd(sql, values)

    return self._get_last_inserted_id()

  def update_storage_location(self, storage_location_dict: dict, id: int):
    """
    Modify a storage location identified by ID with given values
    """
    # --- Construct the SQL UPDATE statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
      [f"{column} = ?" for column in list(storage_location_dict.keys())]
    )

    sql = (
      f"UPDATE {INVENTORY_STORAGE_LOCATIONS_TABLE_NAME} SET {set_clause} WHERE id = ?"
    )

    # Prepare the data to update
    values = list(storage_location_dict.values()) + [id]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def delete_storage_location(self, id: int):
    """
    Delete Storage location
    """
    sql = f"DELETE FROM {INVENTORY_STORAGE_LOCATIONS_TABLE_NAME} WHERE id = ?"
    values = list([id])

    # Execute the DELETE statement
    self.exec_sql_cmd(sql, values)

  def get_all_storage_locations_as_dict_list(self) -> list:
    """
    Return all content from storage locations table in a list of dictionaries
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_STORAGE_LOCATIONS_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    data_list_out = df.to_dict("records")

    debug(f"Storage location data {df}")

    return data_list_out

  def update_inventory_item(self, inventory_item_dict: dict, id: int):
    """
    Modify and inventory item identified by ID with given values
    """
    # --- Construct the SQL UPDATE statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
      [f"{column} = ?" for column in list(inventory_item_dict.keys())]
    )

    sql = f"UPDATE {INVENTORY_REGISTRY_TABLE_NAME} SET {set_clause} WHERE id = ?"

    # Prepare the data to update
    values = list(inventory_item_dict.values()) + [id]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def update_inventory_item_image_path(self, id: int, path: str):
    """
    Modify the image path of an inventory item identified by ID with the
    given path
    """
    sql = f"UPDATE {INVENTORY_REGISTRY_TABLE_NAME} SET image = ? WHERE id = ?"
    values = [path] + [id]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def update_inventory_item_checkout_status(
    self, item_id: int, poc: str, checkout_type: CheckoutType
  ):
    """Modify the  item checkout status of an inventory item identified by ID
    with the parameters provided

    Args:
        id (int): Item ID
        poc (str): Check-out point of contact user name
        checkout_status (int): Check-out status flag. If 1 item is checked out,
            0 otherwise.
    """
    date_time_now = datetime.now()
    check_out_date = date_time_now.strftime("%m/%d/%Y, %H:%M:%S")
    if checkout_type.value == CheckoutType.BORROW.value:
      # CASE: Item is being checked out
      sql = f"UPDATE {
        INVENTORY_REGISTRY_TABLE_NAME
      } SET is_checked_out = ?, check_out_date = ?, check_out_poc = ? WHERE id = ?"
      values = [1] + [check_out_date] + [poc] + [item_id]
      self.exec_sql_cmd(sql, values)

    elif checkout_type.value == CheckoutType.RETURN.value:
      # CASE: Item is being returned
      sql = (
        f"UPDATE {INVENTORY_REGISTRY_TABLE_NAME} SET is_checked_out = ? WHERE id = ?"
      )
      values = [0] + [item_id]
      self.exec_sql_cmd(sql, values)

    log_sql = (
      f"INSERT INTO {INVENTORY_CHECKOUT_TABLE_NAME} ( user, item_id, "
      "checkout, date ) VALUES ( ?, ?, ?, ? )"
    )
    log_values = [poc] + [item_id] + [int(checkout_type.value)] + [check_out_date]
    self.exec_sql_cmd(log_sql, log_values)

  def log_user_login(self, user_name: str, status: LoginStatus):
    """Log user login attempt in the inventory login table

    Args:
        user_name (str): User name
        status (LoginStatus): Login status
    """
    log_sql = f"INSERT INTO {INVENTORY_LOGIN_TABLE_NAME} ( user, status, date ) VALUES ( ?, ?, ? )"
    date_time_now = datetime.now()
    log_date = date_time_now.strftime("%Y/%m/%d %H:%M:%S")
    log_values = [user_name] + [status.value] + [log_date]
    self.exec_sql_cmd(log_sql, log_values)

  def get_all_inventory_items_as_dict_list(self) -> list:
    """
    Return all content from a database in a pandas dataframe
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_REGISTRY_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    data_list_out = df.to_dict("records")

    debug(f"Inventory data {df}")

    return data_list_out

  def get_all_inventory_as_df(self) -> pd.DataFrame:
    """
    Return all content from a database in a pandas dataframe
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_REGISTRY_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    return pd.DataFrame(rows, columns=columns)

  def get_login_log_as_df(self) -> pd.DataFrame:
    """Return all login log entries as a list of dictionaries"""
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_LOGIN_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    return pd.DataFrame(rows, columns=columns)

  def get_checkout_log_as_df(self) -> pd.DataFrame:
    """Return item borrow/return log entries as a pandas dataframe"""
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_CHECKOUT_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    return pd.DataFrame(rows, columns=columns)

  def delete_inventory_item(self, id: int):
    """
    Delete Inventory item
    """
    sql = f"DELETE FROM {INVENTORY_REGISTRY_TABLE_NAME} WHERE id = ?"
    values = list([id])

    # Execute the DELETE statement
    self.exec_sql_cmd(sql, values)

  def exec_sql_cmd(self, sql, values: list):
    """
    Generic execute SQL command defined by sql qery and its accompanying
    values

    """
    # Execute the UPDATE statement
    self.cursor.execute(sql, values)

    # Commit the transaction
    self.connection.commit()

  # -----------------------------------------------------------------------
  #                        [MISC]
  # -----------------------------------------------------------------------

  def load_media_image(self, image_path: Path):
    """
    Load image file from media folder
    """
    return cv.imread(image_path.absolute().as_posix())

  # -----------------------------------------------------------------------
  #                 [INVENTORY USER FUNCTIONS]
  # -----------------------------------------------------------------------
  def get_inventory_user_as_object(self, user_name: str):
    """
    Return a specific inventory user identified by its user_name
    as a InventoryUser object
    """
    valid = False
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = ?"

    # Execute the query
    self.exec_sql_cmd(query, (user_name,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    if len(rows) == 1:
      valid = True

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create InventoryUser instance
    inventoryUser = InventoryUser("", "")

    # Populate all fields from the database export
    inventoryUser.populate_from_df(user_data_df=pd.DataFrame(rows, columns=columns))
    return valid, inventoryUser

  def delete_inventory_user(self, user_name: str):
    """
    Delete Inventory user
    """
    info(f"[-] Delete user {user_name} ")
    sql = f"DELETE FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = ?"
    values = list([user_name])

    # Execute the DELETE statement
    self.exec_sql_cmd(sql, values)

  def add_inventory_user(self, user: InventoryUser):
    """
    Create column in INVENTORY_USER_TABLE_NAME
    """
    info(f"[+] Add user {user.user_name} with privileges {user.user_privileges}")
    # SQL query to insert a new row into the table
    sql, values = user.get_sql_query_add_user()

    self.exec_sql_cmd(sql, values)

  def update_inventory_user_password(self, user: InventoryUser):
    """
    Update password of existing inventory user
    """
    sql = (
      f"UPDATE {INVENTORY_USER_TABLE_NAME} SET user_password = ? WHERE user_name = ?"
    )
    values = [user.hashed_user_password] + [user.user_name]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def update_inventory_user_privileges(self, user: InventoryUser):
    """
    Update privileges of existing inventory user
    """
    info(f"[+] Update privileges for user {user.user_name} to {user.user_privileges}")
    sql = (
      f"UPDATE {INVENTORY_USER_TABLE_NAME} SET user_privileges = ? WHERE user_name = ?"
    )
    values = [user.user_privileges] + [user.user_name]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def get_inventory_user_as_dict(self, user_name: str) -> dict:
    """
    Return a specific inventory user identified by its user_name as dictionary
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = ?"

    # Execute the query
    self.exec_sql_cmd(query, (user_name,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    item_dict = df.to_dict("records")

    return item_dict[0]

  def get_inventory_users_as_df(self):
    """
    Return all content from a inventory users table in a pandas dataframe
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_USER_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    return df

  def get_all_inventory_users_as_dict_list(self) -> list:
    """
    Return all inventory users as a list of dictionaries
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_USER_TABLE_NAME}"

    # Execute the query
    self.cursor.execute(query)

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    data_list_out = df.to_dict("records")

    debug(f"Inventory users {df}")

    return data_list_out

  def get_storage_location(self, storage_id: int) -> dict:
    """
    Return all inventory users as a list of dictionaries
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_STORAGE_LOCATIONS_TABLE_NAME} WHERE id = ?"

    # Execute the query
    self.cursor.execute(query, (storage_id,))

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    data_dict_out = df.to_dict("records")

    return data_dict_out

  def get_storage_items(self, storage_id: int) -> dict:
    """Return all inventory items stored at a specific storage location as a
    list of dictionaries
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_REGISTRY_TABLE_NAME} WHERE location = ?"

    # Execute the query
    self.cursor.execute(query, (storage_id,))

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    data_dict_out = df.to_dict("records")

    return data_dict_out
