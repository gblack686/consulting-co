# Multi-Agent Orchestrator Backend - Docker Container
# Runs FastAPI backend in Linux environment to fix Windows asyncpg DNS issues

FROM python:3.12-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (for layer caching)
COPY pyproject.toml .

# Install Python dependencies
RUN uv sync

# Copy the rest of the backend code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run backend server with asyncio loop (not uvloop) to fix Docker DNS issues
# uvloop + Docker + glibc 2.34 causes DNS resolution failures due to clone3() syscall
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]
