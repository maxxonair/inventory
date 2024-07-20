from influxdb import InfluxDBClient
from logging import info, warning, debug
from InventoryItem import InventoryItem
from logging import info


class DataBaseClient():

  # [CONSTANT] Name of the main database to store the Inventory
  INVENTORY_DATABASE_NAME = 'inventory'

  def __init__(self, host: str, port: int = 8086):
    self.host = host
    self.port = port
    self.client = InfluxDBClient(port=port, host=host)

    # Check required databases exist
    if not self.is_db(self.INVENTORY_DATABASE_NAME):
      warning(
          f' Inventory database not found -> create database: {self.INVENTORY_DATABASE_NAME}')
      self.create_db(self.INVENTORY_DATABASE_NAME)
    else:
      debug('Inventory library found.')

    # Set to use the inventory database
    self.client.switch_database(self.INVENTORY_DATABASE_NAME)

  # ------------------------------------------------------------------------
  #                        [LIST & SEARCH]
  # ------------------------------------------------------------------------

  def list_db(self):
    """
    Return a list of all databases
    """
    return self.client.get_list_database()

  def is_db(self, data_base_name: str) -> bool:
    """
    Check if database of given name exists. If so return True, False 
    otherwise

    """
    db_list = self.list_db()
    for element in db_list:
      if element['name'] == str(data_base_name):
        return True
    return False

  def show_db_content(self):
    info(self.client.query(f"SELECT * from {self.INVENTORY_DATABASE_NAME}"))

  # ------------------------------------------------------------------------
  #                        [MODIFY]
  # ------------------------------------------------------------------------

  def create_db(self, data_base_name: str):
    """
    Create database
    """
    self.client.create_database(str(data_base_name))

  def add_inventory_item(self, inventory_item: InventoryItem):
    """
    Create column in INVENTORY_DATABASE_NAME 
    """
    self.client.write_points(inventory_item.get_item_dict())
