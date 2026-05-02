"""
Configuration file for all database parameters

"""

from pathlib import Path
from enum import Enum

# Determine absolute path of directory where this script is located
config_path = Path(__file__).parent.resolve()

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


# [ENUM] defining thw two possible checkout types: borrow and return
class CheckoutType(Enum):
  BORROW = 1
  RETURN = 2


# [ENUM] defining the possible login statuses
class LoginStatus(Enum):
  SUCCESS = 1
  USER_NOT_FOUND = 2
  PASSWORD_INVALID = 3
