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
from backend.InventoryUser import InventoryUser, UserPrivileges

# --- Config imports
from backend.database_config import database_host


def main():
  """
  Create a new Inventory user via terminal prompts

  """
  pw_invalid = True
  privileges_invalid = True
  username = input("Enter user name :")
  # Remove whitespaces from user name
  username = username.strip(' ')

  while pw_invalid:
    pw1 = getpass("Enter user password:")
    pw2 = getpass("Repeat user password:")

    # Remove whitespaces from both inputs
    pw1 = pw1.strip(' ')
    pw2 = pw2.strip(' ')

    if not pw1 == pw2:
      error("Passwords don't match. Try again")
    else:
      pw_invalid = False

  while privileges_invalid:
    privileges = input(('Enter user privileges Select: \n'
                        '0 - For GUEST \n'
                        '1 - For REPORTER \n'
                        '2 - For DEVELOPPER \n'
                        '3 - For MAINTAINER \n'
                        '4 - For OWNER \n'))

    privileges = int(privileges)

    if not (privileges >= UserPrivileges.GUEST.value
            and privileges <= UserPrivileges.OWNER.value):
      error(('Entered privilege level is not valid. Select: \n'
             '0 - For GUEST \n'
             '1 - For REPORTER \n'
             '2 - For DEVELOPPER \n'
             '3 - For MAINTAINER \n'
             '4 - For OWNER \n'))
    else:
      privileges_invalid = False

  # Create user
  inventoryUser = InventoryUser(user_name=username,
                                user_password=pw1,
                                user_privileges=UserPrivileges(privileges))

  client = DataBaseClient(host=database_host)

  # Create new user
  client.add_inventory_user(inventoryUser)


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)
  main()
