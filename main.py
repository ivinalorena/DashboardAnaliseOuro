import streamlit as st
import pandas as pd
from utils import organizar_df, df_logreturn, _sinal_atual,plot_indicadores_tecnicos
st.set_page_config(page_title="Dashboard de Informações Gerais do Ouro", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: #ffffff;
            padding-bottom: 24px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.header("Dashboard de Informações Gerais do Ouro")
    #st.markdown("---")
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


    df = organizar_df('data/gold_features.csv')

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
            tab1, tab2, tab3 = st.tabs(["Série bruta", "log-return", "-"])

            with tab1:
                chart_df = df[["date", "close"]].copy()
                chart_df["date"] = pd.to_datetime(chart_df["date"])
                chart_df = chart_df.set_index("date")

                st.line_chart(_downsample(chart_df[["close"]]))           # last() — preço de fechamento semanal

            with tab2:  
                logreturn = df_logreturn(df)
                selected_log_return = st.radio(
                    "Escolha a série",
                    options=["log 1", "log 5", "log 21"],
                    horizontal=True,
                )
                log_return_map = {
                    "log 1": "log_ret_1",
                    "log 5": "log_ret_5",
                    "log 21": "log_ret_21",
                }
                col = log_return_map[selected_log_return]
                st.line_chart(_downsample(logreturn[[col]], agg="mean"), y=col)  # mean() — média dos retornos na semana

    with st2:
        with st.expander("Saída esperada para 5, 15 e 30 dias"):
            sectab1, sectab2 = st.tabs(["Próximos dias", "---"])
            with sectab1:
                output_df = df[["date", "y_5", "y_15", "y_30"]].copy()
                output_df["date"] = pd.to_datetime(output_df["date"])
                output_df = output_df.set_index("date")

                selected_log_return_dias = st.radio(
                    "Resultado em dias",
                    options=["5 dias", "15 dias", "30 dias"],
                    horizontal=True,
                )
                log_return_map_dias = {
                    "5 dias": "y_5",
                    "15 dias": "y_15",
                    "30 dias": "y_30",
                }
                col_dias = log_return_map_dias[selected_log_return_dias]
                st.line_chart(_downsample(output_df[[col_dias]]), y=col_dias) 
    
    st.markdown("---")
    st.markdown("## Indicadores: ")
    #tab_indicadores = st.tabs(["Indicadores"])
    #with tab_indicadores:  
    RSI_OB,  RSI_OS  = 0.40, -0.40
    BB_OB,   BB_OS   = 0.40, -0.40
    ultimo = df[["rsi", "boll_b", "macd_hist"]].dropna().iloc[-1]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("RSI", f"{ultimo['rsi']:.3f}",
                _sinal_atual(ultimo["rsi"], RSI_OB, RSI_OS))
        #st.info("Mede a proporção de dias de alta vs. dias de baixa em uma janela")
    with col2:
        st.metric("Bollinger %B", f"{ultimo['boll_b']:.3f}",
                _sinal_atual(ultimo["boll_b"], BB_OB, BB_OS))
        #with st.expander("Interpretação"):
        #    st.info("Mostra onde o preço atual está em relação às bandas de desvio-padrão ao redor de uma média móvel.")
    with col3:
        macd_val = ultimo["macd_hist"]
        st.metric("MACD Hist.", f"{macd_val:.5f}",
                "Positivo" if macd_val > 0 else "Negativo")

    st.plotly_chart(plot_indicadores_tecnicos(df), use_container_width=True)

    st.caption(
        "Zona vermelha = sobrecompra (limiar ≈ +0.40)    "
        "Zona verde = sobrevenda (limiar ≈ −0.40)  "

        "Série amostrada semanalmente"
    )

        


    st.markdown("---")
    # botão do kaggle: 
    st.markdown(
    """
    <a href="https://www.kaggle.com/datasets/romanfonel/precious-metals-history-since-2000-with-news" target="_blank"
    style="display:center; align-items:center; gap:0.5rem; padding:0.55rem 0.9rem; border-radius:999px; text-decoration:none; color:#111827; font-weight:600; border:1px solid #bdbdbd; box-shadow:0 6px 18px rgba(0,0,0,0.08);">
        <span style="font-size:1rem;">Dataset extraído de Kaggle</span>
        <span style="background:rgba(17,24,39,0.08); padding:0.2rem 0.55rem; border-radius:999px; font-size:0.78rem; letter-spacing:0.02em;">Abrir fonte</span>
    </a>
    """,
    unsafe_allow_html=True)
    #####################################################



if __name__ == "__main__":
    main()

