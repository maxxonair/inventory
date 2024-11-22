# inventory

Minimal inventory management system to track physical assets in a digital database. The assets are identified by QR code, which are generated and recognized by inventory. When creating a new item inventory tries to interface automatically with a Niimbot printer to print the corresponding QR label sticker. The QR label is read using a webcam interface.

:construction: Work in Progress :construction:

![inventory](https://github.com/maxxonair/inventory/tree/main/frontend/data/inventory_example_ui_home.png?raw=true)

# Configuration

## Configure Database

:construction: Work in Progress :construction:

## Configure Camera Server

:construction: Work in Progress :construction:

## Configure Printer Interface

:construction: Work in Progress :construction:

## Configure User Interface

:construction: Work in Progress :construction:

# Run with Docker

## Run the Database Server with Docker

Required dependencies to run the database

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

## Run the UI Server with Docker

:construction: Work in Progress :construction:

Build the main application docker container with the following command:

```
cd inventory/

sudo docker build --tag "inventory" .

```

Run the container with:

```

sudo docker run --detach 'inventory'

```

Run the following for debbuging, to keep attached to the running container:

```

sudo docker run 'inventory'

```

## Useful Docker Commands

To check the container status, run:

```

docker ps -a

```

Which should show the influxDb container up and running:

```
CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS                       PORTS                                       NAMES
a9066efdb6e7   mariadb:2.1   "/entrypoint.sh infl…"   25 hours ago   Up About an hour (healthy)   0.0.0.0:3306->3306/tcp, :::8086->8086/tcp   inventory

```

# Install and Run Modules Manually

## Install required packages

Required packages

```
sudo apt-get install zbar-tools libmariadb3 libmariadb-dev
```

## Run the Database Server with Docker

The database server currently needs to be run with Docker. See the Docker install & run section on how to run the database server.

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

## Run Application Manually

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

# Handy Commands

## UV commands

Compile platform independent requirements file from pip requirements.txt
file with uv:

```
uv pip compile requirements.txt --universal --output-file requirements.txt
```

## User Management

Adding, removing or modifying users is currently only possible in the terminal
using helper functions. Make sure the database container is running, when
running the following commands.

Use the following commands to add, delete users, or list all existing database
users. To modify user permissions it is currently required to first delete
the user entirely and then create it again with the altered permissions.

```
python util.create_user.py # Alternatively with uv $ uv run util.create_user.py
```

```
python util.delete_user.py # Alternatively with uv $ uv run util.delete_user.py
```

```
python util.show_users.py # Alternatively with uv $ uv run util.show_users.py
```

# Troubleshooting

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
