# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Playwright browsers path
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright

# Install Playwright browsers with explicit path and verification
RUN playwright install chromium
RUN playwright install-deps chromium
RUN playwright --version

# Verify browser installation
RUN ls -la /app/.cache/ms-playwright/ || echo "Browser cache directory not found"
RUN find /app/.cache/ms-playwright -name "chrome*" -type f 2>/dev/null || echo "Chrome executable not found"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.cache/ms-playwright

# Create a startup script to ensure browsers are accessible
RUN echo '#!/bin/bash\n\
echo "Checking Playwright browsers..."\n\
ls -la /app/.cache/ms-playwright/\n\
echo "Starting application..."\n\
exec python server.py' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/summary || exit 1

# Run the application
CMD ["/app/start.sh"]
