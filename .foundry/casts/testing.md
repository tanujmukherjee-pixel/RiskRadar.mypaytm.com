# Testing Standards

## Rules

- If the repo does not have a single testing framework, come up with your own recommendation of the best testing framework for the purpose of that repo. 
- (Try to) keep all tests in the tests/ directory. 
- (Try to) leverage the same framework for all new test-cases unless there is high complexity in doing that kind of testing in the existing framework - in which case you should pick a new framework for what the old one does not cover well.
- When you add a feature, add tests in the same commit. Tests are not optional -- a change is not complete until its tests pass.
- When you fix a bug, add a regression test that would have caught it.
- Any major change must ship with tests covering core behavior, edge cases, and error handling. Do not defer test-writing. 
- In some situations it might be better to first write the test-cases (that fail) and work towards making them pass. 
- Tests must be runnable without real external services -- mock all external dependencies.
- The test suite must always pass. If you break a test, fix it immediately.

## Verification

After writing or changing tests verify them.
