#!/bin/bash

# Script to build the inventory server podman image

set -e

ROOT_DIR=$PWD

#-------------------------------------------
#      BUILD INVENTORY SERVER BASE IMAGE
#-------------------------------------------

cd ${ROOT_DIR}/backend/src/server/server_base_image

podman build --no-cache -t inventoryserverbase:latest .

# ---- THE END ----

cd ${ROOT_DIR}

