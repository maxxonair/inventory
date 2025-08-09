"""

Service function to delete an existing Inventory user

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
  valid = False

  while not valid:
    username = input("Enter user name : ")
    # Remove whitespaces from user name
    username = username.strip(' ')

    client = DataBaseClient(host=database_host)
    valid, inventoryUser = client.get_inventory_user_as_object(username)

    if not valid:
      error('User not found. Try again.')

  valid = False

  while not valid:
    answer = input(f"Delete user {username} ? [yes/y] [n/no]\n")
    answer = str(answer).strip(' ').lower()
    if answer == 'y' or answer == 'yes':
      valid = True
    elif answer == 'n' or answer == 'no':
      info('Exit')
      exit(0)
    else:
      error('Confirmation invalid try again')

  # Delete user
  client.delete_inventory_user(username)


if __name__ == '__main__':
  logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                      datefmt='%H:%M:%S',
                      level=logging.INFO)
  main()
