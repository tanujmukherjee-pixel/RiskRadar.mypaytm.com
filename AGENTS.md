# agents.md

this is the operating contract for ai coding agents and human contributors. it is intentionally kept lean -- detailed guidance lives in the `.foundry/casts/` directory.

**do not read every cast file upfront.** read only the file(s) relevant to your current task. this keeps context small and focused.


## core rules (always apply)

- never hardcode secrets or commit `.env` files.
- match the existing code style -- read neighboring files before writing new code.
- run lint → test before submitting any pr.
- do not skip ahead of the user's instructions. wait for explicit approval before starting implementation.
- any field marked `TODO` in a cast file: if you can determine the correct value by inspecting the repo, replace it and commit the update. otherwise leave it.


## project files

these files track project context and workflow state. read them when relevant to your task.

| file | purpose | when to read |
|------|---------|-------------|
| [vision.md](.foundry/vision.md) | repo purpose, milestones, principles, non-goals | understanding what the project is trying to achieve |
| [tasks.json](.foundry/tasks.json) | task tracker with status, priority, description | planning work, checking task status, or picking up tasks |
| [state.json](.foundry/state.json) | session state, tool config, model settings | resuming work, checking workflow state, or configuring tools |


## cast directory

pick the file(s) that match what you're doing right now.

| cast | when to read |
|------|-------------|
| [code-style.md](.foundry/casts/code-style.md) | writing or reviewing code (naming, structure, language rules) |
| [collaboration.md](.foundry/casts/collaboration.md) | git conventions, branching, commits, or prs |
| [cross-platform.md](.foundry/casts/cross-platform.md) | writing shell scripts or dealing with macos/linux differences |
| [debugging.md](.foundry/casts/debugging.md) | investigating a bug or error |
| [decisions.md](.foundry/casts/decisions.md) | after making a major architectural or dependency decision |
| [documentation.md](.foundry/casts/documentation.md) | writing or updating docs |
| [environment.md](.foundry/casts/environment.md) | setting up env vars, secrets, or local dependencies |
| [logging.md](.foundry/casts/logging.md) | adding or modifying logging |
| [repo-map.md](.foundry/casts/repo-map.md) | first time in the repo, or need to find where things live |
| [security.md](.foundry/casts/security.md) | touching auth, user input, queries, or doing a security review |
| [testing.md](.foundry/casts/testing.md) | writing, updating, or reviewing tests |
| [workflow.md](.foundry/casts/workflow.md) | task lifecycle -- plan, implement, review, complete |


## task workflow

foundry uses a task lifecycle for structured development:

1. `foundry task create "description"` -- create a task
2. `foundry task plan <id>` -- scaffold + agentic plan (optionally `--git-flow` or `--worktree`)
3. `foundry task implement <id>` -- agentic implementation of the plan
4. `foundry task review <id>` -- agentic review / sanity check
5. `foundry task complete <id>` -- mark task done (requires merged PR on primary branch)

three dev modes:
- **default**: no git operations -- agent writes code, you handle git
- **git-flow** (`--git-flow`): auto branch, commit, push
- **worktree** (`--worktree`): isolated git worktree for the task


## meta

- **this file + the .foundry/casts directory** are the source of truth for agent behavior.
- agent-specific config files (CLAUDE.md, .cursorrules, etc.) can extend or override these.
- if you find a cast file outdated or contradicting the actual project, fix it in your pr.
