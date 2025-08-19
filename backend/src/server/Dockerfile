FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y \
libmariadb-dev build-essential \
libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
libfreetype6-dev pkg-config python3-dev \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create backend subdirectory to copy python files to
RUN mkdir -p server
RUN mkdir -p media

# Copy in all relevant project files
COPY *.py server/
COPY pyproject.toml ./

# Sync uv environment before starting the server
RUN uv sync --verbose

# Expose required ports used by the InventoryServer:
# Inventory server port:      5000
# MariaDB port:               3306
# Camera server port:         5050
# Label printer server port:  5100
EXPOSE 5000

# Start the server
ENTRYPOINT [ "uv", "run", "-m", "server.InventoryServer" ]