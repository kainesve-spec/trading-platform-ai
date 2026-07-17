"""Page de gestion du risque."""

import streamlit as st
import pandas as pd
from portfolio.risk_manager import RiskManager
from config import DEFAULT_CAPITAL, DEFAULT_RISK_PERCENT

st.set_page_config(
    page_title="Risk Management",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ Gestion du Risque")

st.markdown("Calculez automatiquement votre dimensionnement de position et votre stop loss.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Calculateur de Position Size")
    capital = st.number_input(
    "Capital",
    value=float(DEFAULT_CAPITAL),
    min_value=100.0,
    step=100.0
    )
    risk_percent = st.slider("Risque (%)", 0.1, 10.0, DEFAULT_RISK_PERCENT, 0.1)
    entry_price = st.number_input("Prix d'entrée", value=150.0, min_value=0.01)
    stop_loss = st.number_input("Stop Loss", value=140.0, min_value=0.01)
    
    if st.button("Calculer", use_container_width=True):
        result = RiskManager.calculate_position_size(capital, risk_percent, entry_price, stop_loss)
        
        if "error" not in result:
            st.success("✅ Calcul effectué")
            st.metric("Quantité", int(result['quantity']))
            st.metric("Risque Montant", f"${result['risk_amount']:.2f}")
            st.metric("Risque %", f"{result['risk_percent']:.2f}%")
        else:
            st.error(result['error'])

with col2:
    st.subheader("🎯 Calculateur Take Profit")
    
    entry_price2 = st.number_input("Prix d'entrée", value=150.0, min_value=0.01, key="tp_entry")
    stop_loss2 = st.number_input("Stop Loss", value=140.0, min_value=0.01, key="tp_sl")
    rr_ratio = st.slider("Ratio Risk/Reward", 1.0, 5.0, 2.0, 0.1)
    
    if st.button("Calculer TP", use_container_width=True):
        tp = RiskManager.calculate_take_profit(entry_price2, stop_loss2, rr_ratio)
        st.metric("Take Profit", f"${tp:.2f}")
        st.metric("Profit Potentiel", f"${(tp - entry_price2):.2f}")

st.divider()

st.subheader("📈 Kelly Criterion")

col1, col2, col3 = st.columns(3)

with col1:
    win_rate = st.slider("Win Rate (%)", 10.0, 90.0, 50.0, 1.0)

with col2:
    avg_win = st.number_input("Gain Moyen", value=150.0)

with col3:
    avg_loss = st.number_input("Perte Moyenne", value=100.0)

if st.button("Calculer Kelly", use_container_width=True):
    kelly = RiskManager.calculate_kelly_criterion(win_rate/100, avg_win, avg_loss)
    st.info(f"🎯 Kelly Criterion: {kelly*100:.1f}% du capital par trade")
    st.warning("Conseil: Utilisez 25-50% du Kelly pour la prudence.")

st.divider()

st.subheader("⚖️ Métriques de Risque")

st.info("""
**Volatilité**: Mesure les fluctuations du prix
**Sharpe Ratio**: Rendement ajusté au risque
**VaR (Value at Risk)**: Perte potentielle maximale
**CVaR**: Perte moyenne en cas de scénario extrême
""")
