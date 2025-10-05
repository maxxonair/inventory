# Start from MariaDB 10.5 base image
FROM mariadb:10.11

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
    python3-dev \
    supervisor \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.12 from source (since mariadb:10.5 is Debian-based with older Python)
RUN wget https://www.python.org/ftp/python/3.12.6/Python-3.12.6.tgz && \
    tar -xvf Python-3.12.6.tgz && \
    cd Python-3.12.6 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && rm -rf Python-3.12.6*

# Ensure python3 and pip point to 3.12
RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3

# Install supervisor for python 3.12
RUN pip3 install --no-cache-dir supervisor
    
# Add uv install to PATH 
ENV HOME=/root
ENV PATH="$HOME/.local/bin:${PATH}" 
    
# Install uv (ultrafast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

# Create backend subdirectory to copy python files to
RUN mkdir -p /app/server /app/media

# Copy in all relevant project files
COPY *.py server/
COPY pyproject.toml ./

# Sync uv environment before starting the server
RUN $HOME/.local/bin/uv sync --verbose

# Expose required ports used by the InventoryServer:
# Inventory server port:      5000
EXPOSE 5000

# Run both MariaDB and Python server under supervisord
COPY supervisord.conf /etc/supervisord.conf
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.conf"]