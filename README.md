# agency

brew install poetry
brew install uvicorn
poetry env use python3.12 (3.13 doesn't work unable to download torch)
poetry install 

## To run

```bash
poetry run uvicorn src:app --reload
```