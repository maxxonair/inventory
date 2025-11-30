FROM docker.io/node:20-bullseye-slim AS base

WORKDIR /app

# Install curl and bash
RUN apt-get update && apt-get install -y curl bash unzip && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.com/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Copy in project files
COPY static/ ./static/
COPY src/ ./src/
COPY *.json  *.ts svelte.config.js bun.lock .env ./

RUN bun install

RUN bun run build

ENV NODE_ENV=production

EXPOSE 3000
ENTRYPOINT ["/root/.bun/bin/bun", "build/index.js"]