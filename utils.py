import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

RSI_OB,  RSI_OS  = 0.40, -0.40
BB_OB,   BB_OS   = 0.40, -0.40

LOOKBACK = 60  # tamanho da janela deslizante (dias)
HORIZONS = [5, 15, 30]  # horizontes de predição
GAP = max(HORIZONS)  # gap entre splits (anti-vazamento)
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

def _sinal_atual(valor: float, limiar_ob: float, limiar_os: float) -> str:
    if valor > limiar_ob:
        return "Sobrecompra"
    elif valor < limiar_os:
        return "Sobrevenda"
    return "Neutro"


def plot_indicadores_tecnicos(df_idx: pd.DataFrame) -> go.Figure:
    """df_idx deve ter DatetimeIndex e colunas: rsi, boll_b, macd_hist."""

    rsi  = df_idx["rsi"].dropna()
    bb   = df_idx["boll_b"].dropna()
    macd = df_idx["macd_hist"].dropna()

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=("RSI", "Bollinger %B", "MACD — Histograma"),
        vertical_spacing=0.10,
        row_heights=[0.35, 0.35, 0.30],
    )

    fig.add_hrect(y0=RSI_OB, y1=rsi.max() + 0.05,
                  fillcolor="rgba(239,68,68,0.12)", line_width=0, row=1, col=1)
    fig.add_hrect(y0=rsi.min() - 0.05, y1=RSI_OS,
                  fillcolor="rgba(34,197,94,0.12)", line_width=0, row=1, col=1)
    fig.add_hline(y=RSI_OB, line_dash="dot", line_color="rgba(239,68,68,0.6)",   line_width=1, row=1, col=1)
    fig.add_hline(y=RSI_OS, line_dash="dot", line_color="rgba(34,197,94,0.6)",   line_width=1, row=1, col=1)
    fig.add_hline(y=0,       line_dash="solid", line_color="rgba(150,150,150,0.3)", line_width=1, row=1, col=1)
    fig.add_trace(go.Scatter(
        x=rsi.index, y=rsi, mode="lines", name="RSI",
        line=dict(color="#f59e0b", width=1.5),
        hovertemplate="%{x|%d/%m/%Y}<br>RSI: %{y:.3f}<extra></extra>",
    ), row=1, col=1)


    fig.add_hrect(y0=BB_OB, y1=bb.max() + 0.05,
                  fillcolor="rgba(239,68,68,0.12)", line_width=0, row=2, col=1)
    fig.add_hrect(y0=bb.min() - 0.05, y1=BB_OS,
                  fillcolor="rgba(34,197,94,0.12)", line_width=0, row=2, col=1)
    fig.add_hline(y=BB_OB, line_dash="dot", line_color="rgba(239,68,68,0.6)",   line_width=1, row=2, col=1)
    fig.add_hline(y=BB_OS, line_dash="dot", line_color="rgba(34,197,94,0.6)",   line_width=1, row=2, col=1)
    fig.add_hline(y=0,      line_dash="solid", line_color="rgba(150,150,150,0.3)", line_width=1, row=2, col=1)
    fig.add_trace(go.Scatter(
        x=bb.index, y=bb, mode="lines", name="Bollinger %B",
        line=dict(color="#8b5cf6", width=1.5),
        hovertemplate="%{x|%d/%m/%Y}<br>%%B: %{y:.3f}<extra></extra>",
    ), row=2, col=1)

  
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(150,150,150,0.4)", line_width=1, row=3, col=1)
    fig.add_trace(go.Bar(
        x=macd.index, y=macd, name="MACD Hist",
        marker_color=["#ef4444" if v < 0 else "#22c55e" for v in macd],
        hovertemplate="%{x|%d/%m/%Y}<br>MACD: %{y:.5f}<extra></extra>",
    ), row=3, col=1)

    fig.update_layout(
        height=650, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=10, t=40, b=0),
        hoverlabel=dict(bgcolor="rgba(30,30,30,0.9)", font_color="white"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)", zeroline=False)

    return fig

def plot_drawdown_serie(df_idx: pd.DataFrame) -> go.Figure:
    """Série completa com anotações nos principais eventos de crise."""
    dd = df_idx["drawdown_252"].dropna()

    fig = go.Figure()

    
    fig.add_hrect(y0=-0.10, y1=0.005,
                  fillcolor="rgba(34,197,94,0.07)", line_width=0)
    fig.add_hrect(y0=-0.20, y1=-0.10,
                  fillcolor="rgba(251,146,60,0.12)", line_width=0)
    fig.add_hrect(y0=-0.50, y1=-0.20,
                  fillcolor="rgba(239,68,68,0.12)", line_width=0)

    
    fig.add_hline(y=-0.10, line_dash="dot",
                  line_color="rgba(251,146,60,0.7)", line_width=1.2,
                  annotation_text="Atenção −10%",
                  annotation_position="top right",
                  annotation_font=dict(color="rgba(251,146,60,0.9)", size=11))
    fig.add_hline(y=-0.20, line_dash="dot",
                  line_color="rgba(239,68,68,0.7)", line_width=1.2,
                  annotation_text="Severo −20%",
                  annotation_position="top right",
                  annotation_font=dict(color="rgba(239,68,68,0.9)", size=11))

   
    fig.add_trace(go.Scatter(
        x=dd.index, y=dd,
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.13)",
        line=dict(color="#6366f1", width=1.5),
        hovertemplate="%{x|%d/%m/%Y}<br>Drawdown: %{y:.2%}<extra></extra>",
    ))

    
    crises = [
        ("2008-11-13", -0.297, "Crise\nfinanceira"),
        ("2013-06-27", -0.325, "Crash\ndo ouro"),
        ("2020-11-30", -0.134, "COVID-19"),
        ("2022-09-26", -0.204, "Fed\nhiking"),
    ]
    for data, val, label in crises:
        fig.add_annotation(
            x=data, y=val,
            text=label,
            showarrow=True,
            arrowhead=2, arrowsize=1, arrowwidth=1.2,
            arrowcolor="rgba(239,68,68,0.7)",
            ax=0, ay=-36,
            font=dict(size=10, color="#374151"),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(209,213,219,0.8)",
            borderwidth=1, borderpad=3,
        )

    fig.update_layout(
        height=380, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=90, t=20, b=0),
        hoverlabel=dict(bgcolor="rgba(30,30,30,0.9)", font_color="white"),
        yaxis=dict(tickformat=".0%", title="Drawdown (252d)"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    return fig


def plot_drawdown_ano(df_idx: pd.DataFrame) -> go.Figure:
    """Drawdown filtrado por ano — resolução diária."""
    dd = df_idx["drawdown_252"].dropna()

    fig = go.Figure()

    fig.add_hrect(y0=-0.10, y1=0.005,
                  fillcolor="rgba(34,197,94,0.07)", line_width=0)
    fig.add_hrect(y0=-0.20, y1=-0.10,
                  fillcolor="rgba(251,146,60,0.12)", line_width=0)
    fig.add_hrect(y0=-0.50, y1=-0.20,
                  fillcolor="rgba(239,68,68,0.12)", line_width=0)

    fig.add_hline(y=-0.10, line_dash="dot",
                  line_color="rgba(251,146,60,0.7)", line_width=1.2,
                  annotation_text="Atenção −10%",
                  annotation_position="top right",
                  annotation_font=dict(color="rgba(251,146,60,0.9)", size=11))
    fig.add_hline(y=-0.20, line_dash="dot",
                  line_color="rgba(239,68,68,0.7)", line_width=1.2,
                  annotation_text="Severo −20%",
                  annotation_position="top right",
                  annotation_font=dict(color="rgba(239,68,68,0.9)", size=11))

    
    pior = dd.min()
    cor  = "#ef4444" if pior < -0.20 else "#f97316" if pior < -0.10 else "#22c55e"

    fig.add_trace(go.Scatter(
        x=dd.index, y=dd,
        mode="lines",
        fill="tozeroy",
        fillcolor=f"rgba({','.join(str(int(c*255)) for c in _hex_to_rgb(cor))},0.15)",
        line=dict(color=cor, width=1.8),
        hovertemplate="%{x|%d/%m/%Y}<br>Drawdown: %{y:.2%}<extra></extra>",
    ))

    fig.update_layout(
        height=300, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=90, t=10, b=0),
        hoverlabel=dict(bgcolor="rgba(30,30,30,0.9)", font_color="white"),
        yaxis=dict(tickformat=".0%"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    return fig


def _hex_to_rgb(hex_color: str) -> tuple:
    """Converte #rrggbb → (r, g, b) em escala 0-1 para o fillcolor do Plotly."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


COLORS = {
    "treino": "#3b82f6",    
    "val": "#f0a500",       
    "teste": "#ef4444"      
}
LABELS = {
    "treino": "Treino",
    "val": "Validação",
    "teste": "Teste"
}


def plot_divisao_temporal(df, data):
    """
    Plota a série temporal destacando os períodos de treino, validação e teste usando Plotly.
    
    Parâmetros:
    - df: DataFrame com colunas 'date' e 'close'
    - data: dicionário com chaves 'treino', 'val', 'teste', cada valor é uma tupla
            (X, Y, P, I) onde I é uma lista/array de índices (posições) que delimitam
            o intervalo contínuo para aquele conjunto.
    Retorna:
    - fig: objeto plotly.graph_objects.Figure
    """
    fig = go.Figure()

    # 1. Série completa (fundo cinza)
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["close"],
        mode='lines',
        line=dict(color="#aaaab8", width=0.8),
        name="Série completa",
        showlegend=True,
        hoverinfo='skip'  # evita poluição no hover
    ))

    # 2. Para cada conjunto, adiciona o segmento colorido
    for key, (X, Y, P, I) in data.items():
        if key not in COLORS:
            continue

        # Garante que I seja um array/list de inteiros
        if isinstance(I, (list, np.ndarray)) and len(I) > 0:
            idx_min = int(min(I))
            idx_max = int(max(I))
            seg = df.iloc[idx_min:idx_max+1]
        else:
            # fallback (caso I seja algo como slice)
            seg = df.iloc[I[0]:I[-1]+1]

        # Adiciona o segmento com a cor correspondente
        fig.add_trace(go.Scatter(
            x=seg["date"],
            y=seg["close"],
            mode='lines',
            line=dict(color=COLORS[key], width=1.3),
            name=LABELS.get(key, key),
            showlegend=True
        ))

    # 3. Ajustes do layout
    fig.update_layout(
        title=dict(
            text="Divisão temporal — Treino / Validação / Teste",
            font=dict(size=12),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='lightgray'
        ),
        yaxis=dict(
            title="US$/oz",
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False,
            showline=True,
            linecolor='lightgray'
        ),
        legend=dict(
            font=dict(size=10),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        height=400,
        width=900,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor='white',
        hovermode='x unified'
    )

    return fig