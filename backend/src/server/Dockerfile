FROM docker.io/maxxonair/inventoryserverbase:latest

WORKDIR /app

# Assume that the base image has already installed all necessary dependencies as 
# well as set up the /app and /app/media directories.

# Copy in all relevant project files
COPY *.py server/
COPY pyproject.toml ./

# Sync uv environment before starting the server
RUN uv sync --verbose

ENTRYPOINT ["uv", "run", "-m", "server.InventoryServer"]