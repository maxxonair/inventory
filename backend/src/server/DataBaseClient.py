"""Client interface to the sqllite database used to store inventory data.

Provides functions to connect to the database, query and modify inventory data,
and manage inventory users. The database schema is defined in the
database_schema.py file and is initialised if it does not exist when the
client connects to the database.

"""

import hashlib
import sqlite3
from logging import info, warning, debug, error
import pandas as pd
from datetime import datetime
from pathlib import Path
import cv2 as cv

from server.database_schema import (
  LoginStatus,
  CheckoutType,
  UserPrivileges,
  INVENTORY_REGISTRY_TABLE_NAME,
  INVENTORY_LOGIN_TABLE_NAME,
  INVENTORY_CHECKOUT_TABLE_NAME,
  INVENTORY_STORAGE_LOCATIONS_TABLE_NAME,
  INVENTORY_USER_TABLE_NAME,
  INVENTORY_ITEM_TYPES_TABLE_NAME,
  ALL_TABLE_SCHEMAS,
  INVENTORY_REGISTRY_SCHEMA,
  INVENTORY_STORAGE_LOCATIONS_SCHEMA,
  INVENTORY_LOGIN_SCHEMA,
  INVENTORY_CHECKOUT_SCHEMA,
  INVENTORY_USER_SCHEMA,
  INVENTORY_ITEM_TYPES_SCHEMA,
)

# --- CONSTANTS ---

# Salt used when hashing user passwords before they are persisted.
# TODO to be changed and moved out of here
PASSWORD_SALT = "sda8DF7d13e3F2"


def _hash_password(password: str) -> str:
  """Hash a plaintext password (with a static salt) for storage/comparison"""
  salted_password = password + PASSWORD_SALT
  return hashlib.md5(salted_password.encode()).hexdigest()


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
    # -- Ensure that every expected table exists --
    for schema in ALL_TABLE_SCHEMAS:
      if not self.is_table(schema.name):
        error(f" {schema.name} table not found.")
        exit(1)
      else:
        debug(f"[x] {schema.name} table found.")
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
    debug("Initialising inventory database:")

    # -- Ensure that inventory tables exist --
    for schema in (
      INVENTORY_REGISTRY_SCHEMA,
      INVENTORY_STORAGE_LOCATIONS_SCHEMA,
      INVENTORY_LOGIN_SCHEMA,
      INVENTORY_CHECKOUT_SCHEMA,
      INVENTORY_ITEM_TYPES_SCHEMA,
    ):
      self._init_table(schema.name, schema.create_table_query())

    # -- Ensure that inventory user table exists --
    user_table_created = self._init_table(
      INVENTORY_USER_TABLE_NAME, INVENTORY_USER_SCHEMA.create_table_query()
    )
    if user_table_created:
      # If user table was just created, add default admin user
      info("First time setup: Adding default admin")
      info("Username: admin")
      info("Password: admin")
      self.add_inventory_user(
        user_name="admin",
        user_password="admin",
        user_privileges=UserPrivileges.OWNER,
      )

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
      debug(f"[x] {table_name} does already exist.")
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

  def _build_insert_query(self, table_name: str, data: dict) -> tuple[str, list]:
    """
    Build a generic parameterised INSERT statement for the given table from
    a dictionary mapping column names to values
    """
    columns_clause = ", ".join(str(column) for column in data.keys())
    placeholders = ", ".join(["?" for _ in data])

    sql = f"INSERT INTO {table_name} ( {columns_clause} ) VALUES ( {placeholders} )"
    values = list(data.values())

    return sql, values

  def _build_update_query(
    self, table_name: str, data: dict, where_column: str, where_value
  ) -> tuple[str, list]:
    """
    Build a generic parameterised UPDATE statement for the given table from
    a dictionary mapping column names to values, matching a single
    WHERE column = value clause
    """
    set_clause = ", ".join(f"{column} = ?" for column in data.keys())

    sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_column} = ?"
    values = list(data.values()) + [where_value]

    return sql, values

  def add_inventory_item(self, inventory_item_dict: dict) -> int:
    """
    Create row in INVENTORY_TABLE_NAME


    returns ID of the created inventory item
    """
    sql, values = self._build_insert_query(
      INVENTORY_REGISTRY_TABLE_NAME, inventory_item_dict
    )
    self.exec_sql_cmd(sql, values)

    return self._get_last_inserted_id()

  def add_storage_location(self, storage_location_dict: dict) -> int:
    """
    Create row in INVENTORY_STORAGE_LOCATIONS_TABLE_NAME


    returns ID of the created storage location
    """
    sql, values = self._build_insert_query(
      INVENTORY_STORAGE_LOCATIONS_TABLE_NAME, storage_location_dict
    )
    self.exec_sql_cmd(sql, values)

    return self._get_last_inserted_id()

  def update_storage_location(self, storage_location_dict: dict, id: int):
    """
    Modify a storage location identified by ID with given values
    """
    sql, values = self._build_update_query(
      INVENTORY_STORAGE_LOCATIONS_TABLE_NAME, storage_location_dict, "id", id
    )
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
    sql, values = self._build_update_query(
      INVENTORY_REGISTRY_TABLE_NAME, inventory_item_dict, "id", id
    )
    self.exec_sql_cmd(sql, values)

  # -----------------------------------------------------------------------
  #                 [ITEM TYPE FUNCTIONS]
  # -----------------------------------------------------------------------
  def add_item_type(self, name: str) -> int:
    """
    Create a new row in INVENTORY_ITEM_TYPES_TABLE_NAME

    returns ID of the created item type

    Raises:
        sqlite3.IntegrityError: if an item type with this name already exists
    """
    sql, values = self._build_insert_query(
      INVENTORY_ITEM_TYPES_TABLE_NAME, {"name": str(name)}
    )
    self.exec_sql_cmd(sql, values)

    return self._get_last_inserted_id()

  def update_item_type(self, item_type_id: int, name: str):
    """
    Rename an existing item type identified by ID

    Raises:
        sqlite3.IntegrityError: if another item type with this name already
            exists
    """
    sql, values = self._build_update_query(
      INVENTORY_ITEM_TYPES_TABLE_NAME, {"name": str(name)}, "id", item_type_id
    )
    self.exec_sql_cmd(sql, values)

  def delete_item_type(self, item_type_id: int):
    """
    Delete an item type identified by ID
    """
    sql = f"DELETE FROM {INVENTORY_ITEM_TYPES_TABLE_NAME} WHERE id = ?"
    values = list([item_type_id])

    # Execute the DELETE statement
    self.exec_sql_cmd(sql, values)

  def get_all_item_types_as_dict_list(self) -> list:
    """
    Return all defined item types as a list of dictionaries
    """
    # Query to fetch all data from the specified table
    query = f"SELECT * FROM {INVENTORY_ITEM_TYPES_TABLE_NAME}"

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

    debug(f"Item types {df}")

    return data_list_out

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
  def get_inventory_user_as_dict(self, user_name: str) -> dict | None:
    """
    Return a specific inventory user identified by its user_name as a
    dictionary, or None if no such user exists
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

    records = df.to_dict("records")

    return records[0] if records else None

  def authenticate_user(
    self, user_name: str, password: str
  ) -> tuple[LoginStatus, dict | None]:
    """
    Validate a user's credentials against the stored (hashed) password.

    Returns a tuple of (LoginStatus, user_dict). user_dict is only
    populated when authentication succeeds, otherwise it is None.
    """
    user_dict = self.get_inventory_user_as_dict(user_name)
    if user_dict is None:
      return LoginStatus.USER_NOT_FOUND, None

    if _hash_password(password) != user_dict["user_password"]:
      return LoginStatus.PASSWORD_INVALID, None

    return LoginStatus.SUCCESS, user_dict

  def delete_inventory_user(self, user_name: str):
    """
    Delete Inventory user
    """
    warning(f"[-] Delete user {user_name} ")
    sql = f"DELETE FROM {INVENTORY_USER_TABLE_NAME} WHERE user_name = ?"
    values = list([user_name])

    # Execute the DELETE statement
    self.exec_sql_cmd(sql, values)

  def add_inventory_user(
    self,
    user_name: str,
    user_password: str,
    user_privileges: UserPrivileges | int = UserPrivileges.GUEST,
  ) -> int:
    """
    Create a new row in INVENTORY_USER_TABLE_NAME. The password is hashed
    before being persisted.

    returns ID of the created user
    """
    privilege_value = (
      user_privileges.value
      if isinstance(user_privileges, UserPrivileges)
      else int(user_privileges)
    )

    warning(f"[+] Add user {user_name} with privileges {privilege_value}")

    user_dict = {
      "user_name": str(user_name),
      "user_password": _hash_password(user_password),
      "user_privileges": privilege_value,
    }

    sql, values = self._build_insert_query(INVENTORY_USER_TABLE_NAME, user_dict)
    self.exec_sql_cmd(sql, values)

    return self._get_last_inserted_id()

  def update_inventory_user_password(self, user_name: str, user_password: str):
    """
    Update password of an existing inventory user. The new password is
    hashed before being persisted.
    """
    sql, values = self._build_update_query(
      INVENTORY_USER_TABLE_NAME,
      {"user_password": _hash_password(user_password)},
      "user_name",
      user_name,
    )
    self.exec_sql_cmd(sql, values)

  def update_inventory_user_privileges(
    self, user_name: str, user_privileges: UserPrivileges | int
  ):
    """
    Update privileges of an existing inventory user
    """
    privilege_value = (
      user_privileges.value
      if isinstance(user_privileges, UserPrivileges)
      else int(user_privileges)
    )

    warning(f"[+] Update privileges for user {user_name} to {privilege_value}")

    sql, values = self._build_update_query(
      INVENTORY_USER_TABLE_NAME,
      {"user_privileges": privilege_value},
      "user_name",
      user_name,
    )
    self.exec_sql_cmd(sql, values)

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
