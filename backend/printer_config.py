"""
Printer parameter file

"""
import sys
from pathlib import Path

# Mac address of the Niimbot D110 printer used to print inventory labels
niimbot_d110_inventory_mac_address = '04:08:04:01:31:04'

# Directory where label images will be saved
print_label_image_file_directory = Path(
    sys.path[0]) / 'backend' / 'images_to_print'

# File name of the test image label
test_image_file_name = 'B21_30x15mm_240x120px.png'

# Set print density.
# Note: The Niimbot D110 only supports maximum density of 3
print_density = 3

# If enabled: Create a time stamped png file for each label print command
# sent
enable_save_label_print_cmds_to_file = True

# Define maximum number of reconnection attempts to the printer before giving
# up
num_reconnection_attempts = 3

# Maximum label width and height in pixel
printer_max_image_height_px = 120
printer_max_image_width_px = 240
