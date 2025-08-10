"""
Camera server configuration file

"""
# CameraServer IP
# Default: Run on localhost
camera_server_ip = "0.0.0.0"

# CameraServer port
# Default: 5050
camera_server_port = 5050


# IP address of the inventory server
# Default: inventory_server (container)
DEFAULT_INVENTORY_HOST = 'inventory_server'

# Port of the inventory server
# Default: 5000 (mapped container port)
DEFAULT_INVENTORY_PORT = 5000
