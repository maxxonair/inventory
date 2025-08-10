#!/bin/bash

ROOT_DIR=$pwd

# ---- BUILD INVENTORY CAMERA CONTAINER ----
cd backend/src/camera

docker build -t inventorycamera:latest .

cd ../printer

docker build -t inventoryprinter:latest .

# ---- START CONTAINERS ----

cd ../../

# Start inventory camera server container
docker compose up -d inventory_camera
# Start inventory printer server container
docker compose up -d inventory_printer

# display container status
docker ps
