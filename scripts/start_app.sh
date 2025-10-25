#!/bin/bash

# Script to start up all required inventory containers

set -e

ROOT_DIR=$PWD

#-------------------------------------------
#        START INVENTORY CONTAINERS
#-------------------------------------------

cd ${ROOT_DIR}/backend

echo "     [ COMPOSE INVENTORY DATABASE CONTAINER ]"
# Start inventory database container
podman-compose up -d inventory_db


echo "     [ COMPOSE INVENTORY SERVER CONTAINER ]"
# Start inventory server container
podman-compose up -d inventory_server

#-------------------------------------------
#        START INVENTORY APP CONTAINER
#-------------------------------------------

cd ${ROOT_DIR}/app

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
