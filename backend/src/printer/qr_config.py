

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


