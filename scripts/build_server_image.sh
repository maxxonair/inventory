#!/bin/bash

# Script to build the inventory server podman image

set -e

ROOT_DIR=$PWD

#-------------------------------------------
#      BUILD INVENTORY SERVER CONTAINER
#-------------------------------------------

cd ${ROOT_DIR}/backend/src/server

podman build --no-cache -t inventoryserver:latest .

# ---- THE END ----

cd ${ROOT_DIR}

