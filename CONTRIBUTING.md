# contributing

## setup

Install dependencies using [Poetry](https://python-poetry.org/):

```bash
brew install poetry
poetry env use python3.12   # Python 3.13 is not supported (torch download fails)
poetry install
```

Python 3.12 is required.

## dev commands

```bash
# run the app
poetry run uvicorn src:app --reload
# or
make run

# install dependencies
make install

# run tests
make test

# run tests with coverage
make cover

# lint (flake8, black --check, isort --check, mypy, pylint)
make lint

# format (black, isort)
make format

# run lint + test
make check

# clean build artifacts
make clean
```

## code style

Code is formatted with [black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/). Static analysis uses [flake8](https://flake8.pycqa.org/), [mypy](https://mypy.readthedocs.io/), and [pylint](https://pylint.readthedocs.io/). Run `make format` before committing and `make lint` to verify.

## branching

Branch off `main` for all changes. Use short descriptive branch names (e.g. `feature/my-feature` or `fix/my-bug`). Open a pull request targeting `main` when the work is ready for review.
