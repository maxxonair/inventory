#!/bin/bash

# Function to clean up background processes on Ctrl+C
cleanup() {
  echo "Terminating servers ..."
  kill -TERM -$PGID1
  kill -TERM -$PGID2
  exit 0
}

# Trap Ctrl+C (SIGINT) and call cleanup
trap cleanup SIGINT

# Launch Inventory Server in a new process group
uv run -m backend.InventoryServer &
PID1=$!
PGID1=$(ps -o pgid= $PID1 | grep -o '[0-9]*')

# Launch Camera Server in a new process group
uv run -m backend.CameraServer &
PID2=$!
PGID2=$(ps -o pgid= $PID2 | grep -o '[0-9]*')

# Wait for both processes
wait $PID1 $PID2