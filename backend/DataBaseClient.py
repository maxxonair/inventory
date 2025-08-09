"""Client interface to the inventory Database tables

Inventory main table:
  name VARCHAR(255) NOT NULL
  image VARCHAR(1055)
  description VARCHAR(1055) 
  manufacturer VARCHAR(255)
  details VARCHAR(1055)
  is_checked_out BOOLEAN
  check_out_date VARCHAR(255) 
  check_out_poc VARCHAR(1055) 
  date_added VARCHAR(255) 
  tags VARCHAR(1055) 
  location VARCHAR(1055) 
  item_type VARCHAR(1055) 
  number_items INT(32) )

Raises:
    RuntimeError: _description_

Returns:
    _type_: _description_
"""
import mariadb
from logging import info, warning, debug, error
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import cv2 as cv

from backend.database_config import (INVENTORY_TABLE_NAME,
                                     INVENTORY_DB_NAME,
                                     INVENTORY_USER_TABLE_NAME,
                                     media_directory,
                                     database_host,
                                     database_port,
                                     DATABASE_USER_NAME,
                                     DATABASE_PASSWORD)
from backend.InventoryUser import InventoryUser


class DataBaseClient():

  def __init__(self, host: str = database_host, port: int = database_port):
    self.connection_config = {
        'user': DATABASE_USER_NAME,
        'password': DATABASE_PASSWORD,
        'host': host,
        'port': port,
        'database': INVENTORY_DB_NAME,
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

    # -- Ensure that database exists --
    if not self.is_database(INVENTORY_DB_NAME):
      error(
          f' {INVENTORY_DB_NAME} database not found.')
      exit(1)
    else:
      info(f'[x] {INVENTORY_DB_NAME} database found.')

    # Use inventory database from here onwards
    self.cursor.execute(f"USE {INVENTORY_DB_NAME}")

    # -- Ensure that inventory table exists --
    if not self.is_table(INVENTORY_TABLE_NAME):
      error(
          f' {INVENTORY_TABLE_NAME} table not found.')
      exit(1)
    else:
      info(f'[x] {INVENTORY_TABLE_NAME} table found.')

    # -- Ensure that inventory user table exists --
    if not self.is_table(INVENTORY_USER_TABLE_NAME):
      error(
          f' {INVENTORY_USER_TABLE_NAME} table not found.')
      exit(1)
    else:
      info(f'[x] {INVENTORY_USER_TABLE_NAME} table found.')

    # Initialize media folder
    self.init_media_dir()

  def close(self):
    """
    """
    self.cursor.close()
    self.connection.close()

  # -----------------------------------------------------------------------
  #                        [LIST & SEARCH]
  # -----------------------------------------------------------------------

  def list_tables(self):
    """
    Return a list of all tables
    """
    self.cursor.execute("SHOW TABLES;")
    db_list = []
    for (databases) in self.cursor:
      db_list.append(databases[0])
    return db_list

  def list_databases(self):
    """
    Return a list of all databases
    """
    self.cursor.execute("SHOW DATABASES")
    db_list = []
    for (databases) in self.cursor:
      db_list.append(databases[0])
    return db_list

  def is_database(self, database_name: str) -> bool:
    """
    Check if database of given name exists. If so return True, False 
    otherwise

    """
    db_list = self.list_databases()
    for element in db_list:
      if element == str(database_name):
        return True
    return False

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

    return df

  def get_inventory_item_as_df(self, item_id):
    """
    Return a specific inventory item identified by its ID from a database 
    in a pandas dataframe
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_TABLE_NAME} WHERE ID = %s"

    # Execute the query
    self.exec_sql_cmd(query, (item_id,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    info(f'Inventory data {df}')

    return df

  def get_inventory_item_as_dict(self, item_id) -> dict:
    """
    Return a specific inventory item identified by its ID from a database 
    as a dictionary
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_TABLE_NAME} WHERE ID = %s"

    # Execute the query
    self.exec_sql_cmd(query, (item_id,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    item_dict = df.to_dict('records')

    return item_dict[0]

  # ------------------------------------------------------------------------
  #                        [MODIFY]
  # ------------------------------------------------------------------------

  def create_database(self, database_name: str):
    """
    Create database
    """
    query = f'CREATE DATABASE `{database_name}`;'
    self.cursor.execute(query)

  def create_inventory_table(self):
    """
    Create inventory table 
    """
    # Compile query to create inventory table
    create_table_query = f'CREATE TABLE IF NOT EXISTS {
        INVENTORY_TABLE_NAME} ( id INT PRIMARY KEY AUTO_INCREMENT,'
    create_table_query += f'name VARCHAR(255) NOT NULL,'
    create_table_query += f'image VARCHAR(1055),'
    create_table_query += f'description VARCHAR(1055) ,'
    create_table_query += f'manufacturer VARCHAR(255),'
    create_table_query += f'details VARCHAR(1055),'
    create_table_query += f'is_checked_out BOOLEAN,'
    create_table_query += f'check_out_date VARCHAR(255) ,'
    create_table_query += f'check_out_poc VARCHAR(1055) ,'
    create_table_query += f'date_added VARCHAR(255) ,'
    create_table_query += f'tags VARCHAR(1055) ,'
    create_table_query += f'location VARCHAR(1055) ,'
    create_table_query += f'item_type VARCHAR(1055) ,'
    create_table_query += f'number_items INT(32) )'

    # Execute query
    self.cursor.execute(query)

    # Commit the transaction
    self.connection.commit()

  def create_inventory_user_table(self):
    """
    Create inventory user table 
    """
    # Create InventoryUser instance and compile query to create the user table
    user = InventoryUser('', '')
    query = user.get_sql_query_table_for_user()

    # Execute query
    self.cursor.execute(query)

    # Commit the transaction
    self.connection.commit()

  def _get_last_inserted_id(self) -> int:
    """
    Returns the ID of the most recent added item

    """
    sql = 'SELECT LAST_INSERT_ID()'
    # Execute the query
    self.exec_sql_cmd(sql, [])

    # Fetch all rows from the executed query
    id_list = self.cursor.fetchall()
    id_out = -1
    if len(id_list) == 1:
      id_out = id_list[0]
      id_out = int(id_out[0])

    return id_out

  def add_inventory_item(self, inventory_item_dict: dict) -> id:
    """
    Create row in INVENTORY_TABLE_NAME 


    returns ID of the created inventory item
    """
    # --- Construct the SQL INSERT statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
        [f"{column}" for column in list(inventory_item_dict.keys())])

    # Create series of ? that matches the number of values in
    # list(inventory_item_dict.values())
    value_clause = ", ".join(
        [f"?" for column in list(inventory_item_dict.values())])

    sql = f"INSERT INTO {INVENTORY_TABLE_NAME} ( {set_clause} ) VALUES ( {
        value_clause} )"

    # Prepare the data to update
    values = list(inventory_item_dict.values())

    self.exec_sql_cmd(sql, values)

    return self._get_last_inserted_id()

  def update_inventory_item(self, inventory_item_dict: dict, id: int):
    """
    Modify and inventory item identified by ID with given values
    """
    # --- Construct the SQL UPDATE statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
        [f"{column} = ?" for column in list(inventory_item_dict.keys())])

    sql = f"UPDATE {INVENTORY_TABLE_NAME} SET {set_clause} WHERE id = ?"

    # Prepare the data to update
    values = list(inventory_item_dict.values()) + [id]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def update_inventory_item_image_path(self, id: int, path: str):
    """
    Modify the image path of an inventory item identified by ID with the 
    given path
    """
    sql = f"UPDATE {INVENTORY_TABLE_NAME} SET image = ? WHERE id = ?"
    values = [path] + [id]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def update_inventory_item_checkout_status(self,
                                            item_id: int,
                                            poc: str,
                                            checkout_status: int = 1):
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
    if checkout_status == 1:
      sql = f"UPDATE {
          INVENTORY_TABLE_NAME} SET is_checked_out = ?, check_out_date = ?, check_out_poc = ? WHERE id = ?"
      values = [int(checkout_status)] + [check_out_date] + [poc] + [item_id]
    else:
      sql = f"UPDATE {
          INVENTORY_TABLE_NAME} SET is_checked_out = ? WHERE id = ?"
      values = [int(checkout_status)] + [item_id]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

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

    debug(f'Inventory data {df}')

    return data_list_out

  def delete_inventory_item(self, id: int):
    """
    Delete Inventory item
    """
    sql = f"DELETE FROM {INVENTORY_TABLE_NAME} WHERE id = ?"
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

  def init_media_dir(self):
    """
    Initialize subdirectory to store media data. Media data is data that will
    not be stored in the database itself (images, video, audio). The inventory
    database will hold a path to the respective file in the media folder instead.

    """
    if not media_directory.exists():
      info(f'[x] Create media directory at {media_directory}')
      os.makedirs(media_directory.absolute().as_posix(), 0o775)

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
    query = f"SELECT * FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = %s"

    # Execute the query
    self.exec_sql_cmd(query, (user_name,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    if len(rows) == 1:
      valid = True

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create InventoryUser instance
    inventoryUser = InventoryUser('', '')

    # Populate all fields from the database export
    inventoryUser.populate_from_df(
        user_data_df=pd.DataFrame(rows, columns=columns))
    return valid, inventoryUser

  def delete_inventory_user(self, user_name: str):
    """
    Delete Inventory user
    """
    info(f'[-] Delete user {user_name} ')
    sql = f"DELETE FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = ?"
    values = list([user_name])

    # Execute the DELETE statement
    self.exec_sql_cmd(sql, values)

  def add_inventory_user(self, user: InventoryUser):
    """
    Create column in INVENTORY_USER_TABLE_NAME 
    """
    info(
        f'[+] Add user {user.user_name} with privileges {user.user_privileges}')
    # SQL query to insert a new row into the table
    sql, values = user.get_sql_query_add_user()

    self.exec_sql_cmd(sql, values)

  def update_inventory_user_password(self, user: InventoryUser):
    """
    Update password of existing inventory user
    """
    sql = f"UPDATE {
        INVENTORY_USER_TABLE_NAME} SET user_password = ? WHERE user_name = ?"
    values = [user.user_password] + [user.user_name]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def update_inventory_user_privileges(self, user: InventoryUser):
    """
    Update privileges of existing inventory user
    """
    info(
        f'[+] Update privileges for user {user.user_name} to {user.user_privileges}')
    sql = f"UPDATE {
        INVENTORY_USER_TABLE_NAME} SET user_privileges = ? WHERE user_name = ?"
    values = [user.user_privileges] + [user.user_name]

    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

  def get_inventory_user_as_dict(self, user_name: str) -> dict:
    """
    Return a specific inventory user identified by its user_name as dictionary
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = %s"

    # Execute the query
    self.exec_sql_cmd(query, (user_name,))

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    item_dict = df.to_dict('records')

    return item_dict[0]

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

    # Create InventoryUser instance
    inventoryUser = InventoryUser('', '')

    # Populate all fields from the database export
    inventoryUser.populate_from_df(
        user_data_df=pd.DataFrame(rows, columns=columns))

    return valid, inventoryUser

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
