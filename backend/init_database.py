"""Script to initialise the inventory database

This script creates if non-existent:
  -> The inventory database
  -> The inventory database table
  -> The inventory user database table
"""

from logging import info, warning
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.DataBaseClient import DataBaseClient
from src.database_config import (
    INVENTORY_TABLE_NAME,
    INVENTORY_DB_NAME,
    INVENTORY_USER_TABLE_NAME,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')


db = DataBaseClient()

info("Initialising inventory database:")

# -- Ensure that database exists --
if not db.is_database(INVENTORY_DB_NAME):
    warning(f" {INVENTORY_DB_NAME} database not found.")
    db.create_database(INVENTORY_DB_NAME)
    info(f"[x] Created database: {INVENTORY_DB_NAME}")
else:
    info(f"[x] {INVENTORY_DB_NAME} does already exist.")

# Use inventory database from here onwards
db.cursor.execute(f"USE {INVENTORY_DB_NAME}")

# -- Ensure that inventory table exists --
if not db.is_table(INVENTORY_TABLE_NAME):
    warning(f" {INVENTORY_TABLE_NAME} table not found.")
    db.create_inventory_table()
    info(f"|-> Created table: {INVENTORY_TABLE_NAME}")
else:
    info(f"[x] {INVENTORY_TABLE_NAME} does already exist.")

# -- Ensure that inventory user table exists --
if not db.is_table(INVENTORY_USER_TABLE_NAME):
    warning(f" {INVENTORY_USER_TABLE_NAME} table not found.")
    db.create_inventory_user_table()
    info(f"|-> Created table: {INVENTORY_USER_TABLE_NAME}")
else:
    info(f"[x] {INVENTORY_USER_TABLE_NAME} does already exist.")
