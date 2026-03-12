# agent workflow protocol

## sequence

```
1. UNDERSTAND
   - Read AGENTS.md and any agent-specific config (CLAUDE.md, .cursorrules, etc.)
   - Read the primary README and docs/architecture/ for system context
   - Read .foundry/vision.md, .foundry/people.md, .foundry/tasks.json for project context and current work
   - Explore the repo's file tree -- understand the actual structure

2. PREPARE
   - Check the workflow state in .foundry/state.json -- what stage are we in?
   - Read .foundry/tasks.json for active/in-progress tasks relevant to your work
   - If resuming, read the most recent handoff in .foundry/handoffs/ or .foundry/tasks/<id>/HANDOFF.md
   - Verify local environment is ready: dependencies installed, tests passing, no uncommitted changes on main

3. PLAN
   - Write a short plan: what will change, what will not, how to verify
   - Save the plan in the .foundry/plans/ folder and make it available for review before you begin

4. EXECUTE
   - Create a feature branch following the branch naming convention in collaboration.md
   - Write/update tests first (or alongside)
   - Make small, verifiable changes in reviewable commits
   - Run after each logical change
   - Update documentation if behavior changes

5. VERIFY
   - Review your own diff against the main branch
   - Walk the security checklist (.foundry/casts/security.md)
   - Ensure no debug logging or temporary code left behind

6. SUBMIT
   - Update documentation wherever needed (README, architecture doc, decision logs etc)
   - Write clear PR description with context, approach, and test plan
```

## when stuck or uncertain

- if requirements are ambiguous → state assumptions, implement, and flag in pr
- whenever there is a change in the user experience, ask the user giving them options on what to do and a recommendation.
- if multiple valid approaches exist → pick the simpler one
- if a change feels too large → break it into smaller prs
- if tests are flaky → fix the flake before continuing, don't skip
- if you're unsure about security implications → flag it explicitly in pr

## agent roles (optional boundaries)

| role | purpose | scope |
|------|---------|-------|
| @test-agent | add or upgrade tests | test files, harness, fixtures, test config only |
| @docs-agent | update documentation | documentation files only |
| @lint-agent | formatting and style | mechanical style changes only -- no logic changes |
| @security-agent | threat modeling, secure coding review | read-only analysis by default; code changes only if authorized |
| @triage-agent | diagnose issues from logs/symptoms | read-only; outputs suspected root causes and minimal patch options |
