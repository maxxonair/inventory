from datetime import datetime
from pathlib import Path
from pandas import DataFrame
from logging import warning

from backend.database_config import INVENTORY_TABLE_NAME, INVENTORY_DB_NAME


class InventoryItem():

  def __init__(self,
               item_name: str,
               item_image_path: Path = None,
               item_description: str = None,
               manufacturer: str = None,
               manufacturer_contact: str = None,
               is_checked_out: bool = False,
               check_out_poc: str = None,
               check_out_date: datetime = None,
               item_tags: str = None):
    """
    This function initializes the inventory item instance and makes sure that
    the dictorionary contains ALL properties of that item. When updating item
    properties ensure the MySQL query to create a table for that item is updated 
    as well

    """
    if check_out_date is None:
      check_out_date_str = ''
    else:
      check_out_date_str = check_out_date.strftime("%m/%d/%Y, %H:%M:%S")

    if item_image_path is None:
      item_image_path_str = ''
    else:
      item_image_path_str = item_image_path.absolute().as_posix()

    date_time_now = datetime.now()

    # Initialize class members
    self.item_name = item_name
    # item_image is a Path. Ensure it's always a Path and never to be set
    # as a string
    self.item_image = Path(item_image_path_str)
    self.item_description = item_description
    self.manufacturer = manufacturer
    self.manufacturer_contact = manufacturer_contact
    self.is_checked_out = is_checked_out
    self.check_out_poc = check_out_poc
    self.check_out_date = check_out_date_str
    self.item_tags = item_tags

    self.date_added = date_time_now.strftime("%m/%d/%Y, %H:%M:%S")

    self._update_dict()

  def get_item_dict(self) -> dict:
    return self.inventoryItemDict

  def _update_dict(self):
    #  Create dictonary from item data
    self.inventoryItemDict = {
        "item_name": str(self.item_name),
        "item_image": Path(self.item_image).absolute().as_posix(),
        "item_description": str(self.item_description),
        "manufacturer": str(self.manufacturer),
        "manufacturer_contact": str(self.manufacturer_contact),
        "is_checked_out": bool(self.is_checked_out),
        "check_out_date": str(self.check_out_date),
        "check_out_poc": str(self.check_out_poc),
        "date_added": str(self.date_added),
        "item_tags": str(self.item_tags),
    }

  def set_img_path(self, img_path: Path):
    self.item_image = Path(img_path).absolute().as_posix()
    self._update_dict

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
    valid - Flag if True checkout status update is valid 
    """
    valid = False
    if poc is None or poc == '':
      warning('No point of contact provided. Check out is invalid!')
    else:
      date_time_now = datetime.now()
      self.check_out_date = date_time_now.strftime("%m/%d/%Y, %H:%M:%S")
      self.check_out_poc = poc
      self.is_checked_out = True
      valid = True

    return valid

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
      self.item_name = item_data_df.iloc[0]['item_name']
      self.date_added = item_data_df.iloc[0]['date_added']
      self.manufacturer = item_data_df.iloc[0]['manufacturer']
      self.manufacturer_contact = item_data_df.iloc[0]['manufacturer_contact']
      self.is_checked_out = item_data_df.iloc[0]['is_checked_out']
      self.check_out_date = item_data_df.iloc[0]['check_out_date']
      self.check_out_poc = item_data_df.iloc[0]['check_out_poc']
      try:
        self.item_image = Path(item_data_df.iloc[0]['item_image'])
      except:
        self.item_image = Path('')
      self.item_description = item_data_df.iloc[0]['item_description']
      self.item_tags = item_data_df.iloc[0]['item_tags']
    else:
      warning('Attempted to populate InventoryItem from empty DataFrame')

  def get_sql_query_table_for_item(self) -> str:
    """
    Create a sql query to create a table for this InventoryItem

    """

    # Compile query
    create_table_query = f'CREATE TABLE IF NOT EXISTS {
        INVENTORY_TABLE_NAME} ( id INT PRIMARY KEY AUTO_INCREMENT,'
    create_table_query += f'item_name VARCHAR(255) NOT NULL,'
    create_table_query += f'item_image VARCHAR(1055),'
    create_table_query += f'item_description VARCHAR(1055) ,'
    create_table_query += f'manufacturer VARCHAR(255),'
    create_table_query += f'manufacturer_contact VARCHAR(1055),'
    create_table_query += f'is_checked_out BOOLEAN,'
    create_table_query += f'check_out_date VARCHAR(255) ,'
    create_table_query += f'check_out_poc VARCHAR(1055) ,'
    create_table_query += f'date_added VARCHAR(255) )'
    create_table_query += f'item_tags VARCHAR(1055) )'

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
