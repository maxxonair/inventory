"""

Service function to display all Inventory users

"""
from getpass import getpass
import logging
from logging import info, error
import os
import sys

# Get the parent directory and add it to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from backend.DataBaseClient import DataBaseClient
from backend.InventoryUser import InventoryUser

# --- Config imports
from backend.database_config import database_host


def main():

  client = DataBaseClient(host=database_host)
  user_df = client.get_inventory_users_as_df()

  info(' > Inventory Users <')
  print(user_df)


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)
  main()
