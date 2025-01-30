# Stage 1: Build dependencies
FROM python:3.12.7-slim-bullseye

WORKDIR /agency

COPY . .

# Install Poetry
RUN pip install --no-cache-dir poetry

# Use Poetry to install dependencies
RUN poetry install --no-root

# Ensure root has full permissions
RUN mkdir -p /.cache && \
    chmod -R 777 /.cache    

EXPOSE 5000

CMD ["poetry", "run", "uvicorn", "src:app", "--reload"]

