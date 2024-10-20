"""
Configuration file for all database parameters

"""

# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = 'inventory'

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the
#            Inventory
INVENTORY_TABLE_NAME = 'inventory'

# [CONSTANT] Name of the table in INVENTORY_DB_NAME database to store the
#            Inventory users
INVENTORY_USER_TABLE_NAME = 'inventory_user'

# Default database host IP address
database_host = '127.0.0.1'

# -------------------------------------------------------------------------
#                             [QR]
# -------------------------------------------------------------------------

# Media directory folder. This will be set when creating the DataBaseClient
# instance!
media_directory = '../database/media'
