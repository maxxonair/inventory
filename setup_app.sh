#!/bin/bash

ROOT_DIR=$pwd

#-------------------------------------------
#                BACKEND
#-------------------------------------------

# ---- BUILD INVENTORY SERVER CONTAINER ----
cd backend/src/server

docker build --no-cache -t inventoryserver:latest .

# ---- START CONTAINERS ----

cd ../../

# Start inventory database container
docker compose up -d inventory_db
# Start inventory server container
docker compose up -d inventory_server


#-------------------------------------------
#                FRONTEND
#-------------------------------------------

cd ${ROOT_DIR}/app

docker build --no-cache -t inventoryweb:latest .

# TODO

# display container status
docker ps
