# Stage 1: Build dependencies
FROM python:3.12.7-slim-bullseye

WORKDIR /agency

COPY . .

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Ensure root has full permissions
RUN mkdir -p /.cache && \
    chmod -R 777 /.cache    

EXPOSE 5000

# Set environment variables for timeout
ENV UVICORN_TIMEOUT_KEEP_ALIVE=120


CMD ["python3", "-m", "uvicorn", "src:app", "--host", "0.0.0.0", "--port", "5000", "--timeout-keep-alive", "$UVICORN_TIMEOUT_KEEP_ALIVE"]