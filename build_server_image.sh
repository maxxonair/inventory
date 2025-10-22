#!/bin/bash

# Script to build the inventory server podman image

set -e

ROOT_DIR=$pwd

#-------------------------------------------
#      BUILD INVENTORY SERVER CONTAINER
#-------------------------------------------

cd backend/src/server

podman build --no-cache -t inventoryserver:latest .

# ---- THE END ----

cd ${ROOT_DIR}

