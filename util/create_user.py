"""

Service function to create an Inventory user

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
  pw_invalid = True
  privileges_invalid = True
  username = input("Enter user name :")

  while pw_invalid:
    pw1 = getpass("Enter user password:")
    pw2 = getpass("Repeat user password:")
    if not pw1 == pw2:
      error("Passwords don't match. Try again")
    else:
      pw_invalid = False

  while privileges_invalid:
    privileges = input("Enter user privileges [1-3]:")

    privileges = int(privileges)

    if not (privileges > 0 and privileges < 4):
      error('Entered privilege level is not valid. Select 1, 2 or 3')
    else:
      privileges_invalid = False

  # Create user
  inventoryUser = InventoryUser(user_name=username,
                                user_password=pw1,
                                user_privileges=privileges)

  client = DataBaseClient(host=database_host)

  # Create new user
  client.add_inventory_user(inventoryUser)


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)
  main()
