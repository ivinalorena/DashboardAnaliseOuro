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

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


RSI_OB,  RSI_OS  = 0.40, -0.40
BB_OB,   BB_OS   = 0.40, -0.40


def _sinal_atual(valor: float, limiar_ob: float, limiar_os: float) -> str:
    if valor > limiar_ob:
        return "Sobrecompra"
    elif valor < limiar_os:
        return "Sobrevenda"
    return "Neutro"


def plot_indicadores_tecnicos(df: pd.DataFrame) -> go.Figure:
    df_plot = df[["date", "rsi", "boll_b", "macd_hist"]].copy()
    df_plot["date"] = pd.to_datetime(df_plot["date"])
    df_plot = df_plot.set_index("date")

    # downsample semanal — last() preserva o sinal pontual de cada indicador
    df_w = df_plot.resample("W").last()

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=("RSI", "Bollinger %B", "MACD — Histograma"),
        vertical_spacing=0.10,
        row_heights=[0.35, 0.35, 0.30],
    )

   
    rsi = df_w["rsi"].dropna()

    fig.add_hrect(y0=RSI_OB,  y1=rsi.max() + 0.05,
                  fillcolor="rgba(239,68,68,0.12)", line_width=0, row=1, col=1)
    fig.add_hrect(y0=rsi.min() - 0.05, y1=RSI_OS,
                  fillcolor="rgba(34,197,94,0.12)", line_width=0, row=1, col=1)
    fig.add_hline(y=RSI_OB,  line_dash="dot", line_color="rgba(239,68,68,0.6)",  line_width=1, row=1, col=1)
    fig.add_hline(y=RSI_OS,  line_dash="dot", line_color="rgba(34,197,94,0.6)",  line_width=1, row=1, col=1)
    fig.add_hline(y=0,        line_dash="solid", line_color="rgba(150,150,150,0.3)", line_width=1, row=1, col=1)
    fig.add_trace(go.Scatter(
        x=rsi.index, y=rsi,
        mode="lines", name="RSI",
        line=dict(color="#f59e0b", width=1.5),
        hovertemplate="%{x|%d/%m/%Y}<br>RSI: %{y:.3f}<extra></extra>",
    ), row=1, col=1)

  
    bb = df_w["boll_b"].dropna()

    fig.add_hrect(y0=BB_OB,  y1=bb.max() + 0.05,
                  fillcolor="rgba(239,68,68,0.12)", line_width=0, row=2, col=1)
    fig.add_hrect(y0=bb.min() - 0.05, y1=BB_OS,
                  fillcolor="rgba(34,197,94,0.12)", line_width=0, row=2, col=1)
    fig.add_hline(y=BB_OB,  line_dash="dot", line_color="rgba(239,68,68,0.6)",  line_width=1, row=2, col=1)
    fig.add_hline(y=BB_OS,  line_dash="dot", line_color="rgba(34,197,94,0.6)",  line_width=1, row=2, col=1)
    fig.add_hline(y=0,       line_dash="solid", line_color="rgba(150,150,150,0.3)", line_width=1, row=2, col=1)
    fig.add_trace(go.Scatter(
        x=bb.index, y=bb,
        mode="lines", name="Bollinger %B",
        line=dict(color="#8b5cf6", width=1.5),
        hovertemplate="%{x|%d/%m/%Y}<br>%%B: %{y:.3f}<extra></extra>",
    ), row=2, col=1)


    macd = df_w["macd_hist"]
    colors_macd = ["#ef4444" if v < 0 else "#22c55e" for v in macd]

    fig.add_hline(y=0, line_dash="solid", line_color="rgba(150,150,150,0.4)", line_width=1, row=3, col=1)
    fig.add_trace(go.Bar(
        x=macd.index, y=macd,
        name="MACD Hist",
        marker_color=colors_macd,
        hovertemplate="%{x|%d/%m/%Y}<br>MACD: %{y:.5f}<extra></extra>",
    ), row=3, col=1)

    fig.update_layout(
        height=650,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=10, t=40, b=0),
        hoverlabel=dict(bgcolor="rgba(30,30,30,0.9)", font_color="white"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)", zeroline=False)

    return fig