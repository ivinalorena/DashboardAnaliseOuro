import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=False)
def organizar_df(_df):
    _df = pd.read_csv(_df)
    _df["date"] = pd.to_datetime(_df["date"], errors="coerce")
    _df = _df[_df["date"].between("2000-01-01", "2025-12-31")]
    _df = _df.sort_values("date").reset_index(drop=True)
    _df["date"] = _df["date"].dt.strftime("%Y-%m-%d")

    return _df

@st.cache_data(show_spinner=False)
def df_logreturn(_df):
    log_df = _df[["date", "log_ret_1", "log_ret_5", "log_ret_21"]].copy()
    log_df["date"] = pd.to_datetime(log_df["date"])
    log_df = log_df.sort_values("date").set_index("date")
    return log_df