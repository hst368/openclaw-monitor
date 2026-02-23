FROM python:3.11-slim

LABEL maintainer="OpenClaw Monitor Contributors"
LABEL description="Web dashboard for monitoring OpenClaw AI agents"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MONITOR_USERNAME=admin
ENV MONITOR_PASSWORD=changeme

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directory for OpenClaw data
RUN mkdir -p /root/.openclaw-monitor

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run the application
CMD ["python3", "app.py"]
