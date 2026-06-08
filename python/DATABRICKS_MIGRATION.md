# Databricks Setup Guide

Run the LangChain Essentials notebooks on Databricks using **Unity AI Gateway** (Claude Sonnet/Haiku) — no OpenAI API key required.

## Prerequisites (one-time, account admin)

1. Enable **Unity AI Gateway** in Account Console → **Previews**.
2. Confirm endpoints `databricks-claude-sonnet-4-5` and `databricks-claude-haiku-4-5` are available.
3. Clone or sync this repo into your Databricks workspace (open the `python/` folder).

## Required repo files

Open notebooks from the synced `python/` directory so these files resolve:

| File | Purpose |
|------|---------|
| `databricks_model.py` | Configures `MODEL` / `MODEL_FAST` via AI Gateway |
| `env_utils.py` | Optional env / package checks |
| `Chinook.db` | SQL agent notebooks (L1, L6, L8, L9) |
| `pyproject.toml` | Package check in L1 |
| `example.env` | LangSmith keys template (optional) |

## Notebook Setup (every notebook L1–L9)

Run **top-to-bottom** in the Setup section:

| Order | Cell | Action |
|-------|------|--------|
| 1 | `%sh` | Install dependencies (once per cluster) |
| 2 | Python | `from databricks_model import MODEL, MODEL_FAST` |
| 3 | Python | Env check (LangSmith optional) |

After `%sh`, use **Restart Python** on first run so upgraded packages load.

### `%sh` cell (all notebooks)

```sh
pip install --quiet --upgrade "typing_extensions>=4.13.0" \
  langgraph langchain langchain-core langchain-openai \
  langchain-anthropic langchain-community langchain-mcp-adapters
```

### Configure model cell (all notebooks)

```python
from databricks_model import MODEL, MODEL_FAST
```

Gateway routing is defined once in `databricks_model.py`. To change endpoints, edit that file only.

## Model mapping

| Original course model | Databricks variable | Gateway endpoint |
|-----------------------|---------------------|------------------|
| `openai:gpt-5-nano` | `MODEL_FAST` | `databricks-claude-haiku-4-5` |
| `openai:gpt-5-mini` | `MODEL` | `databricks-claude-sonnet-4-5` |
| `openai:gpt-5` | `MODEL` | `databricks-claude-sonnet-4-5` |

## Optional: LangSmith tracing

Set cluster env vars or Databricks secrets — `OPENAI_API_KEY` is **not** needed:

```python
import os
os.environ["LANGSMITH_API_KEY"] = dbutils.secrets.get(scope="<scope>", key="langsmith-api-key")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "lc-essentials"
```

## Sanity check

```python
from databricks_model import MODEL
MODEL.invoke("Say hello in one sentence.")
```

## Troubleshooting

### `TypeError: _TypedDictMeta.__new__() got an unexpected keyword argument 'extra_items'`

**Cause:** Old `typing_extensions` on Python 3.10–3.12 clusters.

**Fix:** Re-run the `%sh` cell, **Restart Python**, confirm you are **not** importing `databricks-langchain` (this repo uses `databricks_model.py` + `langchain-openai` instead).

### `wsfs/fuse ... Cannot find child <unknown>`

**Cause:** Notebook opened without the full `python/` folder synced.

**Fix:** Clone/sync the entire repo; open notebooks from `python/` so `databricks_model.py` and `env_utils.py` are on the path.

### `ModuleNotFoundError: databricks_model`

**Fix:** Ensure the notebook working directory is the `python/` folder (same directory as `databricks_model.py`).

## Push to GitHub → open in Databricks

1. Commit and push this repo (including `databricks_model.py` and updated notebooks).
2. In Databricks: **Workspace → Git folders** → clone your repo.
3. Open any notebook under `python/`.
4. Attach a cluster, run Setup cells, then run the lesson.

## Rollback to OpenAI API (local dev)

Replace `model=MODEL` with `model="openai:gpt-5-mini"` (etc.) and set `OPENAI_API_KEY` in `.env`.
