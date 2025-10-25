#!/bin/bash

# Script to compose and start all inventory containers

set -e

ROOT_DIR=$pwd

#-------------------------------------------
#        START INVENTORY CONTAINERS
#-------------------------------------------

cd backend

echo "     [ COMPOSE INVENTORY DATABASE CONTAINER ]"
# Start inventory database container
podman-compose up -d inventory_db


echo "     [ COMPOSE INVENTORY SERVER CONTAINER ]"
# Start inventory server container
podman-compose up -d inventory_server

