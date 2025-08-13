FROM oven/bun:1 AS base

WORKDIR /app

# Copy in all relevant project files
COPY *.json ./
COPY *.yaml ./
COPY *.js ./
COPY *.ts ./
COPY src ./

ENV NODE_ENV=production

EXPOSE 4173

RUN bun install

RUN bun run build

# USER bun
# ENTRYPOINT [ "bun", "run", "index.ts" ]

# Run preview for testing
ENTRYPOINT [ "bun", "run", "preview" ]