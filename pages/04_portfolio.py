"""Page de gestion du portefeuille."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from portfolio.manager import PortfolioManager
from config import DEFAULT_CAPITAL

st.set_page_config(
    page_title="Portfolio Manager",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Portfolio Manager")

# Initialiser le portfolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = PortfolioManager(DEFAULT_CAPITAL)

portfolio = st.session_state.portfolio

# Sidebar
with st.sidebar:
    st.header("⚙️ Gestion du Portfolio")
    
    tab1, tab2, tab3 = st.tabs(["Ajouter", "Fermer", "Config"])
    
    with tab1:
        st.subheader("Ajouter Position")
        symbol = st.text_input("Symbole", "AAPL").upper()
        quantity = st.number_input("Quantité", min_value=1, value=10)
        entry_price = st.number_input("Prix d'entrée", min_value=0.01, value=150.0)
        stop_loss = st.number_input("Stop Loss", min_value=0.01, value=140.0)
        take_profit = st.number_input("Take Profit", min_value=0.01, value=160.0)
        
        if st.button("Ajouter Position", use_container_width=True):
            if portfolio.add_position(symbol, quantity, entry_price, stop_loss, take_profit):
                st.success(f"✅ Position {symbol} ajoutée")
            else:
                st.error("❌ Erreur")
    
    with tab2:
        st.subheader("Fermer Position")
        open_pos = [p for p in portfolio.positions if p['status'] == 'OPEN']
        if open_pos:
            pos_list = [f"{p['symbol']} x{p['quantity']}" for p in open_pos]
            selected = st.selectbox("Position", pos_list)
            exit_price = st.number_input("Prix de sortie", min_value=0.01, value=150.0)
            
            if st.button("Fermer", use_container_width=True):
                idx = pos_list.index(selected)
                if portfolio.close_position(open_pos[idx]['id'], exit_price):
                    st.success("✅ Position fermée")
        else:
            st.info("Aucune position ouverte")
    
    with tab3:
        st.subheader("Configuration")
        new_capital = st.number_input("Capital Initial", value=DEFAULT_CAPITAL)
        if st.button("Mettre à jour", use_container_width=True):
            portfolio.initial_capital = new_capital
            st.success("✅ Capital mis à jour")

# Affichage principal
stats = portfolio.get_portfolio_stats()

if stats:
    st.subheader("📊 Statistiques Globales")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Capital Actuel", f"${stats.get('current_capital', 0):.2f}")
    
    with col2:
        st.metric("P/L Total", f"${stats.get('total_profit_loss', 0):.2f}")
    
    with col3:
        st.metric("P/L %", f"{stats.get('total_profit_loss_pct', 0):.2f}%")
    
    with col4:
        st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%")
    
    with col5:
        st.metric("Trades", f"{stats.get('closed_trades', 0)}")

st.divider()

# Positions ouvertes
st.subheader("📈 Positions Ouvertes")
open_positions = [p for p in portfolio.positions if p['status'] == 'OPEN']

if open_positions:
    df_open = pd.DataFrame(open_positions)[['symbol', 'quantity', 'entry_price', 'stop_loss', 'take_profit']]
    st.dataframe(df_open, use_container_width=True)
else:
    st.info("Aucune position ouverte")

st.divider()

# Historique des trades
st.subheader("📋 Historique des Trades")
if portfolio.trades_history:
    df_trades = pd.DataFrame(portfolio.trades_history)[['symbol', 'quantity', 'entry_price', 'exit_price', 'profit_loss', 'profit_loss_pct']]
    st.dataframe(df_trades, use_container_width=True)
    
    # Export
    csv = df_trades.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name="trades_history.csv",
        mime="text/csv"
    )
else:
    st.info("Aucun historique de trade")
