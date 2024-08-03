import mariadb
from logging import info, warning, debug, error
import pandas as pd
import os
from pathlib import Path
import cv2 as cv

from backend.database_config import (INVENTORY_TABLE_NAME,
                                     INVENTORY_DB_NAME,
                                     media_directory)
from backend.InventoryItem import InventoryItem


class DataBaseClient():

  def __init__(self, host: str, port: int = 3306):
    self.connection_config = {
        'user': 'inventory_user',
        'password': 'inventory24',
        'host': host,  # or use the container name 'mariadb'
        'port': port,
        'database': 'inventory'
    }

    try:
      # Establishing the connection
      self.connection = mariadb.connect(**self.connection_config)

      # Perform database operations
      self.cursor = self.connection.cursor()
      self.cursor.execute("SELECT DATABASE()")

      info("[x] Connected to the inventory database")
    except mariadb.Error as e:
      error()
      error(f"Error connecting to MariaDB: {e}")

    if not self.is_database(INVENTORY_DB_NAME):
      warning(
          f' {INVENTORY_DB_NAME} database not found.')
      self.create_database(INVENTORY_DB_NAME)
      info(f'[x] Created database: {INVENTORY_DB_NAME}')
    else:
      info(f'[x] {INVENTORY_DB_NAME} database found.')

    # Use inventory database from here onwards
    self.cursor.execute(f"USE {INVENTORY_DB_NAME}")

    if not self.is_table(INVENTORY_TABLE_NAME):
      warning(
          f' {INVENTORY_TABLE_NAME} table not found.')
      self.create_table(INVENTORY_TABLE_NAME)
      info(f'[x] Created table: {INVENTORY_TABLE_NAME}')
    else:
      info(f'[x] {INVENTORY_TABLE_NAME} table found.')

    # Initialize media folder
    self.init_media_dir()

  def close(self):
    """
    """
    self.cursor.close()
    self.connection.close()

  # ------------------------------------------------------------------------
  #                        [LIST & SEARCH]
  # ------------------------------------------------------------------------

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
    self.cursor.execute(query, (item_id,))

    self.connection.commit()

    # Fetch all rows from the executed query
    rows = self.cursor.fetchall()

    # Get column names from the cursor
    columns = [col[0] for col in self.cursor.description]

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(rows, columns=columns)

    info(f'Inventory data {df}')

    return df

  # ------------------------------------------------------------------------
  #                        [MODIFY]
  # ------------------------------------------------------------------------

  def create_database(self, database_name: str):
    """
    Create database
    """
    query = f'CREATE DATABASE `{database_name}`;'
    self.cursor.execute(query)

  def create_table(self, table_name: str):
    """
    Create table 
    """
    # Create dummy InventoryItem and get query
    item = InventoryItem('')
    query = item.get_sql_table_query()

    # Execute query
    self.cursor.execute(query)

    # Commit the transaction
    self.connection.commit()

  def add_inventory_item(self, inventory_item: InventoryItem):
    """
    Create column in INVENTORY_TABLE_NAME 
    """
    # SQL query to insert a new row into the table
    query = f'INSERT INTO {INVENTORY_TABLE_NAME} (item_name, '\
        'item_description, manufacturer, manufacturer_contact, is_checked_out, '\
        'check_out_date, date_added, item_image, item_tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'

    inventory_dict = inventory_item.get_item_dict()

    self.exec_sql_cmd(query, (inventory_dict["item_name"],
                              inventory_dict["item_description"],
                              inventory_dict["manufacturer"],
                              inventory_dict["manufacturer_contact"],
                              inventory_dict["is_checked_out"],
                              inventory_dict["check_out_date"],
                              inventory_dict["date_added"],
                              inventory_dict["item_image"],
                              inventory_dict["item_tags"]))

  def update_inventory_item(self, inventory_item: InventoryItem, id: int):
    """
    Modify and inventory item identified by ID with given values
    """
    sql, values = inventory_item.get_sql_item_query(id)
    # Execute the UPDATE statement
    self.exec_sql_cmd(sql, values)

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
    pwd_path = Path(os.path.realpath(__file__))
    media_directory = pwd_path.parent / '..' / 'database' / 'media'
    if not media_directory.exists():
      info(f'[x] Create media directory at {media_directory}')
      os.makedirs(media_directory.absolute().as_posix(), 0o775)

  def load_media_image(self, image_path: Path):
    """
    Load image file from media folder
    """
    return cv.imread(image_path.absolute().as_posix())
