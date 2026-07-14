"""Page de backtesting."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data
from utils.indicators import TechnicalIndicators
from backtests.engine import BacktestEngine
from config import DEFAULT_SYMBOL, DEFAULT_PERIOD, PERIODS, POPULAR_SYMBOLS, BACKTEST_STRATEGIES

st.set_page_config(
    page_title="Backtesting",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Backtesting Engine")

with st.sidebar:
    st.header("Configuration Backtest")
    symbol = st.selectbox("Symbole", options=POPULAR_SYMBOLS)
    period = st.selectbox("Période", options=PERIODS.keys(), format_func=lambda x: PERIODS[x], index=4)
    strategies = st.multiselect("Stratégies", BACKTEST_STRATEGIES, default=["RSI", "MACD"])
    capital = st.number_input("Capital Initial", value=10000, min_value=100)
    commission = st.slider("Commission (%)", 0.0, 1.0, 0.1, 0.01)
    
    if st.button("Lancer Backtest", use_container_width=True):
        st.session_state.bt_symbol = symbol
        st.session_state.bt_period = period
        st.session_state.bt_strategies = strategies
        st.session_state.bt_capital = capital
        st.session_state.bt_commission = commission / 100

if 'bt_symbol' not in st.session_state:
    st.session_state.bt_symbol = DEFAULT_SYMBOL
if 'bt_period' not in st.session_state:
    st.session_state.bt_period = DEFAULT_PERIOD
if 'bt_strategies' not in st.session_state:
    st.session_state.bt_strategies = ["RSI"]
if 'bt_capital' not in st.session_state:
    st.session_state.bt_capital = 10000
if 'bt_commission' not in st.session_state:
    st.session_state.bt_commission = 0.001

with st.spinner("Backtesting en cours..."):
    df = load_data(st.session_state.bt_symbol, period=st.session_state.bt_period, interval="1d")
    
    if df is not None:
        df = TechnicalIndicators.add_all_indicators(df)
        
        engine = BacktestEngine(df, capital=st.session_state.bt_capital, commission=st.session_state.bt_commission)
        
        results = []
        for strategy in st.session_state.bt_strategies:
            result = engine.backtest_strategy(strategy)
            if "error" not in result:
                results.append(result)
        
        if results:
            # Résumé
            st.subheader("📊 Résumé des Backtests")
            
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True)
            
            # Graphique comparatif
            st.subheader("📈 Comparaison des Stratégies")
            
            fig = go.Figure()
            
            for idx, result in enumerate(results):
                fig.add_trace(go.Bar(
                    x=[f"Win Rate", f"Profit %", f"Profit Factor"],
                    y=[
                        result.get('win_rate', 0),
                        result.get('total_profit_pct', 0),
                        result.get('profit_factor', 0) * 10  # Scaled for visibility
                    ],
                    name=result.get('strategy', 'Unknown')
                ))
            
            fig.update_layout(template="plotly_dark", height=400, barmode="group")
            st.plotly_chart(fig, use_container_width=True)
            
            # Détails par stratégie
            st.subheader("🔍 Détails par Stratégie")
            
            for result in results:
                with st.expander(f"{result.get('strategy', 'Strategy')} - {result.get('trades', 0)} trades"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Trades", result.get('trades', 0))
                        st.metric("Wins", result.get('wins', 0))
                    
                    with col2:
                        st.metric("Losses", result.get('losses', 0))
                        st.metric("Win Rate", f"{result.get('win_rate', 0):.1f}%")
                    
                    with col3:
                        st.metric("Profit", f"${result.get('total_profit', 0):.2f}")
                        st.metric("Profit %", f"{result.get('total_profit_pct', 0):.2f}%")
                    
                    with col4:
                        st.metric("Profit Factor", f"{result.get('profit_factor', 0):.2f}")
                        st.metric("Avg Win", f"${result.get('avg_win', 0):.2f}")
        else:
            st.error("Aucun résultat de backtest")
    else:
        st.error("Erreur lors du chargement des données")
