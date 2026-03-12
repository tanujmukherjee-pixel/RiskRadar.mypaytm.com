# Collaboration Guidelines

- Multiple branches of this repo might be worked upon at the same time. Often a few worktrees would be used in building features in this repo.

---

## Hard Rules

- **no force push.** do not use `git push --force`, `git push -f`, or `--force-with-lease`. if push is rejected, `git pull` (rebase) then push again.
- **no direct push to main.** use a branch and open a pr.

---

## Branch Strategy

### Naming

branch should be named automatically based on the kind of work that is being done.

```
<feature/<short-description>
<infra/<short-description>
<bugs/<short-description>
<tests/<short-description>
<perf/short-description>
```

Examples: `feature/add-pagination`, `perf/reduce-latency`, `tests/e2e-wav-format-export`

- One branch per roadmap item (or per phase if the item is large).
- Be careful that there may be other worktrees - DO NOT work outside of your worktree.

### Base branch

All feature branches start from `main`. Keep your branch up to date:

```bash
git fetch origin
git rebase origin/main
```

Rebase your own branch -- never force-push to `master`.

---

## Commits

### Message format

```
<type>: <what changed>
```

Types: `feature`, `bug`, `tests`, `refactor`, `docs`, `perf`.

Examples:
- `feature: add circuit breaker to HTTP connector`
- `tests: add unit tests for Kafka processor`
- `docs: add a decision log for Camel choice`

Keep the first line under 72 characters. Add a body if the "why" isn't obvious.

### What goes in a commit

- One logical change per commit. Don't mix unrelated changes.
- Put a brief description of what is being changed and to what end.

---

## Pull Requests

### Before opening a PR

1. Rebase on latest `master` and resolve conflicts locally.
2. All tests pass 
3. Formatting is clean 
4. Coverage thresholds met 

### PR content

- Title: same format as commit messages (`feature: add dry-run mode`).
- Description: what changed, why, and how to test it.

---

## When Things Go Wrong

| Problem | Action |
|---------|--------|
| Merge conflict on `master` | The person whose PR caused the conflict resolves it. Don't push the conflict to someone else. |
| Agent made changes outside its lane | Revert the out-of-scope changes before opening the PR. |
