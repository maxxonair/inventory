#!/bin/bash

ROOT_DIR=$pwd

#-------------------------------------------
#                BACKEND
#-------------------------------------------

# ---- BUILD INVENTORY SERVER CONTAINER ----
cd backend/src/server

podman build --no-cache -t inventoryserver:latest .

# ---- START CONTAINERS ----

cd ../../

# TODO: Add check if inventory_server image exists in local repository before 
# composing the container

# # Start inventory server container
podman-compose up -d inventory_server


#-------------------------------------------
#                FRONTEND
#-------------------------------------------

# cd ${ROOT_DIR}/app

# Work in progress 
# docker build --no-cache -t inventoryweb:latest .

# TODO

# display container status
podman ps
