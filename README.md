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

### Find out users who submit at least once

```bash
poetry run python -m cli submission get-list \
    --tag hw2 \
    --course 111-Computer-Programming-I \
    --before 2022-09-20T12:01 \
    -f user
```

and generate csv from above output

```bash
jq -r '[.[].user | .username] | unique | .[] | "\(.),100"' submission.json 
```
