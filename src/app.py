"""Streamlit UI: upload a CSV, chat with it, plus instant quick charts.

Run:  streamlit run src/app.py
"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from config import SAMPLE_CSV
from data_agent import ask, build_agent
from llm import ollama_reachable, provider_label, resolve_provider

st.set_page_config(page_title="Chat With Your Data", layout="wide")
st.title("Chat With Your Data")

provider = resolve_provider()
st.sidebar.caption(f"LLM: {provider_label()}")
if provider == "ollama" and not ollama_reachable():
    st.sidebar.warning(
        "Ollama isn't running, so chat answers are unavailable. "
        "Start Ollama locally, or add a free Gemini key "
        "(`GOOGLE_API_KEY`) and redeploy — the app picks it up automatically."
    )


@st.cache_resource
def get_agent(csv_path: str, mtime: float):
    """Cache the agent per file (mtime busts the cache on re-upload)."""
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return build_agent(df), df


# ---- data source ----
uploaded = st.sidebar.file_uploader("Upload a CSV", type=["csv"])
if uploaded is not None:
    os.makedirs("data/uploads", exist_ok=True)
    csv_path = os.path.join("data/uploads", uploaded.name)
    with open(csv_path, "wb") as f:
        f.write(uploaded.getbuffer())
else:
    csv_path = SAMPLE_CSV
    st.sidebar.info("Using sample_sales.csv — upload your own CSV any time.")

mtime = os.path.getmtime(csv_path)
try:
    agent, df = get_agent(csv_path, mtime)
except Exception as e:  # e.g. Ollama not running
    st.error(f"Could not start the agent: {e}")
    st.stop()

st.sidebar.subheader("Dataset preview")
st.sidebar.dataframe(df.head(), use_container_width=True)
st.sidebar.caption(f"{len(df)} rows × {len(df.columns)} columns")

# ---- quick charts (no LLM calls) ----
st.sidebar.subheader("Quick charts")
num_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(exclude="number").columns.tolist()
if num_cols:
    hist_col = st.sidebar.selectbox("Histogram of", num_cols, key="hist")
    fig = px.histogram(df, x=hist_col, title=f"Distribution of {hist_col}")
    st.sidebar.plotly_chart(fig, use_container_width=True)
if cat_cols and num_cols:
    bar_cat = st.sidebar.selectbox("Top categories in", cat_cols, key="barcat")
    bar_val = st.sidebar.selectbox("Summed over", num_cols, key="barval")
    top = df.groupby(bar_cat)[bar_val].sum().nlargest(10).reset_index()
    fig2 = px.bar(top, x=bar_cat, y=bar_val,
                  title=f"Top 10 {bar_cat} by {bar_val}")
    st.sidebar.plotly_chart(fig2, use_container_width=True)

# ---- chat ----
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {"role": "assistant",
         "content": "Ask me anything about this dataset. Try: "
                    "\"total revenue by region\" or \"which product sold the most?\""}
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask about your data…")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                answer = ask(agent, question)
            except Exception as e:
                answer = f"That failed: {e}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
