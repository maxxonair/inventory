# inventory

Minimal inventory management system to track physical assets. The assets are
identified by QR code, which are generated and recognized by inventory.

:construction: Work in Progress :construction:

# Project Setup

# Python setup

## Setup virtual python environment

Set up the virtual python environment and install all required dependencies
as follows:

```

# Go to the inventory root directory
cd inventory

# Create a folder called env
mkdir env

# Create a virtual enviroment
python -m venv env

# Install all required python dependencies
pip install -r requirements.txt

```

# Docker setup

This project uses docker to run the database that is holding the inventory.
To compose and run docker needs to be installed.

Start the database container as follows

```
cd inventory/database

docker compose up -d influxdb

```

To check the container status, run:

```

docker ps -a

```

Which should show the influxDb container up and running:

```
CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS                       PORTS                                       NAMES
a9066efdb6e7   influxdb:1.8   "/entrypoint.sh infl…"   25 hours ago   Up About an hour (healthy)   0.0.0.0:8086->8086/tcp, :::8086->8086/tcp   influxdb

```
