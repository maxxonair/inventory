#!/bin/bash

# Define server working directory 
WORKDIR="/home/mrx/Documents/inventory"

cd $WORKDIR

# Start the server
uv run -m backend.CameraServer