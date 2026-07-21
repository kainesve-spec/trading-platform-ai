"""Page du Signal Engine."""

import streamlit as st
import pandas as pd

from utils.data_loader import load_data
from utils.indicators import TechnicalIndicators
from signals.signal_engine import SignalEngine
from models.ai_engine import AIEngine
from config import DEFAULT_SYMBOL, DEFAULT_PERIOD, POPULAR_SYMBOLS, PERIODS


st.set_page_config(
    page_title="Signal Engine",
    page_icon="🎯",
    layout="wide"
)


st.title("🎯 Signal Engine - Score de Conviction 0-100")


with st.sidebar:
    st.header("Configuration")

    symbol = st.selectbox(
        "Symbole",
        options=POPULAR_SYMBOLS,
        index=0
    )

    period = st.selectbox(
        "Période",
        options=PERIODS.keys(),
        format_func=lambda x: PERIODS[x],
        index=3
    )

    if st.button(
        "Générer Signal",
        use_container_width=True
    ):
        st.session_state.signal_symbol = symbol
        st.session_state.signal_period = period


if "signal_symbol" not in st.session_state:
    st.session_state.signal_symbol = DEFAULT_SYMBOL

if "signal_period" not in st.session_state:
    st.session_state.signal_period = DEFAULT_PERIOD


with st.spinner("Analyse en cours..."):

    df = load_data(
        st.session_state.signal_symbol,
        period=st.session_state.signal_period,
        interval="1d"
    )

    if df is not None and not df.empty:

        df = TechnicalIndicators.add_all_indicators(df)

        try:

            # Analyse IA
            ai_engine = AIEngine()

            ai_engine.train_models(
                df,
                st.session_state.signal_symbol
            )

            ai_pred = ai_engine.predict(df)

        except Exception:

            ai_pred = None


        # Génération signal
        signal_engine = SignalEngine()

        signal = signal_engine.generate_signal(
            df,
            ai_prediction=ai_pred
        )


        # Affichage principal

        st.subheader(
            f"Signal : {signal['emoji']} {signal['signal']}"
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:
            st.metric(
                "Conviction",
                f"{signal['conviction']:.0f}/100"
            )


        with col2:
            st.metric(
                "Technique",
                f"{signal['technical_score']:.0f}/40"
            )


        with col3:
            st.metric(
                "IA",
                f"{signal['ai_score']:.0f}/30"
            )


        with col4:
            st.metric(
                "Tendance",
                f"{signal['trend_score']:.0f}/20"
            )


        st.progress(
            int(signal["conviction"]),
            text=f"Conviction : {signal['conviction']:.1f}%"
        )


        st.divider()


        # Analyse détaillée

        st.subheader("📊 Analyse Détaillée")


        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                "### Analyse Technique"
            )

            st.info(
                signal["analysis"].get(
                    "technical",
                    "N/A"
                )
            )


            st.markdown(
                "### Tendance"
            )

            st.info(
                signal["analysis"].get(
                    "trend",
                    "N/A"
                )
            )


        with col2:

            st.markdown(
                "### Prédiction IA"
            )

            st.info(
                signal["analysis"].get(
                    "ai",
                    "N/A"
                )
            )


            st.markdown(
                "### Risk / Reward"
            )

            st.info(
                signal["analysis"].get(
                    "risk_reward",
                    "N/A"
                )
            )


        # Risk Management

        st.subheader("🎯 Gestion du risque")


        col1, col2, col3, col4 = st.columns(4)


        with col1:
            st.metric(
                "Entrée",
                str(signal["entry_price"])
            )

        with col2:
            st.metric(
                "Stop Loss",
                str(signal["stop_loss"])
            )

        with col3:
            st.metric(
                "Take Profit",
                str(signal["take_profit"])
            )

        with col4:
            st.metric(
                "Ratio R/R",
                str(signal["rr_ratio"])
            )


        # Commentaires

            st.subheader("💬 Commentaires")

            comments = signal.get(
               "comments",
               "Aucun commentaire disponible."
            )

            st.write(
                  f"• {comments}"
            )


           st.divider()


        # Actions

        if signal["direction"] == "BUY":

            st.success(
                f"✅ Signal ACHAT - Conviction {signal['conviction']:.0f}%"
            )

            if st.button(
                "📥 Ajouter au Portfolio",
                use_container_width=True
            ):

                st.success(
                    "Position ajoutée au portfolio"
                )


        elif signal["direction"] == "SELL":

            st.error(
                f"⛔ Signal VENTE - Conviction {signal['conviction']:.0f}%"
            )

            if st.button(
                "📤 Vendre Position",
                use_container_width=True
            ):

                st.success(
                    "Position vendue"
                )


        else:

            st.warning(
                f"⏸️ Signal neutre - Conviction {signal['conviction']:.0f}%"
            )


    else:

        st.error(
            "Erreur lors du chargement des données"
        )
