# agency

## Setup

```bash
brew install poetry
brew install uvicorn
poetry env use python3.12 # (3.13 doesn't work unable to download torch)
poetry install
```

## Running Options

### 1. Chat Interface (Recommended)

Run the interactive chat interface:
```bash
poetry run python -m src.__main__
```

### 2. API Server

Run the FastAPI server:
```bash
poetry run uvicorn src:app --reload
```

## Dependencies

- Python 3.12
- Poetry for dependency management
- Ollama for local LLM support
- FastAPI for API server
- Pydantic for data validation

## Chat Interface Commands

- Just type your message to chat with the agent
- `help` - Show all available commands
- `clear` - Clear conversation history
- `history` - Show conversation history
- `models` - List available models
- `use <model_id>` - Switch to a different model
- `exit` - Exit the chat interface