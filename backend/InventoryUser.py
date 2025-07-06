
import hashlib
from pandas import DataFrame
from logging import warning
from enum import Enum


# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = 'inventory'

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_TABLE_NAME = 'inventory'

# [CONSTANT] Name of the table in INVENTORY_DB_NAME database to store the
#            Inventory users
INVENTORY_USER_TABLE_NAME = 'inventory_user'


class UserPrivileges(Enum):
  GUEST = 0
  REPORTER = 1
  DEVELOPPER = 2
  MAINTAINER = 3
  OWNER = 4


class InventoryUser():

  # Salt for password hashing
  # TDOO to be changed and moved out of here
  SALT = 'sda8DF7d13e3F2'

  def __init__(self,
               user_name: str,
               user_password: str,
               user_privileges: UserPrivileges = UserPrivileges.GUEST):

    self.user_name = user_name
    self.hashed_user_password = self._hash(user_password)
    self.user_privileges = user_privileges.value

    self._update_dict()

  # ------------------------------------------------------------------------
  #                       [PUBLIC]
  # ------------------------------------------------------------------------
  def get_item_dict(self) -> dict:
    self._update_dict()
    return self.inventoryUserDict

  def set_user_password(self, user_password: str):
    self.hashed_user_password = self._hash(user_password)
    self._update_dict()

  def is_password(self, test_password: str):
    """
    Function to test if a given password matches the user passord of this 
    InventoryUser instance
    """
    hash_test_password = self._hash(test_password)
    return (hash_test_password == self.hashed_user_password)

  def populate_from_df(self, user_data_df: DataFrame):
    """
    Function to populate user data from a dataframe object
    """
    if user_data_df.empty == False:
      self.user_name = user_data_df.iloc[0]['user_name']
      self.hashed_user_password = user_data_df.iloc[0]['user_password']
      self.user_privileges = int(user_data_df.iloc[0]['user_privileges'])
    else:
      warning('Attempted to populate InventoryItem from empty DataFrame')
  # ------------------------------------------------------------------------
  #                       [PRIVATE]
  # ------------------------------------------------------------------------

  def _update_dict(self):
    #  Create dictonary from item data
    self.inventoryUserDict = {
        "user_name": str(self.user_name),
        "user_password": self.hashed_user_password,
        "user_privileges": self.user_privileges
    }

  def _hash(self, message: str):
    # Adding salt to the message
    message_salt = message + self.SALT
    # Encoding the password
    return str((hashlib.md5(message_salt.encode())).hexdigest())

  # ------------------------------------------------------------------------
  #                       [SQL QUERIES]
  # ------------------------------------------------------------------------

  def get_sql_query_table_for_user(self) -> str:
    """
    Create a sql query to create a table for this InventoryUser

    """

    # Compile query
    create_table_query = f'CREATE TABLE IF NOT EXISTS {
        INVENTORY_USER_TABLE_NAME} ( id INT PRIMARY KEY AUTO_INCREMENT,'
    create_table_query += f'user_name VARCHAR(50) UNIQUE NOT NULL,'
    create_table_query += f'user_password VARCHAR(50),'
    create_table_query += f'user_privileges INT )'

    return create_table_query

  def get_sql_query_add_user(self):
    """
    Create a sql query to add this self to the user table
    """
    # We use the InventoryUser class data in dictionary form here, so we
    # have to make sure the dictionary is up to date
    self._update_dict()

    # --- Construct the SQL INSERT statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
        [f"{column}" for column in list(self.inventoryUserDict.keys())])

    # Create series of ? that matches the number of values in
    # list(self.inventoryUserDict.values())
    value_clause = ", ".join(
        [f"?" for column in list(self.inventoryUserDict.values())])

    sql = f"INSERT INTO {INVENTORY_USER_TABLE_NAME} ( {set_clause} ) VALUES ( {
        value_clause} )"

    # Prepare the data to update
    values = list(self.inventoryUserDict.values())

    return sql, values

  def get_sql_query_update_user(self, user_name: str):
    """
    Create a sql query to update an existing inventory user
    """
    # We use the InventoryUser class data in dictionary form here, so we
    # have to make sure the dictionary is up to date
    self._update_dict()

    # --- Construct the SQL UPDATE statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
        [f"{column} = ?" for column in list(self.inventoryUserDict.keys())])

    sql = f"UPDATE {INVENTORY_USER_TABLE_NAME} SET {
        set_clause} WHERE user_name = ?"

    # Prepare the data to update
    values = list(self.inventoryUserDict.values()) + [user_name]

    return sql, values
