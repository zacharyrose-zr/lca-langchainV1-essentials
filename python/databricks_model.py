"""LangChain chat models routed through Databricks Unity AI Gateway.

Import in Databricks notebooks after running the Setup %sh cell:

    from databricks_model import MODEL, MODEL_FAST

Requires notebook context (dbutils) — not for local OpenAI API usage.
"""

import sys

from langchain_openai import ChatOpenAI

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
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
