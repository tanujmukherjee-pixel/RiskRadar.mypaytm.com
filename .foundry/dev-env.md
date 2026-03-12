# dev environment

## commands

| purpose | command |
|---------|---------|
| test | `make test` |
| lint | `make lint` |
| format | `make format` |
| typecheck | `mypy src/ && mypy tests/` |

## code style notes

- Formatter: `black` (default line length: 88)
- Import sorting: `isort`
- Linters: `flake8`, `pylint`
- Type checker: `mypy`
- Lint and typecheck are combined under `make lint`; format uses `make format`
