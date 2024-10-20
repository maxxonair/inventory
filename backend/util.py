"""

Utility functions used on the backend side 

"""
# QR code reader
from pyzbar.pyzbar import decode
import cv2 as cv
import numpy as np

from logging import warning
from .qr_config import (qr_iden_str,
                        qr_id_iden_str,
                        qr_msg_delimiter,
                        decode_id_from_qr_message)

# ------------------------------------------------------------------------
#                 [IMAGE PROCESSING FUNCTIONS]
# ------------------------------------------------------------------------
# TODO move parameter to a sensible place
enableQrText = False


def detect_and_decode_qr_marker(frame):
  """
  Detect and decode one or several QR code messages within a given image.

  This functions uses pyzbar for detection and decoding


  """
  # ---------------------------------------------------------------------
  # ----- Use Pyzbar
  # Initialize flag to track if a marker has been found
  qr_marker_found = False
  # Initialize counter to track the number of markers detected in the image
  num_markers = 0
  # Initialize a list to store all decoded messages
  decoded_list = []

  for d in decode(frame):
    qr_marker_found = True
    num_markers += 1
    decoded_text = str(d.data.decode())
    decoded_list.append(decoded_text)

    # Draw perimeter of the marker
    frame = cv.polylines(frame, [np.array(d.polygon)], True, (0, 255, 0), 2)
    # Draw marker text
    if enableQrText:
      frame = cv.putText(frame, decoded_text, (d.rect.left, d.rect.top + d.rect.height),
                         cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv.LINE_AA)

  return frame, qr_marker_found, num_markers, decoded_list
