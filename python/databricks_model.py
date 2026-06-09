"""LangChain chat models routed through Databricks Unity AI Gateway.

Import in Databricks notebooks after running the Setup %pip cell and restart:

    from databricks_model import MODEL, MODEL_FAST

Requires notebook context (dbutils) — not for local OpenAI API usage.
"""

import subprocess
import sys

# Databricks Git folders reject __pycache__ on the workspace fuse filesystem.
sys.dont_write_bytecode = True


def _version_tuple(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for piece in version.split(".")[:3]:
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _ensure_typing_extensions() -> None:
    """LangChain 1.x needs typing_extensions>=4.13 for TypedDict extra_items."""
    try:
        import typing_extensions as te

        if _version_tuple(te.__version__) >= (4, 13, 0):
            return
    except Exception:
        pass

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "typing_extensions>=4.13.0"],
    )


_ensure_typing_extensions()

from langchain_openai import ChatOpenAI


def _get_dbutils():
    """dbutils is in notebook scope but not inside imported .py files."""
    try:
        from databricks.sdk.runtime import dbutils as _dbutils

        return _dbutils
    except ImportError:
        pass

    try:
        from pyspark.dbutils import DBUtils
        from pyspark.sql import SparkSession

        return DBUtils(SparkSession.builder.getOrCreate())
    except ImportError:
        pass

    ip = __import__("IPython").get_ipython()
    if ip is not None and "dbutils" in ip.user_ns:
        return ip.user_ns["dbutils"]

    raise RuntimeError(
        "dbutils is not available. Run this notebook on Databricks, not locally."
    )


def _normalize_workspace_url(url: str) -> str:
    """Return https://<workspace-host> with no trailing slash."""
    url = url.strip().rstrip("/")
    if url.startswith("https://"):
        return url
    if url.startswith("http://"):
        return "https://" + url.removeprefix("http://")
    return f"https://{url}"


def _get_workspace_url(dbutils) -> str:
    """Resolve the workspace-specific URL (not the regional apiUrl shard).

    ctx.apiUrl() often returns a regional host like nvirginia.cloud.databricks.com
    instead of the workspace host (dbc-....cloud.databricks.com), which breaks
    AI Gateway with 404. Prefer spark conf and browserHostName when available.
    """
    import os

    override = os.environ.get("DATABRICKS_HOST") or os.environ.get("DATABRICKS_WORKSPACE_URL")
    if override:
        return _normalize_workspace_url(override)

    try:
        from pyspark.sql import SparkSession

        spark_url = SparkSession.builder.getOrCreate().conf.get(
            "spark.databricks.workspaceUrl",
            None,
        )
        if spark_url:
            return _normalize_workspace_url(spark_url)
    except Exception:
        pass

    ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    try:
        browser_host = ctx.browserHostName().get()
        if browser_host:
            return _normalize_workspace_url(browser_host)
    except Exception:
        pass

    return _normalize_workspace_url(ctx.apiUrl().get())


_dbutils = _get_dbutils()
ctx = _dbutils.notebook.entry_point.getDbutils().notebook().getContext()
workspace_url = _get_workspace_url(_dbutils)
token = ctx.apiToken().get()
gateway_base_url = f"{workspace_url}/ai-gateway/mlflow/v1"

print(
    f"Python {sys.version_info.major}.{sys.version_info.minor} | "
    f"gateway: {gateway_base_url}"
)

MODEL = ChatOpenAI(
    model="databricks-claude-sonnet-4-5",
    api_key=token,
    base_url=gateway_base_url,
)
MODEL_FAST = ChatOpenAI(
    model="databricks-claude-haiku-4-5",
    api_key=token,
    base_url=gateway_base_url,
)
