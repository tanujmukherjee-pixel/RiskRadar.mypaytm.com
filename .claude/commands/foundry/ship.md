ship the current changes end-to-end: branch, push, PR, wait for green CI, merge, confirm main is green.

## instructions

you MUST follow these steps in order. do not skip steps. if a step fails, follow the recovery path described. ship is **resumable** — detect where you are in the workflow and pick up from there.

### step 1: assess current state

1. run `git status` and `git branch --show-current` to determine the current branch and working tree state.
2. determine which sub-step to enter:
   - **on main with no changes**: stop and tell the user there is nothing to ship.
   - **on main with changes**: go to step 1a (create branch).
   - **on a feature branch with changes**: go to step 1b (commit and push).
   - **on a feature branch with clean tree**: go to step 2 (check/create PR).

### step 1a: create a branch (from main)

1. determine a branch name from the changes (use `feature/`, `bug/`, `refactor/`, `tests/`, `docs/`, `perf/` prefix per project conventions). keep it short and descriptive.
2. run `git checkout -b <branch>` to create the branch.
3. continue to step 1b.

### step 1b: commit and push

1. stage the relevant files (`git add <files>` — be specific, do not use `git add -A`).
2. commit with a conventional message: `<type>: <what changed>` (lowercase, first line <=72 chars).
3. push with `git push -u origin <branch>` (or `git push` if already tracking).

### step 2: create a pull request

1. run `foundry bb pr list` to check if a PR already exists for this branch.
2. if a PR already exists, capture the PR id and skip to step 3.
3. if no PR exists, run `foundry bb pr create` to create one and capture the PR id.

### step 3: wait for the pipeline

1. wait 15 seconds for the pipeline to start.
2. run `foundry bb pipeline watch` to block until the pipeline completes. this polls automatically and prints the final result.
3. if the result is **SUCCESSFUL**, proceed to step 5 (merge).
4. if the result is **FAILED**, proceed to step 4 (fix).

### step 4: fix a failed build

1. run `foundry bb pipeline logs` to get the failure logs.
2. read the logs and diagnose the issue.
3. fix the code.
4. run `make lint` and `make test` locally to verify the fix.
5. stage, commit, and push the fix (`git push`).
6. go back to step 3 to wait for the new pipeline.

### step 5: merge the PR

1. run `foundry bb pr merge <pr_id>` to merge.
2. if merge fails (e.g. conflicts), tell the user and stop.

### step 6: confirm main is green

1. wait 15 seconds for the main pipeline to start.
2. run `foundry bb pipeline watch` to block until the main pipeline completes.
3. if **SUCCESSFUL**: report success — ship complete.
4. if **FAILED**: run `foundry bb pipeline logs`, show the failure to the user, and suggest next steps.

## important

- never force-push.
- never push directly to main.
- always use `foundry bb` commands for bitbucket operations (pr create, pr merge, pipeline watch/logs).
- if any step fails more than 3 times, stop and ask the user for guidance instead of looping forever.
- keep the user informed at each major step with a short status update.
