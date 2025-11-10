#!/bin/bash

# Compose all inventory containers
podman-compose up -d inventory_db
podman-compose up -d inventory_server
podman-compose up -d inventory_app

# Compose Traefik container for reverse proxy
podman-compose up -d traefik