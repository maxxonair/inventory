FROM oven/bun:1 AS base

WORKDIR /app

# Copy in all relevant project files
COPY *.json ./
COPY *.yaml ./
COPY *.js ./
COPY *.ts ./
COPY src ./
COPY .svelte-kit ./



ENV NODE_ENV=production
# Run tests when implemented
# RUN bun test

EXPOSE 5173 5000 5050

RUN bun install
# RUN bun run build
# USER bun
# EXPOSE 5173/tcp
# ENTRYPOINT [ "bun", "run", "index.ts" ]

ENTRYPOINT [ "bun", "run", "dev" ]