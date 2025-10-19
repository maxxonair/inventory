"""CLI admin service functions to

* create a new user
* delete a user
* modifify user privileges
* modify user passwords

Run with:
$ uv run -m server.admin

"""

from getpass import getpass
import logging
from logging import error, info
from rich.prompt import Prompt

from server.DataBaseClient import DataBaseClient
from server.InventoryUser import InventoryUser, UserPrivileges
from server.inventory_server_config import DEFAULT_DB_PORT

database_host = "127.0.0.1"
database_port = 3307


def main():
  """Admin CLI functions to handle inventory users"""
  info("Possible admin actions:")
  info("1 - Create user")
  info("2 - Delete User")
  info("3 - Change user privileges")
  info("4 - Change user password")
  answer = Prompt.ask(
    "Enter action to perform", choices=["1", "2", "3", "4"], default="1"
  )

  if answer == "1":
    create_user()
  elif answer == "2":
    delete_user()
  elif answer == "3":
    update_privileges()
  elif answer == "4":
    update_password()


# ------------------------------------------------------------------------------
#                         ADMIN SERVICE FUNCTIONS
# ------------------------------------------------------------------------------


def create_user():
  """Create a new Inventory user via terminal prompts"""
  info("[Create user]")
  pw_invalid = True
  privileges_invalid = True
  username = input("Enter user name :")
  # Remove whitespaces from user name
  username = username.strip(" ")

  while pw_invalid:
    pw1 = getpass("Enter user password:")
    pw2 = getpass("Repeat user password:")

    # Remove whitespaces from both inputs
    pw1 = pw1.strip(" ")
    pw2 = pw2.strip(" ")

    if not pw1 == pw2:
      error("Passwords don't match. Try again")
    else:
      pw_invalid = False

  while privileges_invalid:
    privileges = input(
      (
        "Enter user privileges Select: \n"
        "0 - For GUEST \n"
        "1 - For REPORTER \n"
        "2 - For DEVELOPPER \n"
        "3 - For MAINTAINER \n"
        "4 - For OWNER \n"
      )
    )

    privileges = int(privileges)

    if not (
      privileges >= UserPrivileges.GUEST.value
      and privileges <= UserPrivileges.OWNER.value
    ):
      error(
        (
          "Entered privilege level is not valid. Select: \n"
          "0 - For GUEST \n"
          "1 - For REPORTER \n"
          "2 - For DEVELOPPER \n"
          "3 - For MAINTAINER \n"
          "4 - For OWNER \n"
        )
      )
    else:
      privileges_invalid = False

  # Create user
  inventoryUser = InventoryUser(
    user_name=username, user_password=pw1, user_privileges=UserPrivileges(privileges)
  )

  client = DataBaseClient(host=database_host, port=database_port)

  # Create new user
  client.add_inventory_user(inventoryUser)


def delete_user():
  """Delete Inventory user"""
  info("[Delete user]")
  valid = False

  while not valid:
    username = input("Enter user name : ")
    # Remove whitespaces from user name
    username = username.strip(" ")

    client = DataBaseClient(host=database_host, port=database_port)
    valid, _ = client.get_inventory_user_as_object(username)

    if not valid:
      error("User not found. Try again.")

  valid = False

  while not valid:
    answer = input(f"Delete user {username} ? [yes/y] [n/no]\n")
    answer = str(answer).strip(" ").lower()
    if answer == "y" or answer == "yes":
      valid = True
    elif answer == "n" or answer == "no":
      info("Exit")
      exit(0)
    else:
      error("Confirmation invalid try again")

  # Delete user
  client.delete_inventory_user(username)


def update_privileges():
  """Update existing inventory users privileges"""
  info("[Update user privileges]")
  valid = False
  privileges_invalid = True

  while not valid:
    username = input("Enter user name : ")
    # Remove whitespaces from user name
    username = username.strip(" ")

    client = DataBaseClient(host=database_host, port=database_port)
    valid, user_instance = client.get_inventory_user_as_object(username)

    if not valid:
      error("User not found. Try again.")

  while privileges_invalid:
    privileges = input(
      (
        "Enter user privileges Select: \n"
        "0 - For GUEST \n"
        "1 - For REPORTER \n"
        "2 - For DEVELOPPER \n"
        "3 - For MAINTAINER \n"
        "4 - For OWNER \n"
      )
    )

    privileges = int(privileges)

    if not (
      privileges >= UserPrivileges.GUEST.value
      and privileges <= UserPrivileges.OWNER.value
    ):
      error(
        (
          "Entered privilege level is not valid. Select: \n"
          "0 - For GUEST \n"
          "1 - For REPORTER \n"
          "2 - For DEVELOPPER \n"
          "3 - For MAINTAINER \n"
          "4 - For OWNER \n"
        )
      )
    else:
      privileges_invalid = False

  # Modify privileges of existing user
  user_instance.user_privileges = privileges

  info(
    f"Setting user privileges for {user_instance.user_name} to {UserPrivileges(privileges).name}"
  )
  # Update user privileges in database
  client.update_inventory_user_privileges(user=user_instance)


def update_password():
  """Update existing inventory users password"""
  info("[Update user password]")
  valid = False
  pw_invalid = True

  while not valid:
    username = input("Enter user name : ")
    # Remove whitespaces from user name
    username = username.strip(" ")

    client = DataBaseClient(host=database_host, port=database_port)
    valid, user_instance = client.get_inventory_user_as_object(username)

    if not valid:
      error("User not found. Try again.")

  while pw_invalid:
    pw1 = getpass("Enter user password:")
    pw2 = getpass("Repeat user password:")

    # Remove whitespaces from both inputs
    pw1 = pw1.strip(" ")
    pw2 = pw2.strip(" ")

    if not pw1 == pw2:
      error("Passwords don't match. Try again")
    else:
      pw_invalid = False

  # Modify privileges of existing user
  user_instance.set_user_password(user_password=pw1)

  # Update user privileges in database
  client.update_inventory_user_password(user=user_instance)

  info(f"Password for user {user_instance.user_name} updated!")


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

if __name__ == "__main__":
  logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
  )
  main()
