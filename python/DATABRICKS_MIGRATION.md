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
| 1 | `%pip` | Install dependencies into the **notebook kernel** (once per cluster) |
| 2 | Python | `dbutils.library.restartPython()` |
| 3 | Python | `from databricks_model import MODEL, MODEL_FAST` |
| 4 | Python | Env check (LangSmith optional) |

**Important:** Use `%pip`, not `%sh pip`. Shell installs go to a different Python than the notebook kernel.

### `%pip` cell (all notebooks)

```python
%pip install -q --upgrade "typing_extensions>=4.13.0" \
  langgraph langchain langchain-core langchain-openai \
  langchain-anthropic langchain-community langchain-mcp-adapters
```

### Restart Python cell (all notebooks)

```python
dbutils.library.restartPython()
```

### Configure model cell (all notebooks)

```python
import sys
sys.dont_write_bytecode = True  # Databricks Git folders reject __pycache__

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

**Cause:** Packages were installed with `%sh pip` (wrong Python) or `typing_extensions` is still too old in the kernel.

**Fix:**
1. Run the `%pip` cell (not `%sh`)
2. Run `dbutils.library.restartPython()`
3. Re-run the import cell

### `wsfs/fuse ... __pycache__ is not allowed`

**Cause:** Python wrote a `__pycache__` folder into the Git-backed workspace path.

**Fix:**
1. Delete any `python/__pycache__` folder in the workspace (if present)
2. Re-run import with `sys.dont_write_bytecode = True` (already in the notebook)
3. Pull latest repo — `databricks_model.py` sets this automatically

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
