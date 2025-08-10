"""
Configuration file for all database parameters

"""
from pathlib import Path

# Determine absolute path of directory where this script is located
config_path = Path(__file__).parent.resolve()

# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = 'inventory'

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_TABLE_NAME = 'inventory'

# [!SENSITIVE!] Name of the table in INVENTORY_DB_NAME database to store the
#               Inventory users
INVENTORY_USER_TABLE_NAME = 'inventory_user'

# [!SENSITIVE!] Name of the table in INVENTORY_DB_NAME database to store the
#               Inventory users
DATABASE_USER_NAME = 'inventory_user'

# [!SENSITIVE!] Name of the table in INVENTORY_DB_NAME database to store the
#               Inventory users
DATABASE_PASSWORD = 'inventory24'

# Database IP address
# Default: localhost
database_host = '127.0.0.1'

database_port = 46123

# -------------------------------------------------------------------------
#                             [QR]
# -------------------------------------------------------------------------

# Media directory folder. This will be set when creating the DataBaseClient
# instance!
media_directory = (config_path / ".." / "database" / "media").resolve()
