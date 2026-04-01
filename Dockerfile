FROM python:3.11

# Install Node.js (>=18) and required tools
# Note: the default nodejs in Debian bookworm (python:3.11 base) is Node 18,
# which satisfies the frontend requirement.
RUN apt-get update \
  && apt-get install -y --no-install-recommends nodejs npm \
  && rm -rf /var/lib/apt/lists/*

# Copy uv from its official image
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /app

# Copy dependency manifests first to maximise layer cache reuse
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package-lock.json ./frontend/
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Install Node + Python dependencies
RUN npm ci \
  && npm ci --prefix frontend \
  && cd backend && uv sync

# Copy project source
COPY . .

EXPOSE 3000 5001

# Start frontend (dev server) and backend concurrently.
# For local-first use this is the standard mode; for production consider
# building the frontend separately and serving via nginx.
CMD ["npm", "run", "dev"]
