# Decision Log

After any major change (new feature, architectural shift, significant refactor, dependency change, or removal of functionality), update the decision log.

## How to Record New Decisions

### Location

All decision files live in `docs/decisions/`.

### Format

- **File name**: `DECISION_<descriptive-name>.md`
- **Contents**:
  - **Date** of the change.
  - **What** was changed (one-sentence summary).
  - **Why** -- motivation or problem that prompted the change.
  - **Alternatives considered** -- what was evaluated and why it was rejected.
  - **Consequences** -- trade-offs, follow-up work, things to watch.

### Rules

- One file per decision (not a single growing log).
- Create the `docs/decisions/` folder if it doesn't exist.
- Do not skip this step if you made a major change, document the decision before considering the work done.
