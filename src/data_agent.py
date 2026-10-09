"""LangChain pandas agent: natural language → pandas code → answer.

Only run against data you trust: the agent executes generated Python
(allow_dangerous_code=True is required for it to work at all).
"""
from langchain_experimental.agents import create_pandas_dataframe_agent

from llm import get_llm

SYSTEM_PREFIX = """You are a data analyst. Answer questions about the dataframe
using pandas. Be concise. When asked for a table, return markdown.
Column names are lowercase with underscores. Dates are in YYYY-MM-DD."""


def build_agent(df):
    """Build a pandas agent over the given DataFrame."""
    llm = get_llm()
    return create_pandas_dataframe_agent(
        llm,
        df,
        prefix=SYSTEM_PREFIX,
        verbose=False,
        allow_dangerous_code=True,
    )


def ask(agent, question: str) -> str:
    """Ask one question; return the agent's text answer."""
    result = agent.invoke({"input": question})
    return result.get("output", "")
