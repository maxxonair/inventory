#!/bin/bash

# Script to start up all required inventory containers

set -e

ROOT_DIR=$pwd

# Start all backend containers first
./start_containers.sh

#-------------------------------------------
#        START INVENTORY APP CONTAINER
#-------------------------------------------

cd app

echo "     [ COMPOSE INVENTORY APP CONTAINER]"
# Start inventory server container
podman-compose up -d inventory_app

#-------------------------------------------
#        START TRAEFIK CONTAINER
#-------------------------------------------
podman-compose up -d traefik

# display container status
echo "RUNNING CONTAINERS:"
podman ps
