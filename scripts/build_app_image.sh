#!/bin/bash

# Script to build the inventory app podman image

set -e

ROOT_DIR=$PWD

#---------------------------------------------
# BUILD INVENTORY WEB APP ON THE HOST MACHINE 
#---------------------------------------------

cd ${ROOT_DIR}/app

# Install Dependencies 
bun install

# Build Application
bun run build

#---------------------------------------------
#      BUILD INVENTORY APP IMAGE
#---------------------------------------------

podman build --no-cache -t inventoryapp:latest .

# ---- THE END ----

cd ${ROOT_DIR}

