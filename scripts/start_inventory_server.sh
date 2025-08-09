#!/bin/bash

# Define server working directory 
WORKDIR="/home/mrx/Documents/inventory"

cd $WORKDIR

# Remove all active session cookies when the server is restarted
rm ./flask_session/*

# Start the server
uv run -m backend.InventoryServer