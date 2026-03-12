# documentation contract

documentation must cover:
- how to install, run, test, and troubleshoot
- if needed, how to deploy on a prod server (including how to get and configure secrets)
- architecture overview: major components and how data/requests flow
- interfaces: public apis, events, cli usage, configuration keys

## rules

- write for a new engineer or agent joining cold.
- prefer diagrams (mermaid) and short sections over long prose.
- keep docs in sync with code changes.
- date all documents. stale docs are worse than no docs.
- architecture docs live in `docs/architecture/`. 
- decision records go in `docs/decisions/` 
