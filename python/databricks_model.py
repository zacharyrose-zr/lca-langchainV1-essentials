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


ctx = _get_dbutils().notebook.entry_point.getDbutils().notebook().getContext()
workspace_url = ctx.apiUrl().get().rstrip("/")
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
