#!/bin/bash

ROOT_DIR=$pwd

# ---- BUILD INVENTORY SERVER CONTAINER ----
cd backend/src/server

docker build -t inventoryserver:latest .

# ---- START CONTAINERS ----

cd ../../

# Start inventory database container
docker compose up -d inventory_db
# Start inventory server container
docker compose up -d inventory_server

# display container status
docker ps
