# Generated by https://smithery.ai. See: https://smithery.ai/docs/config#dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy project metadata and lock file
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --upgrade pip \
    && pip install .

# Copy the rest of the source code
COPY . .

# Expose MCP port
EXPOSE 8000

# Start the MCP server
ENTRYPOINT ["python", "main.py"]
