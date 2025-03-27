FROM python:3.12-slim-bullseye as builder

WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY requirements.txt .

# Install build dependencies, then install Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Second stage: runtime
FROM python:3.12-slim-bullseye

WORKDIR /agency

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Create cache directory with proper permissions
    mkdir -p /.cache && \
    chmod -R 777 /.cache

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -ms /bin/bash appuser && \
    chown -R appuser:appuser /agency

# Switch to non-root user
USER appuser

EXPOSE 5000

# Set environment variables for timeout
ENV UVICORN_TIMEOUT_KEEP_ALIVE=300

# Using shell form to properly expand environment variables
CMD python3 -m uvicorn src:app --host 0.0.0.0 --port 5000 --timeout-keep-alive $UVICORN_TIMEOUT_KEEP_ALIVE