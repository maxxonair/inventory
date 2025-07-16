from datetime import datetime
from pathlib import Path
from pandas import DataFrame
from logging import warning

from backend.database_config import INVENTORY_TABLE_NAME


class InventoryItem():

  def __init__(self,
               name: str,
               image: str = '',
               description: str = '',
               manufacturer: str = '',
               details: str = '',
               tags: str = '',
               location: str = 'Unknown',
               item_type: str = '',
               number_items: int = 1):
    """
    This function initializes the inventory item instance and makes sure that
    the dictorionary contains ALL properties of that item. When updating item
    properties ensure the MySQL query to create a table for that item is updated 
    as well

    """

    date_time_now = datetime.now()

    # Initialize class members
    self.name = name
    # image is a Path. Ensure it's always a Path and never to be set
    # as a string
    self.image = str(image)
    self.description = description
    self.manufacturer = manufacturer
    self.details = details
    self.is_checked_out = 0
    self.check_out_poc = ''
    self.check_out_date = ''
    self.tags = tags
    self.location = location
    self.item_type = item_type
    self.number_items = number_items

    self.date_added = date_time_now.strftime("%m/%d/%Y, %H:%M")

    self._update_dict()

  def get_item_dict(self) -> dict:
    self._update_dict()
    return self.inventoryItemDict

  def _update_dict(self):
    #  Create dictonary from item data
    self.inventoryItemDict = {
        "name": str(self.name),
        "image": str(self.image),
        "description": str(self.description),
        "manufacturer": str(self.manufacturer),
        "details": str(self.details),
        "is_checked_out": bool(self.is_checked_out),
        "check_out_date": str(self.check_out_date),
        "check_out_poc": str(self.check_out_poc),
        "date_added": str(self.date_added),
        "tags": str(self.tags),
        "location": str(self.location),
        "item_type": str(self.item_type),
        "number_items": int(self.number_items)
    }

  def get_item_property_classes(self) -> list:
    """
    Returns effectively a list of column names of that item in the inventory
    database.
    """
    self._update_dict()
    return list(self.inventoryItemDict.keys())

  def set_checked_out(self, poc: str) -> bool:
    """
    Function to mark this instance checked out from the time this function
    is called

    Args:
    poc - Point of contact. Person who checked out this item

    Returns
    (bool): Flag if True checkout status update is valid, False otherwise
    """
    if poc is None or poc == '':
      warning('No point of contact provided. Check out is invalid!')
      return False
    else:
      date_time_now = datetime.now()
      self.check_out_date = date_time_now.strftime("%m/%d/%Y, %H:%M:%S")
      self.check_out_poc = poc
      self.is_checked_out = True
      return True

  def set_checked_in(self, poc: str):
    """
    Function to mark this instance checked in from the time this function
    is called

    Args:
    poc - Point of contact. Person who checked in this item

    """
    self.check_out_date = ''
    self.check_out_poc = str(poc)
    self.is_checked_out = False

  def populate_from_df(self, item_data_df: DataFrame):
    """
    Function to populate item data from a dataframe object
    """
    if item_data_df.empty == False:
      self.name = item_data_df.iloc[0]['name']
      self.date_added = item_data_df.iloc[0]['date_added']
      self.manufacturer = item_data_df.iloc[0]['manufacturer']
      self.details = item_data_df.iloc[0]['details']
      self.is_checked_out = item_data_df.iloc[0]['is_checked_out']
      self.check_out_date = item_data_df.iloc[0]['check_out_date']
      self.check_out_poc = item_data_df.iloc[0]['check_out_poc']
      self.image = item_data_df.iloc[0]['image']
      self.description = item_data_df.iloc[0]['description']
      self.tags = item_data_df.iloc[0]['tags']
      self.location = item_data_df.iloc[0]['location']
      self.item_type = item_data_df.iloc[0]['item_type']
      self.number_items = item_data_df.iloc[0]['number_items']
    else:
      warning('Attempted to populate InventoryItem from empty DataFrame')

  def get_sql_query_table_for_item(self) -> str:
    """
    Create a sql query to create a table for this InventoryItem

    """

    # Compile query
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

    return create_table_query

  def get_sql_query_add_item(self):
    """
    Create a sql query to update an existing inventory item
    """
    # We use the InventoryItem class data in dictionary form here, so we
    # have to make sure the dictionary is up to date
    self._update_dict()

    # --- Construct the SQL INSERT statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
        [f"{column}" for column in list(self.inventoryItemDict.keys())])

    # Create series of ? that matches the number of values in
    # list(self.inventoryItemDict.values())
    value_clause = ", ".join(
        [f"?" for column in list(self.inventoryItemDict.values())])

    sql = f"INSERT INTO {INVENTORY_TABLE_NAME} ( {set_clause} ) VALUES ( {
        value_clause} )"

    # Prepare the data to update
    values = list(self.inventoryItemDict.values())

    return sql, values

  def get_sql_query_update_item(self, id: int):
    """
    Create a sql query to update an existing inventory item
    """
    # We use the InventoryItem class data in dictionary form here, so we
    # have to make sure the dictionary is up to date
    self._update_dict()

    # --- Construct the SQL UPDATE statement

    # Pre-construct set each value statement
    set_clause = ", ".join(
        [f"{column} = ?" for column in list(self.inventoryItemDict.keys())])

    sql = f"UPDATE {INVENTORY_TABLE_NAME} SET {set_clause} WHERE id = ?"

    # Prepare the data to update
    values = list(self.inventoryItemDict.values()) + [id]

    return sql, values
