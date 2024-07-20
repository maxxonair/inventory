from datetime import datetime

from backend.database_config import INVENTORY_TABLE_NAME, INVENTORY_DB_NAME


class InventoryItem():

  def __init__(self,
               item_name: str,
               item_description: str = None,
               manufacturer: str = None,
               manufacturer_contact: str = None,
               is_checked_out: bool = None,
               check_out_poc: str = None,
               check_out_date: datetime = None):
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

    date_time_now = datetime.now()

    #  Create dictonary from item data
    self.inventoryItemDict = {
        "item_name": item_name,
        "item_description": item_description,
        "manufacturer": manufacturer,
        "manufacturer_contact": manufacturer_contact,
        "is_checked_out": is_checked_out,
        "check_out_date": check_out_date_str,
        "check_out_poc": check_out_poc,
        "date_added": date_time_now.strftime("%m/%d/%Y, %H:%M:%S"),
    }

  def get_item_dict(self) -> dict:
    return self.inventoryItemDict

  def get_item_property_classes(self) -> list:
    """
    Returns effectively a list of column names of that item in the inventory
    database.
    """
    return list(self.inventoryItemDict.keys())

  def get_mysql_table_query(self):
    """
    Create a mysql query to create a table for this InventoryItem

    """

    # Compile query
    create_table_query = f'CREATE TABLE IF NOT EXISTS {
        INVENTORY_TABLE_NAME} ( id INT PRIMARY KEY AUTO_INCREMENT,'
    create_table_query += f'item_name VARCHAR(255) NOT NULL,'
    create_table_query += f'item_description VARCHAR(1055) ,'
    create_table_query += f'manufacturer VARCHAR(255),'
    create_table_query += f'manufacturer_contact VARCHAR(1055),'
    create_table_query += f'is_checked_out BOOLEAN,'
    create_table_query += f'check_out_date VARCHAR(255) ,'
    create_table_query += f'check_out_poc VARCHAR(1055) ,'
    create_table_query += f'date_added VARCHAR(255) )'

    return create_table_query
