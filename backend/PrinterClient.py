"""

Client to interface with the Niimbot label printer

"""
from PIL import Image, ImageOps
from logging import info, error
from pathlib import Path
from datetime import datetime
import qrcode

# Niimbot printer interface
from .niimbot_printer import BluetoothTransport, NiimbotClient, SerialTransport

# ---- Config imports ----
from .printer_config import (niimbot_d110_inventory_mac_address,
                             print_label_image_file_directory,
                             test_image_file_name,
                             print_density,
                             enable_save_label_print_cmds_to_file,
                             num_reconnection_attempts,
                             printer_max_image_height_px,
                             printer_max_image_width_px)
from .qr_config import encode_id_to_qr_message


class PrinterClient():
  """
  * Handle setting up the respective label printer interface
  * Handle load images from file
  * Handle print from file
  * Handle print form PIL Image
  """
  # ------------------------------------------------------------------------
  #                     INIT
  # ----------------------------------------------------------------------

  def __init__(self):
    # Link printer density from config
    self.density = print_density
    self.image = None

  # ------------------------------------------------------------------------
  #                     PUBLIC METHODS
  # ----------------------------------------------------------------------

  def print_test_image(self):
    """
    Call print a test image

    Test image file at backend/images_to_print/B21_30x15mm_240x120px.png 
    required!

    """
    if self._establish_printer_connection():
      test_image_path = print_label_image_file_directory / test_image_file_name
      self._load_image(test_image_path)
      info(f'Print test label: {test_image_path.name}')
      self.printer.print_image(self.image, density=self.density)

  def print_image(self, image_name: str):
    """
    Call print a image from file 

    image needs to be saved first as a file in backend/images_to_print/


    """
    if self._establish_printer_connection():
      # Compile image path
      image_path = print_label_image_file_directory / image_name

      # load the image from file
      self._load_image(image_path)

      info(f'Print label: {image_name}')
      self.printer.print_image(self.image, density=self.density)

  def print_qr_label_from_id(self, item_id: int):
    """
    Call print a image from file 

    image needs to be saved first as a file in backend/images_to_print/


    """
    print_success = False
    if self._establish_printer_connection():
      qr_message = encode_id_to_qr_message(item_id)

      info(f'Print label for item ID {item_id} - QR message: {qr_message}')
      self.image = qrcode.make(qr_message)

      # Add white bar to the top of the bar code to ensure having it centered
      # on the actual label
      self._add_white_bar_to_qr_image()

      # Reseize the generated QR code to fit the label
      # self.image = self.image.resize(
      #     (printer_max_image_height_px, printer_max_image_height_px))
      self.image.thumbnail((printer_max_image_width_px,
                           printer_max_image_height_px), Image.Resampling.LANCZOS)

      # Save label to png
      if enable_save_label_print_cmds_to_file:
        now = datetime.now()
        date_time = now.strftime("%Y_%m_%d__%H_%M_%S")
        info(f'Save label to file: {date_time}_label.png')
        self.image.save(
            (print_label_image_file_directory / f'{date_time}_label.png').absolute().as_posix())

      # Send print command
      self.printer.print_image(self.image, density=self.density)
      print_success = True
    return print_success

  # ------------------------------------------------------------------------
  #                     PRIVATE METHODS
  # ------------------------------------------------------------------------
  def _load_image(self, image_path: Path):
    """
    Load image from file
    """
    # -- Load image
    self.image = Image.open(image_path)
    # Rotate image by 90 degree (to match sticker orientation)
    self.image = self.image.rotate(-int(90), expand=True)

  def _establish_printer_connection(self) -> bool:
    """
    Establish connection with the printer

    @returns: True if connection successful, false otherwise
    """
    for attempt in range(num_reconnection_attempts):
      info(f'Connecting to Niimbot D110 label printer. attempth {attempt}')
      try:
        # -- Init bluetooth connection
        self.transport = BluetoothTransport(niimbot_d110_inventory_mac_address)
        self.printer = NiimbotClient(self.transport)
        return True
      except:
        pass
    error('Connecting to the printer failed!')
    return False

  def _add_white_bar_to_qr_image(self):
    """
    Add a white bar to the QR code image to have it centered on the label    
    """
    if self.image is not None:
      img = self.image
      (w, h) = img.size
      layer = ImageOps.expand(img, border=w, fill='white')
      # Crop the extended image left top right bottom
      self.image = layer.crop(
          (w, round(0.7 * h), 2 * w, 2 * h))
