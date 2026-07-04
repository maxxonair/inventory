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
# Debug path (when running servica manually here)
# MEDIA_DEFAULT_PATH = (config_path / ".." / ".." / "inventory_db" /  "media").resolve()
