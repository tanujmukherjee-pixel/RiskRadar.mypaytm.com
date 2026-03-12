# workflow orchestration

this cast is the source of truth (SDK). tool-specific interfaces (claude commands, cursor rules, codex config) are auto-generated from this file during `foundry init`. if this file changes, re-running `foundry generate` regenerates all interfaces.

## flows

most work follows one of these short paths. pick the one that matches what you're doing.

### do work (the core loop -- most of your time)

```
plan → implement → verify → review
```

you have a task, you build it. this is 4 commands and covers 90% of daily work.

### quick (skip planning for small tasks)

```
implement → review
```

quick fixes, typos, small changes. no plan needed -- just do it and ship it.

### setup (once per repo)

```
discover → people
```

run once when you first init a repo. analyzes the codebase, fills `.foundry/vision.md` and `.foundry/people.md`. you rarely touch these again.

### plan work (starting a milestone or sprint)

```
plan-tasks → assign
```

generate tasks from vision milestones, assign them to people. creates the backlog that feeds the core loop.

### delegate (tech lead assigning work)

```
plan-tasks → assign → handoff
```

plan the work, assign to teammates, auto-generate handoff docs. teammates pick up with `resume → plan → implement → verify → review`.

### orchestrate (multi-agent -- parallel execution with subagents)

```
plan-tasks → [spawn subagents per task/wave] → verify → review
```

one agent acts as the orchestrator (tech lead). it plans work, spawns subagents to execute tasks in parallel, then verifies and reviews results. see the **orchestration mode** section below for details.

### headless (fully autonomous -- no human in the loop)

```
plan-tasks → plan → implement → verify → review → archive
```

a single agent runs the full flow end-to-end. invoked via CLI:

```bash
echo "follow foundry workflow. implement milestone 1." | claude -p --allowedTools "..." --permission-mode bypassPermissions
```

the agent reads `.foundry/casts/workflow.md`, picks the right flow, and runs autonomously until done.

---

**tool integration**: bitbucket is accessed via the foundry CLI (`foundry bb pr create`, `foundry bb pipeline trigger`, etc.). the repo owns task context -- plans, branches, handoffs always live in repo files.

---

## orchestration mode

the workflow supports a multi-agent architecture where one agent orchestrates and others execute. this maps to the persona model:

- **orchestrator** = tech lead persona -- plans work, assigns, spawns subagents, verifies, reviews
- **subagents** = team member persona -- each picks up one task, runs the core loop autonomously

### how it works

```
orchestrator (top-level agent)
  │
  ├── reads .foundry/vision.md, .foundry/tasks.json
  ├── runs plan-tasks → generates task list
  ├── builds dependency graph → groups into waves
  │
  ├── wave 1 (independent tasks -- run in parallel)
  │   ├── spawn subagent → task 1 (own branch/worktree, fresh context)
  │   ├── spawn subagent → task 2
  │   └── spawn subagent → task 3
  │   └── wait for all to complete
  │
  ├── wave 2 (depends on wave 1)
  │   ├── spawn subagent → task 4
  │   └── spawn subagent → task 5
  │   └── wait for all to complete
  │
  ├── verify each task's work
  └── review → create PRs
```

### the file system is the message bus

the orchestrator and subagents communicate through the per-task context directory:

```
.foundry/tasks/<task-id>/
  PLAN.md              -- orchestrator or subagent writes the plan
  SUMMARY.md           -- subagent writes what was done
  VERIFICATION.md      -- orchestrator writes verification results
  HANDOFF.md           -- orchestrator writes context for subagent
```

**orchestrator writes**:
- task assignment in `.foundry/tasks.json`
- task context in `.foundry/tasks/<id>/HANDOFF.md` (what the subagent needs to start cold)

**subagent writes**:
- `.foundry/tasks/<id>/PLAN.md` -- its implementation plan
- `.foundry/tasks/<id>/SUMMARY.md` -- what was done, deviations, blockers
- source code on its feature branch

**orchestrator reads**:
- `.foundry/tasks/<id>/SUMMARY.md` -- did the subagent succeed?
- the feature branch diff -- does the code match the plan?
- test results -- do tests pass?

### orchestrator responsibilities

the orchestrator stays lean -- it does NOT implement. it:

1. **plans** -- runs plan-tasks, generates the task backlog
2. **assigns** -- groups tasks into dependency-aware waves
3. **spawns** -- launches one subagent per task with fresh context
4. **monitors** -- checks SUMMARY.md for completion/blockers
5. **unblocks** -- if a subagent is stuck, the orchestrator can intervene or reassign
6. **verifies** -- runs the verify stage on each completed task
7. **reviews** -- creates PRs, handles the review cycle
8. **archives** -- moves done tasks to archive after merge

### subagent responsibilities

each subagent gets a single task and runs the team member flow autonomously:

1. read `.foundry/tasks/<task-id>/HANDOFF.md` for context
2. read relevant source code
3. create `.foundry/tasks/<task-id>/PLAN.md`
4. create feature branch `feature/<task-slug>`
5. write tests, implement, commit
6. write `.foundry/tasks/<task-id>/SUMMARY.md` with results
7. stop and return control to orchestrator

subagents do NOT:
- modify `.foundry/tasks.json` (orchestrator owns the tracker)
- touch other tasks' directories
- create PRs (orchestrator handles review)
- spawn their own subagents (one level of delegation only)

### spawning subagents

the orchestrator spawns subagents using whatever agent is available. the pattern is the same regardless of tool:

**the subagent prompt** (agent-agnostic):
```
you are a foundry subagent. your task:
1. read .foundry/tasks/<id>/HANDOFF.md for full context
2. read .foundry/casts/workflow.md "subagent responsibilities" section
3. create .foundry/tasks/<id>/PLAN.md
4. implement on branch feature/<task-slug>
5. write .foundry/tasks/<id>/SUMMARY.md with results
do not modify .foundry/tasks.json or other tasks' directories.
```

**from an interactive agent session** (claude code, cursor, codex):
use the agent's built-in subagent/task spawning capability. in claude code this is the `Task` tool. in cursor this is background agents. the key is: each subagent gets a fresh context.

**from CLI** (headless):
```bash
# claude
echo "<subagent prompt>" | claude -p --permission-mode bypassPermissions
# codex
codex --quiet "<subagent prompt>"
```

**mixed teams**: the orchestrator can be claude while subagents are codex, or vice versa. the file system is the interface -- any agent that can read/write markdown works.

### context freshness

each subagent starts with a fresh context window. this is intentional -- it prevents context rot (quality degradation as context fills up during long sessions). the orchestrator stays lean (~15% of context budget) and delegates heavy work to subagents with full context budgets.

### headless invocation

to run the full orchestration autonomously (no human in the loop), pipe a prompt to any agent CLI:

**orchestrator mode** (spawns subagents for parallel work):
```bash
echo "you are a foundry orchestrator. read .foundry/casts/workflow.md orchestration mode.
implement all tasks for milestone 1 in .foundry/vision.md.
run: plan-tasks → spawn subagents per wave → verify → review → archive." \
  | <agent-cli> [agent-specific flags]
```

**single task** (one agent, one task, core loop):
```bash
echo "follow foundry workflow core loop for task 3.
read .foundry/casts/workflow.md. plan → implement → verify → review." \
  | <agent-cli> [agent-specific flags]
```

**fully autonomous sprint**:
```bash
echo "you are a foundry orchestrator. read .foundry/casts/workflow.md.
run the full workflow: discover → plan-tasks → orchestrate all tasks → verify → review → archive.
work autonomously. no questions." \
  | <agent-cli> [agent-specific flags]
```

### the spectrum of control

foundry supports the full spectrum from human-driven to fully autonomous:

| mode | human role | agent role |
|------|-----------|-----------|
| **interactive** | decides each step, reviews outputs, steers | analyzes, plans, implements, creates PRs |
| **supervised** | reviews PRs only | everything else autonomously |
| **orchestrated** | kicks off, reviews PRs | orchestrator + subagents run entire milestone |
| **autonomous** | kicks off and walks away | everything end to end |

the same workflow cast powers all modes. the difference is just how many steps the human stays in the loop for.

---

## stage 1: discover

**objective**: analyze the repo and populate `.foundry/vision.md` with purpose, principles, tech stack, and milestones.

**inputs**:
- `README.md` and any docs/ content
- source code structure and package manifests (package.json, go.mod, build.sbt, Cargo.toml, etc.)
- existing documentation, architecture docs
- `.foundry/vision.md` (create from template if missing)
- `.foundry/state.json`

**process**:
1. read README and all docs/ files to understand what the project does and why
2. scan package manifests and source structure to detect tech stack
3. analyze the codebase for architectural patterns (monolith, microservices, event-driven, etc.)
4. identify existing milestones or roadmap if present
5. populate `.foundry/vision.md`:
   - **purpose**: one paragraph summarizing what the repo does
   - **principles**: 3-5 guiding principles inferred from code patterns and docs
   - **milestones**: ordered deliverables (from roadmap if available, otherwise infer from code state)
   - **non-goals**: infer from what the project explicitly avoids
   - **tech stack**: fill the technology table

**outputs**:
- `.foundry/vision.md` -- populated with repo analysis (including tech stack)
- `.foundry/state.json` active stage updated to `discover`

**agent guidance**:
- spawn a research sub-agent to deep-dive repo structure if the codebase is large
- don't guess -- if something can't be confidently determined, leave it as TODO
- for the tech stack, read actual config files (not just file extensions)

---

## stage 2: people

**objective**: define the team roster in `.foundry/people.md` with names, roles, skills, and availability.

**inputs**:
- `git log --format='%aN' | sort -u` -- unique authors
- `CONTRIBUTORS` or similar files
- existing team documentation
- `.foundry/people.md` (create from template if missing)

**process**:
1. extract unique contributors from git history
2. for each contributor, analyze what types of files they've touched to infer skills:
   - `.py` files → `python`
   - `.go` files → `go`
   - `.ts/.tsx/.js` files → `frontend` or `typescript`
   - `Dockerfile`, `*.yaml` (k8s), terraform → `infra`, `devops`
   - `*_test.*`, `test_*.*` → `testing`
3. populate the team roster table in `.foundry/people.md`
4. if running interactively (`foundry init -i`), present the inferred roster for user refinement

**outputs**:
- `.foundry/people.md` -- team roster filled with names and inferred skills
- `.foundry/state.json` active stage updated to `people`

**agent guidance**:
- git log analysis is best-effort -- skill inference from file types is approximate
- always leave availability as TODO unless explicitly told
- ask the user about roles if running interactively

---

## stage 3: plan-tasks

**objective**: generate tasks from vision milestones + repo gap analysis. write them to `.foundry/tasks.json`.

**inputs**:
- `.foundry/vision.md` -- milestones define what the project aims to achieve
- repo state -- what already exists (source files, tests, docs, ci config)
- `.foundry/tasks.json` -- existing task list (append, don't overwrite)

**process**:
1. read milestones from `.foundry/vision.md`
2. for each milestone, analyze the repo to determine what exists vs what's needed
3. diff vision against reality -- each gap becomes a task
4. for each task:
   - write a clear, actionable description
   - assign a priority based on milestone ordering
   - identify dependencies on other tasks
   - assign a sequential task id (`1`, `2`, `3`)
5. add tasks to `.foundry/tasks.json`
6. create the task directory `.foundry/tasks/<task-id>/`

**outputs**:
- `.foundry/tasks.json` -- populated with new tasks
- `.foundry/state.json` active stage updated to `plan-tasks`

**agent guidance**:
- spawn an analysis sub-agent to diff vision against repo reality
- keep task descriptions concrete and verifiable -- "add unit tests for auth service" not "improve testing"
- group tasks by milestone
- mark cross-cutting tasks (ci, docs, testing) that multiple milestones depend on

---

## stage 4: assign

**objective**: match tasks to team members based on skills and availability. create handoff docs for delegation.

**inputs**:
- `.foundry/tasks.json` -- tasks with status `backlog` or `planned` and no assignee
- `.foundry/people.md` -- team roster with skills and availability
- `.foundry/state.json` -- concurrent task limit

**process**:
1. read unassigned tasks from `.foundry/tasks.json`
2. read team roster from `.foundry/people.md`
3. for each unassigned task:
   - analyze the task description to determine required skills
   - match against team members' skills
   - check concurrent task limit -- skip people who already have max tasks in-progress
   - check availability -- skip unavailable people
   - assign the best match
4. update task assignee in `.foundry/tasks.json`
5. **delegation mode**: when assigning to someone other than the current user:
   - auto-create a handoff doc
   - include task context, plan reference (if exists), branch info
   - the handoff enables the assignee to pick up work cold

**outputs**:
- `.foundry/tasks.json` -- assignee filled
- `.foundry/tasks/<id>/HANDOFF.md` -- handoff docs for delegated tasks
- `.foundry/state.json` active stage updated to `assign`

**agent guidance**:
- if only one person on the team, skip assignment logic and assign everything to them
- if skills don't match any team member, flag the task and leave unassigned
- present assignments for user approval before writing

---

## stage 5: plan

**objective**: create a technical implementation plan for a specific task.

**inputs**:
- task from `.foundry/tasks.json` (identified by task id passed as argument)
- `.foundry/vision.md` -- project context and principles
- repo source code and architecture
- existing plans in `.foundry/tasks/` (check if a stub plan already exists)

**process**:
1. read the task description from `.foundry/tasks.json`
2. read `.foundry/vision.md` for project context
3. analyze relevant source code and architecture
4. create the task directory `.foundry/tasks/<task-id>/` if it doesn't exist
5. create `.foundry/tasks/<task-id>/PLAN.md` with:
   - **first line**: single sentence stating what the plan achieves
   - **header metadata**: date, author, approved by (blank)
   - **approach**: how to implement -- specific files to change, patterns to follow
   - **verification**: how to verify the implementation works (tests, manual checks)
   - **open questions**: `## things we should discuss before any implementation`
6. update task status in `.foundry/tasks.json` to `planned`

**outputs**:
- `.foundry/tasks/<task-id>/PLAN.md` -- technical plan
- `.foundry/tasks.json` -- status updated to `planned`
- `.foundry/state.json` active stage updated to `plan`

**agent guidance**:
- spawn a research sub-agent for domain investigation if the task requires unfamiliar technology
- keep plans concrete -- reference specific files, functions, patterns
- if a stub plan exists, expand it rather than starting from scratch
- the plan must include open questions -- never skip this section

---

## stage 6: implement

**objective**: implement tasks following their plans. uses wave-based parallel execution for independent tasks.

**inputs**:
- `.foundry/tasks/<task-id>/PLAN.md` -- the task's implementation plan
- relevant source code
- task dependencies from `.foundry/tasks.json`
- `.foundry/state.json` -- execution config (max concurrent tasks, use worktrees)

**process**:

### single task execution
1. read the plan file for the task
2. create a feature branch: `feature/<task-slug>`
3. if using worktrees: create a git worktree for the branch
4. write failing tests covering acceptance criteria
5. implement iteratively -- run tests after each logical change
6. make small, atomic commits following `.foundry/casts/collaboration.md` conventions
7. continue until all tests pass
8. update task status in `.foundry/tasks.json` to `in-progress`

### wave-based parallel execution (multiple tasks)
1. read all tasks to be executed from `.foundry/tasks.json`
2. build a dependency graph from the `depends on` column
3. group tasks into waves -- a wave contains tasks with no unresolved dependencies
4. for each wave:
   - execute all tasks in the wave in parallel
   - each task gets its own branch, worktree (if enabled), and fresh agent context
   - wait for all tasks in the wave to complete before starting the next wave
5. context freshness: each parallel task starts with a fresh agent context to prevent context rot from accumulated state

**outputs**:
- source code changes on feature branches
- test files
- `.foundry/tasks.json` -- status updated to `in-progress`
- `.foundry/state.json` active stage updated to `implement`

**agent guidance**:
- each task in a wave should get a fresh sub-agent (don't share context between parallel tasks)
- respect the concurrent task limit from `.foundry/state.json`
- if a task blocks unexpectedly, don't block the entire wave -- continue other tasks and report the blocker
- commit frequently with clear messages

---

## stage 7: verify

**objective**: verify implemented work against its plan before creating a PR.

**inputs**:
- `.foundry/tasks/<task-id>/PLAN.md` -- the task's implementation plan
- diff of changes (`git diff main...<branch>`)
- test results
- `.foundry/casts/security.md` -- security checklist

**process**:
1. read the plan file and note all acceptance criteria
2. run the full test suite -- all tests must pass
3. review the diff against plan requirements:
   - every planned change should be in the diff
   - no unplanned changes should be present
   - no debug code, temporary files, or hardcoded values
4. walk the security checklist from `.foundry/casts/security.md`
5. check documentation -- if behavior changed, docs should be updated
6. write verification results to `.foundry/tasks/<task-id>/VERIFICATION.md`
7. update task status in `.foundry/tasks.json` to `review`

**outputs**:
- `.foundry/tasks/<task-id>/VERIFICATION.md` -- verification results
- `.foundry/tasks.json` -- status updated to `review`
- `.foundry/state.json` active stage updated to `verify`

**agent guidance**:
- be strict -- if tests fail, go back to implement stage and fix
- if unplanned changes exist, explain why they were necessary in verification notes
- security checklist is not optional

---

## stage 8: review

**objective**: create a pull request and handle the review cycle until merge.

**inputs**:
- `.foundry/tasks/<task-id>/PLAN.md` -- the task's implementation plan
- task from `.foundry/tasks.json`
- branch diff (`git diff main...<branch>`)
- `.foundry/state.json` -- VCS platform config (bitbucket/github)

**process**:
1. push the feature branch to the remote
2. create a pull request:
   - title: task description (short)
   - body: reference to plan file, summary of changes, test plan
   - use `foundry bb pr create` (bitbucket) or `gh pr create` (github)
3. respond to review comments:
   - address each comment with a code change or explanation
   - push fixes as new commits (don't force push)
4. after approval and merge:
   - update task status in `.foundry/tasks.json` to `done`
   - write execution summary to `.foundry/tasks/<task-id>/SUMMARY.md`

**outputs**:
- pull request on bitbucket/github
- `.foundry/tasks/<task-id>/SUMMARY.md` -- what was done, deviations from plan
- `.foundry/tasks.json` -- status updated to `done` after merge
- `.foundry/state.json` active stage updated to `review`

**agent guidance**:
- follow PR conventions from `.foundry/casts/collaboration.md`
- include the plan file path in the PR description so reviewers can check against the plan
- never force push during review
- read `.foundry/state.json` version control section to determine the VCS platform

**tool integration**:
- **bitbucket**: create PR via `foundry bb pr create`. read project/org and repo slug from `.foundry/state.json`.
- **github**: create PR via `gh pr create`. read org and repo from `.foundry/state.json`.

---

## auxiliary stages

these can be invoked at any time, independent of the main pipeline.

### handoff

create a handoff document for another person to pick up work:

- include the task id from `.foundry/tasks.json`
- reference the plan file if one exists
- include the branch name and current state of implementation
- note any blockers or open questions from the plan

### resume

resume work from a handoff or from `.foundry/state.json`:

1. if a handoff file is specified, read it and use as context
2. otherwise, read `.foundry/state.json` to determine the active stage and continue from there
3. read `.foundry/tasks.json` to find in-progress tasks assigned to you
4. pick up where the last session left off

### progress

show the current state of all tasks and workflow:

1. read `.foundry/tasks.json` and display a summary grouped by status
2. show the active stage from `.foundry/state.json`
3. list any blockers

### archive

archive completed tasks to keep the active tracker lean. tasks are never deleted -- they move to the archive.

1. read `.foundry/tasks.json` for tasks with status `done`
2. for each done task:
   - set status to `archived` and add a completion date
   - move the task directory from `.foundry/tasks/<task-id>/` to `.foundry/tasks/archive/<task-id>/`
3. report how many tasks were archived

this can be run manually or automatically after a milestone is complete.

### help

show what foundry can do and how to use it. this is the first command a new user should try.

**objective**: show available commands, current project status, and links to documentation.

**process**:
1. read `AGENTS.md` and list the cast directory (available casts and when to read them)
2. show all available slash commands grouped by category
3. read `.foundry/state.json` -- show current session state
4. read `.foundry/tasks.json` -- show a one-line task summary
5. show common workflows:
   - "have a task? run `foundry task plan <id>` → `foundry task implement <id>` → `foundry task review <id>`"
   - "quick fix? run `foundry task implement <id>` → `foundry task review <id>`"

**outputs**: none (display only)

### quick-start

guided onboarding for new users. walks through the essential first steps to start using foundry in a repo.

**objective**: walk a new user through foundry setup and their first task, step by step.

**inputs**:
- `.foundry/state.json`
- `.foundry/vision.md`
- `.foundry/tasks.json`

**process**:
1. **check setup**: read `.foundry/state.json`. if it doesn't exist or has unconfigured fields, tell the user to run `foundry init` first and stop here.
2. **show project context**: read `.foundry/vision.md` and display a one-line summary of the project purpose.
3. **show tasks**: read `.foundry/tasks.json`.
   - if tasks exist, show the top 3 by priority and suggest: "pick a task and run `foundry task plan <id>`"
   - if no tasks, suggest: "run `foundry task create` to add tasks"
4. **demonstrate the core loop**: explain the 4-step flow:
   - `foundry task plan <id>` -- create an implementation plan
   - `foundry task implement <id>` -- implement the plan
   - `foundry task review <id>` -- review and create PR
   - `foundry task complete <id>` -- mark done after merge

**outputs**: none (display only)

---

## per-task context

each task gets a directory under `.foundry/tasks/` that holds all its context:

```
.foundry/tasks/
  <task-id>/
    PLAN.md              -- technical implementation plan
    SUMMARY.md           -- execution summary (what was done, deviations)
    VERIFICATION.md      -- verification results
    HANDOFF.md           -- handoff doc if task was delegated
    notes.md             -- any additional context, research, decisions
```

this keeps task context self-contained. agents working on a task read `.foundry/tasks/<id>/` for full context. the task tracker in `.foundry/tasks.json` remains a lightweight index pointing to these directories.

when a task is archived:
- the task directory moves to `.foundry/tasks/archive/<task-id>/`
- nothing is deleted

## plan lifecycle

- **active plans** → `.foundry/tasks/<task-id>/PLAN.md`
- **implemented plans** → `.foundry/tasks/archive/<task-id>/PLAN.md`
- **rejected plans** → `.foundry/tasks/archive/<task-id>/PLAN.md` (with rejection note)
- **before implementation**: write failing tests covering acceptance criteria. implement iteratively. run the full test suite after each change. do not stop until all tests pass.

## contribution log

every agent that works on a plan, task, or workflow stage must append a contribution entry to the relevant file under a `## contributions` section:
- agent name/model
- date
- brief summary of what they did
