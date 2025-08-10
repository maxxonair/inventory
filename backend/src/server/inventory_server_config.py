"""

Inventory server configuration file

"""
from pathlib import Path

# Determine absolute path of directory where this script is located
config_path = Path(__file__).parent.resolve()

# --- SETTINGS ---

# InventoryServer IP
# Default: Localhost
inventory_server_ip = "0.0.0.0"

# InventorySever port
# Default: 5000
inventory_server_port = 5000

# ---- PRINTER SERVER CONFIG ----

# Printer Server host IP
# Default: Localhost
PRINTER_SERVER_IP = "127.0.0.1"

# Printer Server port
# Default: 5100
PRINTER_SERVER_PORT = 5100

# --- CONSTANTS ---

# Path to where media files are saved
MEDIA_DEFAULT_PATH = (config_path / ".." / "database" / "media" ).resolve() 

# IP address of the database server
# Default: localhost
DEFAULT_DB_HOST = 'inventory_db'

# TODO parameterise DB port here!

# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = 'inventory'
