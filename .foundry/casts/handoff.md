# Handoff Process

When the user says "handoff" (or "hand off", "hand this off", etc.), create a context file so a future session can resume the work seamlessly.

## Steps

1. **Create the file** at `.foundry/handoffs/YYYY-MM-DD-<slug>.md` where `<slug>` is a 2-4 word kebab-case summary (e.g., `2026-02-12-circuit-breaker-setup.md`).

2. **Write these sections**:

```markdown
# Handoff: <short title>

**Date**: YYYY-MM-DD
**Branch**: <current git branch>
**Status**: <in-progress | blocked | investigating>
**Task ID**: <task id from .foundry/tasks.json, if applicable>
**Plan**: <path to plan file in .foundry/tasks/<id>/PLAN.md, if applicable>

## Problem / Goal
<What the user is trying to accomplish or fix. Be specific.>

## Context
<Why this matters, any background the next session needs.>

## What Was Done
<Bullet list of concrete actions taken -- files changed, tests added, things tried.>

## Current State
<Where things stand right now. What's working, what's broken.>

## What's Left / Next Steps
<Numbered list of remaining work, in priority order.>

## Key Files
<Bullet list of file paths most relevant to this task.>

## Gotchas / Notes
<Anything surprising discovered, dead ends, or important constraints.>
```

3. **Commit only the handoff file**:
```bash
git add .foundry/handoffs/<filename>.md
git commit -m "Add handoff: <short title>"
```

## Rules

- **Be thorough**: The next session starts cold -- include everything needed to resume without re-investigating.
- **Be concrete**: Reference exact file paths, line numbers, error messages, and test names.
- **Include failed attempts**: Knowing what didn't work saves the next session from repeating it.
- **One file per handoff**: Don't update old handoff files. Each handoff is a snapshot in time.
- **Commit only the handoff file**: Don't stage or commit any other changes.
- **Don't push**: Only commit locally. The user decides when to push.
- **Never force push**: See hard rules in collaboration.md.

## Per-task handoffs (orchestration)

When a task is delegated through the workflow (via the assign stage or orchestrator), the handoff lives in the task directory instead of `.foundry/handoffs/`:

```
.foundry/tasks/<task-id>/HANDOFF.md
```

Subagents receiving a task handoff should also check for:
- `.foundry/tasks/<task-id>/PLAN.md` -- if a plan already exists (e.g. from pull-tasks)
- `.foundry/casts/workflow.md` "subagent responsibilities" section -- for execution rules

After completing work, the subagent writes:
- `.foundry/tasks/<task-id>/SUMMARY.md` -- what was done, deviations, blockers

## Resuming

When the user says "resume handoff" or similar:
1. check `.foundry/tasks/` for any `HANDOFF.md` files in task directories (orchestration handoffs)
2. check `.foundry/handoffs/` for the most recent file on the current branch (manual handoffs)
3. use the most recent handoff as context

Do not check for or load handoffs unless the user explicitly asks.
