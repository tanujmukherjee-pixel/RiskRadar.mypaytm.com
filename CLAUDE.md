<!-- foundry:instructions:start -->
# project instructions

see [AGENTS.md](../AGENTS.md) for the full cast directory and task workflow reference.

---

## core rules

- never hardcode secrets or commit `.env` files.
- match the existing code style -- read neighboring files before writing new code.
- run lint → test before submitting any pr.
- do not skip ahead of user instructions. wait for explicit approval before starting implementation.
- any `TODO` in a cast file: replace it if you can determine the value by inspecting the repo; otherwise leave it.

---

## language & stack

- **python 3.12**, fastapi + uvicorn (asgi)
- **llamaindex** for agent/rag orchestration -- follow its tool and query-engine patterns
- **pydantic v2** (`BaseModel`) for all request/response schemas and data validation

### naming conventions

- `snake_case` -- functions, methods, variables, module names
- `PascalCase` -- classes and pydantic models
- `UPPER_SNAKE_CASE` -- module-level constants in `src/constants/`

### code rules

- always annotate function signatures with type hints
- prefer `async def` for i/o-bound handlers; use `await` consistently
- use `logging.getLogger(__name__)` at module level -- never `print()`
- load env vars via `python-dotenv` at import time in `src/constants/`
- keep each module focused on a single concern (one agent per file, one tool category per file)
- add a short comment at the top of functions explaining their purpose

### architecture layers

`controllers/` → `services/` → `repositories/`, with `agents/`, `tools/`, `domains/`, `rags/`, `utils/`, `constants/` as supporting packages.

---

## testing

- all tests live in `tests/`
- when you add a feature, add tests in the same commit -- tests are not optional
- when you fix a bug, add a regression test that would have caught it
- mock all external dependencies -- tests must not require real external services
- the test suite must always pass; if you break a test, fix it immediately
- run `make test` to verify

---

## security

- no secrets in code -- use env vars or aws secrets manager
- no dynamic code execution from user input (no `eval` or equivalent)
- no query string concatenation -- use parameterized queries, prepared statements, or orm
- no wildcard imports in production code
- treat all untrusted input as hostile -- validate at the boundary, fail early
- tool-call payloads from llms are untrusted input

---

## environment

- required env vars are documented in `.foundry/casts/environment.md`
- if a required env var is missing, fail loudly -- no silent defaults
- never commit `.env`; create locally from the example table in the environment cast

---

## git & collaboration

- no force push (`--force`, `-f`, `--force-with-lease`)
- no direct push to `main` -- use a branch and open a pr
- branch naming: `feature/<desc>`, `bugs/<desc>`, `tests/<desc>`, `perf/<desc>`, `infra/<desc>`
- all feature branches start from `main`; rebase to stay current
- commit format: `<type>: <what changed>` (types: `feature`, `bug`, `tests`, `refactor`, `docs`, `perf`)
- one logical change per commit; keep first line under 72 characters
- pr description: what changed, why, and how to test it
<!-- foundry:instructions:end -->

<!-- foundry:start -->
please see docs/instructions.md for coding agent instructions

## foundry workflow

this project uses foundry for task management and workflow orchestration.

### task management
- `foundry task list` -- list all tasks
- `foundry task create "desc"` -- create a new task
- `foundry task plan <id>` -- create implementation plan
- `foundry task implement <id>` -- implement the plan
- `foundry task review <id>` -- verify + create PR
- `foundry task complete <id>` -- mark task done

### quality
- `foundry score` -- run maturity scoring

### release
- `foundry release` -- bump version, AI-generated changelog, tag, push
- `foundry release --bump minor` -- minor version bump
- `foundry release --model opus` -- use a specific model

### bitbucket
- `foundry bb pr create` -- create PR for current branch
- `foundry bb pr list` -- list open PRs
- `foundry bb auth status` -- check credentials

### integrations: bitbucket

## testing & linting

- run tests: `make test`
- lint: `make lint`
<!-- foundry:end -->
