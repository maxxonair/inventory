"""
Configuration file for all database parameters

"""

# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = 'inventory'

# [CONSTANT] Name of the main table in INVENTORY_DB_NAME to store the Inventory
INVENTORY_TABLE_NAME = 'inventory'

# Default database host
database_host = '127.0.0.1'

# Media directory folder. This will be set when creating the DataBaseClient
# instance!
media_directory = '../database/media'

# QR code identifier string
# All valid QR code messages for this inventory will start with this string
# followed by a delimiter
qr_iden_str = 'bigml2'

# Delimiter between qr_iden_str and qr_id_iden_str
qr_msg_delimiter = ';'

# Sub-string to identify the item it within a QR code message
qr_id_iden_str = 'id'
