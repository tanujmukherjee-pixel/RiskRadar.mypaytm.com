# security contract

## hard rules (never violate)

- **no secrets in code**: no api keys, passwords, tokens, or connection strings in source files. use env vars or aws secrets manager or a dedicated config file in which all the secrets are kept. This config file should never be checked in to the repo.
- **no dynamic code execution from user input**: no language-level eval or equivalent that executes arbitrary user-supplied strings. graalvm polyglot scripts must not accept untrusted input directly.
- **no query string concatenation**: always use parameterized queries, prepared statements, or an orm.
- **no wildcard imports in production code**: be explicit about what you import.
- **no disabled security headers**: csp, cors, hsts, x-frame-options must be configured where applicable.
- **no overly permissive types**: avoid disabling the type system. exceptions require a justification comment.
- **do not disable security checks to ship faster.**

## secure coding expectations

- treat all untrusted input as hostile by default. tool-call payloads from llms are untrusted input.
- validate inputs at the boundary and fail early. 
- use safe query apis (parameterized queries, orm safe paths).
