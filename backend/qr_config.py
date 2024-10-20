
from logging import warning
# -------------------------------------------------------------------------
#                             [QR]
# -------------------------------------------------------------------------
# QR code identifier string
# All valid QR code messages for this inventory will start with this string
# followed by a delimiter
qr_iden_str = 'bigml2'

# Delimiter between qr_iden_str and qr_id_iden_str
qr_msg_delimiter = ';'

# Sub-string to identify the item it within a QR code message
qr_id_iden_str = 'id'

# -------------------------------------------------------------------------
#                             [QR]
# -------------------------------------------------------------------------


def encode_id_to_qr_message(id: int) -> str:
  """
  Encode item id to QR message string


  Message format:
  <qr_iden_str> <qr_msg_delimiter> <qr_id_iden_str> <qr_msg_delimiter> <ITEM_ID>

  """
  return f'{qr_iden_str}{qr_msg_delimiter}{qr_id_iden_str}{qr_msg_delimiter}{id}'


def decode_id_from_qr_message(msg: str):
  """
  Decode QR message and retrieve item ID

  Expected message format:
  <qr_iden_str> <qr_msg_delimiter> <qr_id_iden_str> <qr_msg_delimiter> <ITEM_ID>

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
