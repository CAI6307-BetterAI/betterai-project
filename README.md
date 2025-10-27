# betterai-project

## Prerequisites

- UV: <https://docs.astral.sh/uv/getting-started/installation/>

## Setup

1. Sync submodules

   ```sh
   git submodule update --init --remote
   ```

2. Install dependencies

   ```sh
   uv sync
   ```

## Helpful Commands

Installing new dependencies (ex: requests)

```sh
uv add requests
```

Run main.py

```sh
uv run main.py
```
