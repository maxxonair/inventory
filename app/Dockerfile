FROM docker.io/node:20-bullseye-slim AS base


WORKDIR /app

# Install curl and bash
RUN apt-get update && apt-get install -y curl bash unzip && rm -rf /var/lib/apt/lists/*


# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Copy project metadata and dependencies
COPY *.json ./
COPY *.yaml ./
COPY bun.lockb* bun.lock* ./

# Copy source files
COPY src/ ./src/
COPY static/ ./static/
COPY .env ./
COPY *.js ./
COPY *.ts ./

COPY build/ ./build/
COPY .svelte-kit/ ./.svelte-kit/

ENV NODE_ENV=production
ENV PUBLIC_INVENTORY_SERVER_URL="http://inventory-server:5000"

# Install all dependencies including dev (needed for TS Vite config)
RUN bun install

# Ensure TypeScript knows how to resolve SvelteKit modules
RUN npx tsc --skipLibCheck --noEmit

EXPOSE 3000
ENTRYPOINT ["/root/.bun/bin/bun", "run", "build/index.js"]
# Debug option 
CMD ["/bin/bash"]