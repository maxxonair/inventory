"""

Inventory server configuration file

"""
from pathlib import Path

# Determine absolute path of directory where this script is located
config_path = Path(__file__).parent.resolve()

# --- SETTINGS ---

# InventoryServer IP
# Default: 0.0.0.0 (expose service outside the container)
inventory_server_ip = "0.0.0.0"

# InventorySever port
# Default: 5000
inventory_server_port = 5000

# ---- PRINTER SERVER CONFIG ----

# Printer Server host IP
# Default: inventory_printer (container)
PRINTER_SERVER_IP = "inventory_printer"

# Printer Server port
# Default: 5100
PRINTER_SERVER_PORT = 5100

# --- CONSTANTS ---

# Path to where media files are saved
MEDIA_DEFAULT_PATH = (config_path / ".." / "media" ).resolve() 

# IP address of the database server
# Default: inventory_db (container)
DEFAULT_DB_HOST = 'inventory_db'

# Port of the database server
# Default: 3306 (mapped container port)
DEFAULT_DB_PORT = 3306

# [CONSTANT] Name of the main database to store the Inventory
INVENTORY_DB_NAME = 'inventory'
