"""
This file contains utility functions used by the main application.

"""
from logging import warning
from backend.database_config import (qr_iden_str,
                                     qr_id_iden_str,
                                     qr_msg_delimiter)

# --------------------------------------------------------------------------
#                         QR code handling
# --------------------------------------------------------------------------


def parse_qr_message(msg: str):
  """
  Test function to get the decoded QR message from the camera server
  print it to the terminal
  """
  is_msg_valid = False
  item_id = -1

  # First check if all substring identifier are contained in the message
  if qr_iden_str in msg and qr_id_iden_str in msg and qr_msg_delimiter in msg:
    try:
      # Remove all identifier strings and convert to integer
      # Step 1: Split the test_str using the delimiter
      parts = msg.split(qr_msg_delimiter)

      # Step 2: Remove qr_iden_str and qr_id_iden_str, extract the numerical part
      remaining_str = parts[1].replace(qr_id_iden_str, '')

      # Step 3: Convert the remaining part to an integer
      item_id = int(remaining_str)
      is_msg_valid = True
    except:
      warning('Parsing QR code message failed. ')

  return is_msg_valid, item_id
