# inventory

Minimal inventory management system to track physical assets. The assets are
identified by QR code, which are generated and recognized by inventory.

:construction: Work in Progress :construction:

# Project Setup

Required packages

```
sudo apt-get install zbar-tools
```

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

Required database dependencies

```
sudo apt install libmariadb3 libmariadb-dev
```

This project uses docker to run the database that is holding the inventory.
To compose and run docker needs to be installed.

Start the database container as follows

```
cd inventory/database

docker compose up -d inventory

```

To check the container status, run:

```

docker ps -a

```

Which should show the influxDb container up and running:

```
CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS                       PORTS                                       NAMES
a9066efdb6e7   mariadb:2.1   "/entrypoint.sh infl…"   25 hours ago   Up About an hour (healthy)   0.0.0.0:3306->3306/tcp, :::8086->8086/tcp   inventory

```

### Troubleshooting

The MariaDB docker container will use port 3306 which might conflict with
running mysql services on the target machine, leading to the following error
when starting up the container:

```
Error response from daemon: driver failed programming external connectivity on endpoint inventory (307f628849c076718517dcaf96313d1df854eca239ef314272932975cd6f2396): Error starting userland proxy: listen tcp4 0.0.0.0:3306: bind: address already in use
```

In that case list services that use this port and shut them down

List services that use port 3306:

```
sudo lsof -i -P -n | grep 3306
```

Shut down mysql service on the target machine.

```
sudo service mysql stop
```

To prevent this issue from coming back when the host machine is restarded,
disable the mysql service with:

```
sudo systemctl disable mysql

```

# Run Application

This is assuming the previous setup has been completed and the database
container is up and running.

Start the application with:

```
python app.py
```

This command includes starting up and handling the following elements: 
- the database client
- the camera server
- the UI server

Note that running the application requires having the database server already running.
