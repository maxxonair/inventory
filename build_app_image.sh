#!/bin/bash

# Script to build the inventory app podman image

set -e

ROOT_DIR=$pwd

#-------------------------------------------
#      BUILD INVENTORY APP IMAGE
#-------------------------------------------

cd app

# Install Dependencies 
bun install

# Build Application
# NOTE: This stepp needs the inventory server to be running
bun run build

podman build --no-cache -t inventoryapp:latest .

# ---- THE END ----

cd ${ROOT_DIR}

