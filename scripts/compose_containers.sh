#!/bin/bash

# Compose all inventory containers
podman-compose up -d inventory_server
podman-compose up -d inventory_app