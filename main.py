import streamlit as st
import pandas as pd
import numpy as np
from utils import organizar_df, df_logreturn, _sinal_atual,plot_indicadores_tecnicos, plot_drawdown_ano,plot_drawdown_serie,plot_divisao_temporal, LOOKBACK, GAP,RSI_OS,RSI_OB, BB_OB,BB_OS


df = organizar_df('data/gold_features.csv')
n = len(df)
i1, i2 = int(n * 0.70), int(n * 0.85)
data = {
    "treino": (None, None, None, np.arange(0, i1)),
    "val":    (None, None, None, np.arange(i1 + GAP + LOOKBACK, i2)),
    "teste":  (None, None, None, np.arange(i2 + GAP + LOOKBACK, n))
}

st.set_page_config(page_title="Dashboard Ouro", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: #ffffff;
            padding-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        .stMainBlockContainer{
        padding-bottom: 3rem;
        }
    <\style>
    """, unsafe_allow_html = True
)



def main():
    st.header("Dashboard de Informações Gerais do Ouro")
    st.markdown("---")
    #st.write("Este dashboard apresenta informações gerais sobre os dados do ouro, incluindo estatísticas descritivas, visualizações e insights relevantes.")

    def latest_valid_value(dataframe, column_name):
        if column_name not in dataframe.columns:
            return None
        series = dataframe[column_name].dropna()
        if series.empty:
            return None
        return float(series.iloc[-1])

    def format_metric(value, is_percent=False):
        if value is None:
            return "N/A"
        if is_percent:
            return f"{value * 100:.2f}%"
        return f"{value:.4f}"


  

    initial_row = df.iloc[0]
    last_row = df.iloc[-1]

    card1, card2 = st.columns(2)

    with card1:
        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #d1d5db; border-radius:14px; padding:12px 14px; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
                <div style="font-size:0.78rem; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px;">Preço inicial</div>
                <div style="font-size:1.35rem; font-weight:700; color:#111827; line-height:1;">US$ {initial_row['close']}</div>
                <div style="font-size:0.82rem; margin-top:4px;">{initial_row['date']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with card2:
        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #d1d5db; border-radius:14px; padding:12px 14px; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
                <div style="font-size:0.78rem; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:4px;">Preço final</div>
                <div style="font-size:1.35rem; font-weight:700; color:#111827; line-height:1;">US$ {last_row['close']}</div>
                <div style="font-size:0.82rem; margin-top:4px;">{last_row['date']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='padding-bottom: 12px;'></div>", unsafe_allow_html=True)


    # colunas (?) 
    st1,st2 = st.columns(2)

    def _downsample(_df_in, rule="W", agg="last"):
        """Reduz pontos para visualização. rule='W' = semanal (~80% menos pontos)."""
        resampler = _df_in.resample(rule)
        return resampler.last().dropna() if agg == "last" else resampler.mean().dropna()

    with st1:
        with st.expander("Informações gerais"):
            tab1, tab2, tab3 = st.tabs(["Série bruta", "Momentum", "-"])

            with tab1:
                chart_df = df[["date", "close"]].copy()
                chart_df["date"] = pd.to_datetime(chart_df["date"])
                chart_df = chart_df.set_index("date")
                # Define altura fixa (ex: 400px)
                st.line_chart(_downsample(chart_df[["close"]]), height=400)

            with tab2:
                logreturn = df_logreturn(df)
                selected_log_return = st.radio(
                    "Velocidade que o preço mudou nos últimos dias",
                    options=["log 1", "log 5", "log 21"],
                    horizontal=True,
                )
                log_return_map = {
                    "log 1": "log_ret_1",
                    "log 5": "log_ret_5",
                    "log 21": "log_ret_21",
                }
                col = log_return_map[selected_log_return]
                st.line_chart(_downsample(logreturn[[col]], agg="mean"), y=col, height=400)

    with st2:
        with st.expander("Split"):
            sectab1, sectab2 = st.tabs(["Divisão Temporal", "---"])
            with sectab1:
                #st.subheader("Divisão temporal dos dados")
                fig = plot_divisao_temporal(df, data)   # retorna go.Figure
                #fig.update_layout(height=490)           # mesma altura
                st.plotly_chart(fig, width='stretch')
                #st.caption("Treino (azul) | Validação (laranja) | Teste (vermelho)")

            with sectab2:
                pass

    st.markdown("---")
    st.markdown("## Indicadores: ")
    anos_disponiveis = sorted(pd.to_datetime(df["date"]).dt.year.unique().tolist())
    ano_selecionado = st.select_slider(
        "Selecione o ano",
        options = anos_disponiveis,
        value = anos_disponiveis[-1],
    )

    mask = pd.to_datetime(df["date"]).dt.year == ano_selecionado
    df_ano = df[mask][["date","close","rsi","boll_b","macd_hist"]].copy()
    df_ano["date"] = pd.to_datetime(df_ano["date"])
    df_ano = df_ano.set_index("date").dropna()

    if df_ano.empty:
        st.warning(f"Sem dados para {ano_selecionado}")
    else:
        ultimo = df_ano.iloc[-1]
        col1,col2,col3 = st.columns(3)

        with col1:
            st.metric("RSI", f"{ultimo['rsi']:.3f}", _sinal_atual(ultimo["rsi"], RSI_OB, RSI_OS))
        
        with col2:
            st.metric("Bollinger %B", f"{ultimo['boll_b']:.3f}", _sinal_atual(ultimo["boll_b"],BB_OB, BB_OS))
        
        with col3:
            mv = ultimo["macd_hist"]
            st.metric("MACD Hist.", f"{mv:.5f}",delta = round(mv, 5), delta_color = "normal")


        st.plotly_chart(plot_indicadores_tecnicos(df_ano), width='stretch')

        st.caption(
            f" {df_ano.index[0].strftime('%d/%m/%Y')} → {df_ano.index[-1].strftime('%d/%m/%Y')}  •  "
            f"{len(df_ano)} pregões  --  "
            " Sobrecompra > +0.40  --   Sobrevenda < −0.40"
        )
    st.markdown("---")
    st.subheader("Períodos de crise")
    
    #st.markdown("## Risco — Drawdown 252 dias")

    dd_tab1, dd_tab2 = st.tabs(["Série completa", "Por ano"])

    # Prepara o df completo com DatetimeIndex uma única vez
    df_dd = df[["date", "drawdown_252"]].copy()
    df_dd["date"] = pd.to_datetime(df_dd["date"])
    df_dd = df_dd.set_index("date").dropna()

    with dd_tab1:
        # Card com o pior drawdown histórico
        pior_hist = df_dd["drawdown_252"].min()
        data_pior = df_dd["drawdown_252"].idxmin()
        atual_dd  = df_dd["drawdown_252"].iloc[-1]

        dd_c1, dd_c2, dd_c3 = st.columns(3)
        with dd_c1:
            st.metric("Drawdown atual", f"{atual_dd:.2%}")
        with dd_c2:
            st.metric("Pior histórico", f"{pior_hist:.2%}",
                    delta=f"{data_pior.strftime('%d/%m/%Y')}",
                    delta_color="off")
        with dd_c3:
            dias_severo = (df_dd["drawdown_252"] < -0.20).sum()
            pct_severo  = dias_severo / len(df_dd)
            st.metric("Dias em zona severa", f"{dias_severo}",
                    delta=f"{pct_severo:.1%} do período",
                    delta_color="off")

        st.plotly_chart(plot_drawdown_serie(df_dd), width='stretch')
        st.caption("Drawdown máximo janela de 252 pregões (≈ 1 ano)  •  "
                " Atenção < −10%  •   Severo < −20%")

    with dd_tab2:
        anos_dd = sorted(df_dd.index.year.unique().tolist())
        ano_dd  = st.select_slider("Ano", options=anos_dd, value=anos_dd[-1],
                                    key="slider_dd")

        df_dd_ano = df_dd[df_dd.index.year == ano_dd]

        if df_dd_ano.empty:
            st.warning(f"Sem dados para {ano_dd}.")
        else:
            pior_ano  = df_dd_ano["drawdown_252"].min()
            media_ano = df_dd_ano["drawdown_252"].mean()
            nivel     = " Severo" if pior_ano < -0.20 else " Atenção" if pior_ano < -0.10 else " Normal"

            an_c1, an_c2, an_c3 = st.columns(3)
            with an_c1:
                st.metric("Pior drawdown do ano", f"{pior_ano:.2%}",
                        delta=round(pior_ano, 4), delta_color="normal")
            with an_c2:
                st.metric("Drawdown médio", f"{media_ano:.2%}")
            with an_c3:
                st.metric("Nível de risco", nivel)

            st.plotly_chart(plot_drawdown_ano(df_dd_ano), width='stretch')




    st.markdown("---")
    # botão do kaggle: 
    st.markdown(
    """
    <div style="display:flex; justify-content:center; margin-top:5px;">
            <a href="https://www.kaggle.com/datasets/romanfonel/precious-metals-history-since-2000-with-news" target="_blank"
            style="display:flex; align-items:center; gap:0.4rem; text-decoration:none;
                color:#6b7280; font-size:0.85rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Dataset extraído do Kaggle
            </a>
        </div>
    """,
    unsafe_allow_html=True)
    #####################################################



if __name__ == "__main__":
    main()

