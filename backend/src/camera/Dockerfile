FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    alsa-utils \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create backend subdirectory to copy python files to
RUN mkdir -p camera

# Copy in all relevant project files
COPY *.py camera/
COPY pyproject.toml ./
COPY assets/*.wav ./

# Sync uv environment before starting the server
RUN uv sync --verbose

# Expose required ports used by the InventoryServer:
# Inventory server port:      5000
# MariaDB port:               3306
# Camera server port:         5050
# Label printer server port:  5100
EXPOSE 5050 

# Start the server
ENTRYPOINT [ "uv", "run", "-m", "camera.CameraServer" ]