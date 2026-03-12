# Cross-Platform Compatibility

- Mostly the repo should work on MacOS and Ubuntu 24.04


## shell scripts

all shell scripts use `set -eo pipefail`. remember that `grep` returns exit code 1 when it finds no matches -- this is fatal under `pipefail`. always append `|| true` when a grep match is optional (e.g., extracting a count that may be zero). this applies to any command in a pipeline that can legitimately produce no output.
