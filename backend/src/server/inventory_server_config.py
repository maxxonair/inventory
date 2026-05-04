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
inventory_server_port = 5001


# --- CONSTANTS ---

# Path to where media files are saved
MEDIA_DEFAULT_PATH = (config_path / ".." / "media").resolve()


# IP address of the database server
# Default: inventory_db (container)
DEFAULT_DB_HOST = "inventory_db"
DEFAULT_DB_HOST = "localhost"  # --- IGNORE ---


# Port of the database server
# Default: 3306 (mapped container port)
# Note: This is not necessarily the port on the host machine. The host port
#       might be mapped to a different value in the docker-compose.yml file.
DEFAULT_DB_PORT = 3307


# [CONSTANT] Name of the main database to store the Inventor
INVENTORY_DB_NAME = "inventory"
