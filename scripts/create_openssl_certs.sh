#!/bin/bash

# Create directory for certificates if it doesn't exist

openssl req -x509 -nodes -days 365 \
  -newkey rsa:4096 \
  -keyout traefik/certs/devmachine.key \
  -out traefik/certs/devmachine.crt \
  -subj "/CN=devmachine.lan/O=DevMachine/L=City/C=US"
