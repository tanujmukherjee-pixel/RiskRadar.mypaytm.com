# security

## reporting

if you discover a security vulnerability, report it privately to the maintainers. do not open a public issue.

contact: atul.shridhar@paytm.com

## credential handling

foundry supports two credential modes:

**environment variables** (preferred for ci/cd):

| variable | purpose |
|----------|---------|
| `ATLASSIAN_BITBUCKET_USERNAME` | bitbucket username |
| `ATLASSIAN_BITBUCKET_APP_PASSWORD` | bitbucket app password |
| `ATLASSIAN_BITBUCKET_URL` | bitbucket base URL (optional) |

**state.json** (for local dev): credentials can be stored in `~/.foundry/state.json` (user-level) or `.foundry/state.json` (project-level) under the `bitbucket` section. run `foundry bb auth setup` to configure.

never hardcode secrets in source files. never commit `.env` files.

## local storage

files committed to git (no credentials):

- `.foundry/tasks.json` -- task list
- `.foundry/state.json` -- project configuration
- `.foundry/casts/` -- agent behavior contracts
- `.foundry/.metadata` -- version info
- `.foundry/scores.json` -- maturity scores

files gitignored (ephemeral):

- `.foundry/.base/` -- sync merge bases

foundry does not transmit local data to external services except through explicitly configured bitbucket API calls.

## agent permissions

foundry invokes claude as a subprocess. the agent inherits the permissions of the user's shell environment. foundry does not escalate privileges or bypass agent permission models.
