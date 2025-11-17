#!/bin/bash

set -e

# Compose Traefik container for reverse proxy
podman-compose up -d traefik