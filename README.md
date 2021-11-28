# noj-cli

NOJ CLI tool

## Setup

```bash
poetry install
```

## How to run

```bash
# In the project root directory
poetry run python -m cli
# Above command will show help message
```

## Examples

### Get single submission

```bash
poetry run python -m cli submission get -i "<submission_id>"
```

### Generate grade file (.csv format)

```bash
poetry run python -m cli grade --homework "<Course name>/<Homework name>"
```

### Rejudge

```bash
poetry run python -m cli rejudge -p "<pid>"
```
