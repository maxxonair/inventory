FROM ghcr.io/astral-sh/uv:bookworm-slim

# Install dependencies for Python build
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    libmariadb-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create backend subdirectory to copy python files to
RUN mkdir -p /app/server /app/media

COPY pyproject.toml ./

# Sync uv environment before starting the server
RUN uv sync --verbose