# Code Style

## Formatter

- code should be readable with comments at the top of the function for easy understanding and building knowledge base about the repo.

## Language

**Primary Language(s):** Python 3.12

**Framework/Runtime:** FastAPI + Uvicorn (ASGI)

**Language-Specific Guidelines:**

- Use `snake_case` for functions, methods, variables, and module names.
- Use `PascalCase` for classes (including Pydantic models).
- Use `UPPER_SNAKE_CASE` for module-level constants (see `src/constants/`).
- Always annotate function signatures with type hints (use `typing` and `pydantic` types).
- Use Pydantic v2 (`BaseModel`) for request/response schemas and data validation.
- Prefer `async def` for I/O-bound handlers and service methods; use `await` consistently.
- Use `logging.getLogger(__name__)` at module level — never use `print()` for diagnostic output.
- Load environment variables via `python-dotenv` (`load_dotenv()`) at module import time in `src/constants/`.
- Never hardcode secrets or connection strings in source files; read them from `os.environ`.
- Organize code by layer: `controllers/` → `services/` → `repositories/`, with `agents/`, `tools/`, `domains/`, `rags/`, `utils/`, and `constants/` as supporting packages.
- LlamaIndex is the primary agent/RAG orchestration framework; follow its tool and query-engine patterns when extending agents.
- Keep each module focused on a single concern (one agent per file, one tool category per file, etc.).

## Separation of Concerns

Each class/module has one job. Do not mix concerns.


