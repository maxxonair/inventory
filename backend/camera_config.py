"""
Camera server configuration file

"""
from pathlib import Path

# Determine absolute path of directory where this script is located
config_path = Path(__file__).parent.resolve()

# CameraServer IP
# Default: Run on localhost
camera_server_ip = "127.0.0.1"

# CameraServer port
# Default: 5050
camera_server_port = 5050


# Path to location where media files are stored 
media_file_path = (config_path / ".." / "database" / "media" ).resolve() 
