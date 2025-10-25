FROM docker.io/node:20-bullseye-slim AS base

WORKDIR /app

# Install curl and bash
RUN apt-get update && apt-get install -y curl bash unzip && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Copy static files
COPY static/ ./static/

# Copy in the built project files
# NOTE: The built is assumed to be done on the host machine outside of this 
# Dockerfile and prio to building the Docker image.
COPY build/ ./build/

ENV NODE_ENV=production

EXPOSE 3000
ENTRYPOINT ["/root/.bun/bin/bun", "run", "build/index.js"]