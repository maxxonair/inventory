#!/bin/bash

PRJCT_DIR=$PWD

cd ${PRJCT_DIR}/backend/src

# Start the server
OPENCV_AVFOUNDATION_SKIP_AUTH=1 DYLD_LIBRARY_PATH=$(brew --prefix zbar)/lib:$DYLD_LIBRARY_PATH uv run -m camera.CameraServer