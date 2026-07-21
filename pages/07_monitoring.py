"""Page de monitoring et alertes."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.indicators import TechnicalIndicators
from signals.signal_engine import SignalEngine
from models.ai_engine import AIEngine
from config import POPULAR_SYMBOLS


st.set_page_config(
    page_title="Monitoring",
    page_icon="📡",
    layout="wide"
)


st.title("📡 Monitoring & Alertes")
st.markdown("Monitoring en temps réel des prix et des indicateurs")


with st.sidebar:
    st.header("Configuration Watchlist")

    symbols = st.multiselect(
        "Sélectionnez les symboles",
        POPULAR_SYMBOLS,
        default=["AAPL", "MSFT", "GOOGL"]
    )

    refresh_interval = st.slider(
        "Intervalle de rafraîchissement (s)",
        5,
        300,
        60
    )


if not symbols:

    st.info("👈 Sélectionnez au moins un symbole")


else:

    st.subheader("📈 Watchlist")

    watchlist_data = []


    for symbol in symbols:

        try:

            df = load_data(
                symbol,
                period="5d",
                interval="1d"
            )


            if df is not None and not df.empty:

                latest_price = df["close"].iloc[-1]

                prev_price = (
                    df["close"].iloc[-2]
                    if len(df) > 1
                    else latest_price
                )


                change_pct = (
                    (latest_price - prev_price)
                    / prev_price
                    * 100
                    if prev_price > 0
                    else 0
                )


                volume = df["volume"].iloc[-1]


                watchlist_data.append({

                    "Symbole": symbol,
                    "Prix": f"${latest_price:.2f}",
                    "Changement": f"{change_pct:+.2f}%",
                    "Volume": f"{volume/1e6:.1f}M"

                })


        except Exception:

            pass


    if watchlist_data:

        df_watchlist = pd.DataFrame(watchlist_data)

        st.dataframe(
            df_watchlist,
            use_container_width=True
        )


    st.divider()

    st.subheader("📈 Détails")


    for symbol in symbols:


        with st.expander(f"📊 {symbol}"):


            df = load_data(
                symbol,
                period="1y",
                interval="1d"
            )


            if df is not None and not df.empty:


                df = TechnicalIndicators.add_all_indicators(df)


                col1, col2, col3, col4 = st.columns(4)


                with col1:

                    st.metric(
                        "Prix Actuel",
                        f"${df['close'].iloc[-1]:.2f}"
                    )


                with col2:

                    if "RSI" in df.columns:

                        st.metric(
                            "RSI",
                            f"{df['RSI'].iloc[-1]:.1f}"
                        )


                with col3:

                    if "ADX" in df.columns:

                        st.metric(
                            "ADX",
                            f"{df['ADX'].iloc[-1]:.1f}"
                        )


                with col4:

                    change_pct = (

                        (df['close'].iloc[-1] - df['close'].iloc[0])

                        / df['close'].iloc[0]

                        * 100

                    )


                    st.metric(
                        "Change 1Y",
                        f"{change_pct:+.2f}%"
                    )


                # ==========================
                # SIGNAL ENGINE
                # ==========================

                signal_result = SignalEngine.generate_signal(df)


                st.divider()

                st.subheader("📡 Signal IA")


                signal_col, score_col = st.columns(2)


                with signal_col:

                    st.metric(
                        "Direction",
                        f"{signal_result['emoji']} {signal_result['signal']}"
                    )


                with score_col:

                    st.metric(
                        "Conviction",
                        f"{signal_result['conviction']:.1f}/100"
                    )


                with st.expander("📄 Analyse du signal"):

                    for comment in signal_result.get("comments", []):

                        st.write(
                            "•",
                            comment
                        )


                # ==========================
                # GRAPHIQUE
                # ==========================

                fig = go.Figure()


                required_cols = [
                    "open",
                    "high",
                    "low",
                    "close"
                ]


                if not all(col in df.columns for col in required_cols):

                    st.warning("Données OHLC incomplètes")

                    continue


                df = df.dropna(
                    subset=required_cols
                )


                if df.empty:

                    st.warning(
                        "Pas assez de données pour afficher le graphique"
                    )

                    continue


                fig.add_trace(

                    go.Candlestick(

                        x=df.index.tolist(),

                        open=df["open"].tolist(),

                        high=df["high"].tolist(),

                        low=df["low"].tolist(),

                        close=df["close"].tolist(),

                        name="OHLC"

                    )

                )


                fig.update_layout(

                    template="plotly_dark",

                    height=300,

                    xaxis_rangeslider_visible=False

                )


                st.plotly_chart(

                    fig,

                    use_container_width=True

            )
