"""
Page Signal Engine
Trading AI Platform V2
"""

import streamlit as st

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


# ============================
# CONFIGURATION
# ============================

with st.sidebar:

    st.header("Configuration")


    symbol = st.selectbox(
        "Symbole",
        POPULAR_SYMBOLS,
        index=0
    )


    period = st.selectbox(
        "Période",
        PERIODS.keys(),
        format_func=lambda x: PERIODS[x],
        index=3
    )


    generate = st.button(
        "Générer Signal",
        use_container_width=True
    )



if "signal_symbol" not in st.session_state:

    st.session_state.signal_symbol = DEFAULT_SYMBOL


if "signal_period" not in st.session_state:

    st.session_state.signal_period = DEFAULT_PERIOD



if generate:

    st.session_state.signal_symbol = symbol

    st.session_state.signal_period = period



# ============================
# CHARGEMENT DONNEES
# ============================

with st.spinner("Analyse en cours..."):


    df = load_data(
        st.session_state.signal_symbol,
        period=st.session_state.signal_period,
        interval="1d"
    )


    if df is None or df.empty:

        st.error(
            "Impossible de charger les données."
        )

        st.stop()



    # ============================
    # INDICATEURS
    # ============================

    try:

        df = TechnicalIndicators.add_all_indicators(df)


    except Exception as e:

        st.error(
            f"Erreur indicateurs : {e}"
        )

        st.stop()



    # ============================
    # DEBUG COMPLET
    # ============================

    with st.expander(
        "🔎 Debug Signal Engine",
        expanded=False
    ):


        st.write(
            "Dimension :",
            df.shape
        )


        st.write(
            "Colonnes :"
        )


        st.write(
            df.columns.tolist()
        )


        st.dataframe(
            df.tail(3)
        )



    # ============================
    # IA
    # ============================

    ai_pred = None


    try:

        ai_engine = AIEngine()


        ai_engine.train_models(
            df,
            st.session_state.signal_symbol
        )


        ai_pred = ai_engine.predict(df)



    except Exception as e:


        st.warning(
            f"IA indisponible : {e}"
        )



    # ============================
    # SIGNAL ENGINE
    # ============================


    engine = SignalEngine()


    signal = engine.generate_signal(
        df,
        ai_prediction=ai_pred
    )



# ============================
# RESULTATS
# ============================


st.subheader(
    f"{signal['emoji']} {signal['signal']}"
)



c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Conviction",
        f"{signal['conviction']}/100"
    )


with c2:

    st.metric(
        "Technique",
        f"{signal['technical_score']}/40"
    )


with c3:

    st.metric(
        "IA",
        f"{signal['ai_score']}/30"
    )


with c4:

    st.metric(
        "Tendance",
        f"{signal['trend_score']}/20"
    )



st.progress(
    signal["conviction"] / 100
)


st.caption(
    f"Conviction : {signal['conviction']}%"
)



# ============================
# ANALYSE
# ============================

st.divider()


st.subheader(
    "📊 Analyse Détaillée"
)


a1, a2 = st.columns(2)


with a1:

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



with a2:

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
        "### Risk Reward"
    )


    st.info(
        signal["analysis"].get(
            "risk_reward",
            "N/A"
        )
    )



# ============================
# RISQUE
# ============================

st.divider()


st.subheader(
    "🎯 Gestion du risque"
)



r1, r2, r3, r4 = st.columns(4)


r1.metric(
    "Entrée",
    signal["entry_price"]
)


r2.metric(
    "Stop Loss",
    signal["stop_loss"]
)


r3.metric(
    "Take Profit",
    signal["take_profit"]
)


r4.metric(
    "Ratio R/R",
    signal["rr_ratio"]
)



# ============================
# COMMENTAIRES
# ============================


st.subheader(
    "💬 Commentaires"
)


st.write(
    "•",
    signal.get(
        "comments",
        "Analyse terminée."
    )
)



if signal["direction"] == "BUY":

    st.success(
        f"✅ Achat - Conviction {signal['conviction']}%"
    )


elif signal["direction"] == "SELL":

    st.error(
        f"⛔ Vente - Conviction {signal['conviction']}%"
    )


else:

    st.warning(
        f"⏸️ Neutre - Conviction {signal['conviction']}%"
    )
        
