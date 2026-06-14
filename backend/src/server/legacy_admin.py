"""CLI admin service functions to


NOTE: THIS IS A LEGACY SCRIPT TO WORK WITH THE MYSQL DATABASE WHICH HAS BEEN
      REPLACED BY THE SQLITE DATABASE. IT IS KEPT HERE FOR LEGACY PURPOSES ONLY.

* create a new user
* delete a user
* modifify user privileges
* modify user passwords

Run with:
$ uv run -m server.legacy_admin

WARNING: This script requires direct access to the database server and should
         be exposed to system administrators only.

"""

from getpass import getpass
import logging
import sqlite3
from logging import error, info, warning
from pathlib import Path
import pandas as pd
from rich.prompt import Prompt
from tabulate import tabulate

from server.DataBaseClient import DataBaseClient
from server.InventoryUser import InventoryUser, UserPrivileges

# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = "inventory"

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_REGISTRY_TABLE_NAME = "registry"

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_STORAGE_LOCATIONS_TABLE_NAME = "storage_locations"

# [CONSTANT] Name of the table in INVENTORY_DB_NAME to store the inventory
#           item checkout history
INVENTORY_CHECKOUT_TABLE_NAME = "checkout_history"

# [!SENSITIVE!] Name of the table in INVENTORY_DB_NAME database to store the
#               Inventory users
INVENTORY_USER_TABLE_NAME = "users"

# [CONSTANT] Name of the table in INVENTORY_DB_NAME to store the inventory
#            log-in history
INVENTORY_LOGIN_TABLE_NAME = "login_history"

database_host = "127.0.0.1"
database_port = 3308

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
NEW_INVENTORY_REGISTRY_TABLE_NAME = "inventory"

# [!SENSITIVE!] Name of the table in INVENTORY_DB_NAME database to store the
#               Inventory users
NEW_INVENTORY_USER_TABLE_NAME = "inventory_user"

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
NEW_INVENTORY_STORAGE_LOCATIONS_TABLE_NAME = "storage_locations"

# [CONSTANT] Name of the table in INVENTORY_DB_NAME to store the inventory
#           item checkout history
NEW_INVENTORY_CHECKOUT_TABLE_NAME = "checkout_history"

# [CONSTANT] Name of the table in INVENTORY_DB_NAME to store the inventory
#            log-in history
NEW_INVENTORY_LOGIN_TABLE_NAME = "login_history"


def main():
  """Admin CLI functions to handle inventory users"""

  print("")
  warning("[DEPRECATION WARNING]")
  warning(
    "THIS IS A LEGACY SCRIPT TO WORK WITH THE MYSQL DATABASE WHICH HAS BEEN"
    " REPLACED BY THE SQLITE DATABASE. IT IS KEPT HERE FOR LEGACY PURPOSES ONLY."
  )
  print("")

  info(
    f"Trying to connect to inventory database at {database_host}:{database_port} ..."
  )
  client = DataBaseClient(host=database_host, port=database_port)

  info("Possible admin actions:\n")
  info("--- Admin Functions ---")
  info("1 - Create user")
  info("2 - Delete User")
  info("3 - Change user privileges")
  info("4 - Change user password\n")
  info("--- Log Functions ---")
  info("5 - List inventory")
  info("6 - List login history")
  info("7 - List checkout history")
  info("--- Export Functions ---")
  info("8 - Export MySQL database to SQLite database\n")
  answer = Prompt.ask(
    "Enter action to perform",
    choices=["1", "2", "3", "4", "5", "6", "7", "8"],
    default="1",
  )

  if answer == "1":
    create_user(client)
  elif answer == "2":
    delete_user(client)
  elif answer == "3":
    update_privileges(client)
  elif answer == "4":
    update_password(client)
  elif answer == "5":
    list_inventory(client)
  elif answer == "6":
    list_login_history(client)
  elif answer == "7":
    list_checkout_history(client)
  elif answer == "8":
    export_to_sqlite(client)


# ------------------------------------------------------------------------------
#                         ADMIN SERVICE FUNCTIONS
# ------------------------------------------------------------------------------


def create_user(client: DataBaseClient = None):
  """Create a new Inventory user via terminal prompts"""
  info("[Create user]")
  client.connect()
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

  # Create new user
  client.add_inventory_user(inventoryUser)
  client.close_connection()


def delete_user(client: DataBaseClient = None):
  """Delete Inventory user"""
  info("[Delete user]")
  valid = False
  client.connect()

  while not valid:
    username = input("Enter user name : ")
    # Remove whitespaces from user name
    username = username.strip(" ")

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
  client.close_connection()


def update_privileges(client: DataBaseClient = None):
  """Update existing inventory users privileges"""
  info("[Update user privileges]")
  valid = False
  privileges_invalid = True
  client.connect()

  while not valid:
    username = input("Enter user name : ")
    # Remove whitespaces from user name
    username = username.strip(" ")

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
  client.close_connection()


def update_password(client: DataBaseClient = None):
  """Update existing inventory users password"""
  info("[Update user password]")
  valid = False
  pw_invalid = True
  client.connect()

  while not valid:
    username = input("Enter user name : ")
    # Remove whitespaces from user name
    username = username.strip(" ")

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
  client.close_connection()

  info(f"Password for user {user_instance.user_name} updated!")


def list_inventory(client: DataBaseClient = None):
  client.connect()
  print(tabulate(client.get_all_inventory_as_df(), headers="keys", tablefmt="psql"))
  client.close_connection()


def list_login_history(client: DataBaseClient = None):
  client.connect()
  print(tabulate(client.get_login_log_as_df(), headers="keys", tablefmt="psql"))
  client.close_connection()


def list_checkout_history(client: DataBaseClient = None):
  client.connect()
  print(tabulate(client.get_checkout_log_as_df(), headers="keys", tablefmt="psql"))
  client.close_connection()


def export_to_sqlite(
  client: DataBaseClient = None, sqlite_db_path: str = "inventory.db"
):
  """Export MySQL database to SQLite database"""
  client.connect()
  if Path(sqlite_db_path).exists():
    info(f"SQLite database {sqlite_db_path} already exists. Overwriting ...")
    Path(sqlite_db_path).unlink()

  sqlite_conn = sqlite3.connect(sqlite_db_path)
  cursor = sqlite_conn.cursor()

  # Export inventory table
  export_table(
    client.cursor,
    sqlite_conn,
    INVENTORY_REGISTRY_TABLE_NAME,
    NEW_INVENTORY_REGISTRY_TABLE_NAME,
  )

  # Export storage locations table
  export_table(
    client.cursor,
    sqlite_conn,
    INVENTORY_STORAGE_LOCATIONS_TABLE_NAME,
    NEW_INVENTORY_STORAGE_LOCATIONS_TABLE_NAME,
  )

  # Export login table
  export_table(
    client.cursor,
    sqlite_conn,
    INVENTORY_LOGIN_TABLE_NAME,
    NEW_INVENTORY_LOGIN_TABLE_NAME,
  )

  # Export checkout table
  export_table(
    client.cursor,
    sqlite_conn,
    INVENTORY_CHECKOUT_TABLE_NAME,
    NEW_INVENTORY_CHECKOUT_TABLE_NAME,
  )

  sqlite_conn.commit()
  sqlite_conn.close()

  verify_sqlite_export(sqlite_db_path=sqlite_db_path)


def verify_sqlite_export(sqlite_db_path: str = "inventory.db") -> bool:
  """Verify that the SQLite database was created successfully"""
  if not Path(sqlite_db_path).exists():
    error(f"SQLite database {sqlite_db_path} does not exist. Export failed.")
    return False

  sqlite_conn = sqlite3.connect(sqlite_db_path)
  cursor = sqlite_conn.cursor()

  # Verify that the tables exist
  for table_name in [
    NEW_INVENTORY_REGISTRY_TABLE_NAME,
    NEW_INVENTORY_STORAGE_LOCATIONS_TABLE_NAME,
    NEW_INVENTORY_LOGIN_TABLE_NAME,
    NEW_INVENTORY_CHECKOUT_TABLE_NAME,
  ]:
    cursor.execute(
      f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    if not cursor.fetchone():
      error(f"Table {table_name} does not exist in SQLite database. Export failed.")
      sqlite_conn.close()
      return False

  cursor.execute(f"SELECT * FROM {NEW_INVENTORY_REGISTRY_TABLE_NAME}")
  sqlite_conn.commit()
  rows = cursor.fetchall()
  columns = [col[0] for col in cursor.description]
  registry_df = pd.DataFrame(rows, columns=columns)

  cursor.close()
  sqlite_conn.close()

  print("Item Registry DataFrame:")
  print(registry_df)

  info(f"SQLite database {sqlite_db_path} created successfully.")
  return True


def export_table(mysql_cursor, sqlite_conn, old_table_name, new_table_name):
  """Read all rows from MySQL and insert them into SQLite."""
  mysql_cursor.execute(f"SELECT * FROM {old_table_name}")
  rows = mysql_cursor.fetchall()

  # Get column names from MySQL cursor description
  column_names = [desc[0] for desc in mysql_cursor.description]

  # Create table in SQLite if it doesn't exist
  create_table_sql = (
    f"CREATE TABLE IF NOT EXISTS {new_table_name} ({', '.join(column_names)})"
  )
  sqlite_conn.execute(create_table_sql)

  # Insert rows into SQLite
  placeholders = ", ".join(["?"] * len(column_names))
  insert_sql = (
    f"INSERT INTO {new_table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
  )
  sqlite_conn.executemany(insert_sql, rows)


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
