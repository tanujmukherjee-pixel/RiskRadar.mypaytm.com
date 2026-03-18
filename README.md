# agency

A FastAPI-based chat completion API service that provides endpoints similar to OpenAI's API structure.

## Prerequisites

- Python 3.12 (3.13 not supported due to torch compatibility)
- Homebrew (for macOS users)
- Poetry (Python package manager)

## Installation

```bash
# Install required system dependencies
brew install poetry
brew install uvicorn

# Set up Python environment
poetry env use python3.12
poetry install 
```

## Running the Server

```bash
poetry run uvicorn src:app --reload
```

The server will start at `http://localhost:8000` by default.

## API Endpoints

### List Available Models
```http
GET /v1/models
```

Returns a list of available models.

### Get Model Information
```http
GET /v1/models/{model_id}
```

Returns information about a specific model.

### Create Text Completion
```http
POST /v1/completions
```

Request body:
```json
{
    "prompt": "Your text prompt here",
    "max_tokens": 100,
    "temperature": 0.7
}
```

### Create Chat Completion
```http
POST /v1/chat/completions
```

Request body:
```json
{
    "model": "model_id",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello!"
        }
    ],
    "stream": false
}
```

Set `stream: true` for server-sent events (streaming responses).

### Delete Model
```http
DELETE /v1/models/{model_id}
```

Deletes a specific model from the system.

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`