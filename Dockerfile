# Stage 1: Build dependencies
FROM python:3.12.9-bullseye

WORKDIR /agency

COPY . .

# Create a non-root user and give it permissions
RUN useradd -ms /bin/bash appuser && \
    chown -R appuser /agency

# Switch to the new user
USER appuser

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Switch back to root to set permissions for /.cache
USER root

# Ensure root has full permissions
RUN mkdir -p /.cache && \
    chmod -R 777 /.cache    

EXPOSE 5000

# Set environment variables for timeout
ENV UVICORN_TIMEOUT_KEEP_ALIVE=300

CMD python3 -m uvicorn src:app --host 0.0.0.0 --port 5000 --timeout-keep-alive $UVICORN_TIMEOUT_KEEP_ALIVE