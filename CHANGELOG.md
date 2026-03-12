# changelog

all notable changes to this project will be documented in this file.
format based on [keep a changelog](https://keepachangelog.com/).

## [unreleased]

### added
- multi-agent orchestration support (`BaseMultiAgent`, `MultiAgentsService`) with state management and agent-to-agent transitions
- rc-lookup agent with tools for rule info lookup, cooloff period calculation, and log time-range fetching
- self-heal, bitbucket, funnel, and ba agents
- rag support via neo4j retriever and llama-index query engine tools
- audit logging for agent interactions
- foundry agent configuration files (`AGENTS.md`, `.foundry/casts/`)
- contributing, contributors, and security project governance files

### changed
- updated `.gitignore`
- bumped version to `v0.0.1-rc-lookup-1747383384-680a7fd`

### fixed
- agent and tool loading issues across multiple agents
