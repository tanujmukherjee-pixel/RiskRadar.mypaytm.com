# vision

## purpose

Agency is an internal Paytm platform that provides an OpenAI-compatible REST API for configurable LLM agents built on the ReAct pattern (via LlamaIndex). Agents are backed by a PostgreSQL config store, receive tools for querying internal data systems (Starburst/Trino, Druid, MongoDB, Elasticsearch/Kibana, Neo4j, rule-admin APIs, Kubernetes, Bitbucket), and can be composed into multi-agent pipelines. The goal is to let product and engineering teams deploy new AI agents — for analytics, rule lookup, funnel analysis, infrastructure self-healing, and more — without rebuilding the agent scaffolding each time.

## principles

- api-first -- every agent is exposed through an OpenAI-compatible chat completions endpoint; clients interact the same way regardless of which agent is running
- configurable over hardcoded -- agents, tool lists, and prompts are loaded dynamically from the database, not baked into code
- composable agents -- individual ReAct agents are first-class units that can be chained into multi-agent pipelines via the state machine in `multi_agents/`
- observable by default -- structured logging is on at startup and optional Opik tracing callbacks are supported; if it runs, it should leave a trace
- fail gracefully -- every agent response path has explicit exception handling so a broken tool or LLM error returns a readable message rather than crashing the stream

## milestones

ordered list of major goals. each milestone should be a concrete deliverable, not a vague aspiration.

| # | milestone | status | description |
|---|-----------|--------|-------------|
| 1 | core agent framework | done | FastAPI app, BaseAgent/BaseMultiAgent, ReAct engine, tool registry, agent CRUD via PostgreSQL |
| 2 | analytics agents | done | BA agent (Starburst/Trino) and Funnel agent (Druid + MongoDB) for internal data querying |
| 3 | ops agents | done | Self-heal agent (Kubernetes node drain/cordon/clean) and Bitbucket agent |
| 4 | rc-lookup agent | in progress | Rule configuration lookup with cooloff period calculation and Kibana log integration |
| 5 | multi-agent orchestration | in progress | BaseMultiAgent state machine enabling sequential agent pipelines |
| 6 | RAG integration | in progress | Per-agent document retrieval via LlamaIndex + Neo4j; query engine exposed as an additional tool |
| 7 | hardened production readiness | not started | Full test coverage, linting/type-checking pipeline, secrets management, CORS lockdown |

### tech debt

identified during `foundry init`. these are structural improvements that don't add features but improve the codebase health. the setup agent populates this from repo analysis.

| # | item | severity | description |
|---|------|----------|-------------|
| 1 | hardcoded credentials in source | critical | `src/constants/database.py` has a plaintext PostgreSQL password as the default env fallback; must be removed |
| 2 | no test coverage | high | `tests/` contains only `__init__.py` — zero unit or integration tests across all agents, services, and tools |
| 3 | CORS wildcard in production | high | `allow_origins=["*"]` in `src/__init__.py` should be restricted to known internal origins |
| 4 | no linting or type-checking config | medium | No ruff/flake8/mypy/black configuration in `pyproject.toml`; code has no static analysis enforced |
| 5 | unpinned dependencies | medium | `elasticsearch`, `elasticsearch-dsl`, and `rank-bm25` are pinned to `"*"` — breaking changes will be silently picked up |
| 6 | thin README | medium | README only covers local setup; no API documentation, agent catalogue, tool list, or architecture overview |

severity: `critical`, `high`, `medium`, `low`

## non-goals

things this project explicitly does NOT do. helps agents avoid scope creep.

- we do not build or fine-tune LLMs -- we use OpenAI-compatible endpoints configured via environment variables
- we do not implement a custom auth system -- authentication delegates to Google service accounts and internal IAM roles
- we do not expose a user-facing UI -- this is a backend API platform; UI is someone else's responsibility
- we do not support general-purpose external deployments -- this is an internal Paytm service; multi-tenancy and public SaaS concerns are out of scope

## tech stack

| layer | technology |
|-------|-----------|
| language | Python 3.12 |
| framework | FastAPI + LlamaIndex (ReAct agent) |
| build tool | Poetry |
| test framework | none (pytest not yet configured) |
| ci/cd | Bitbucket Pipelines (builds and pushes Docker images to AWS ECR) |
| databases | PostgreSQL (agent config), Elasticsearch (audit logs), Neo4j (RAG graph), MongoDB, Druid, Starburst/Trino |
| infra integrations | AWS (boto3, ECR, IAM OIDC), Kubernetes python client, Google Auth |
| observability | Python logging, optional Opik (LlamaIndex callback) |
