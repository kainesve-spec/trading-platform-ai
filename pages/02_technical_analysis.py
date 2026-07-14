"""Page d'analyse technique avancée."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data, validate_data
from utils.indicators import TechnicalIndicators
from config import DEFAULT_SYMBOL, DEFAULT_PERIOD, PERIODS, POPULAR_SYMBOLS

st.set_page_config(
    page_title="Analyse Technique",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Analyse Technique Avancée")

with st.sidebar:
    st.header("Configuration")
    symbol = st.selectbox("Symbole", options=POPULAR_SYMBOLS, index=0)
    period = st.selectbox("Période", options=PERIODS.keys(), format_func=lambda x: PERIODS[x], index=3)
    
    if st.button("Charger", use_container_width=True):
        st.session_state.analysis_symbol = symbol
        st.session_state.analysis_period = period

if 'analysis_symbol' not in st.session_state:
    st.session_state.analysis_symbol = DEFAULT_SYMBOL
if 'analysis_period' not in st.session_state:
    st.session_state.analysis_period = DEFAULT_PERIOD

with st.spinner("Chargement..."):
    df = load_data(st.session_state.analysis_symbol, period=st.session_state.analysis_period, interval="1d")
    
    if df is not None:
        df = TechnicalIndicators.add_all_indicators(df)
        
        is_valid, msg = validate_data(df)
        if is_valid:
            st.success(msg)
            
            # Sélection des indicateurs
            col1, col2, col3 = st.columns(3)
            with col1:
                show_rsi = st.checkbox("RSI", value=True)
                show_atr = st.checkbox("ATR", value=True)
            with col2:
                show_macd = st.checkbox("MACD", value=True)
                show_adx = st.checkbox("ADX", value=True)
            with col3:
                show_stoch = st.checkbox("Stochastique", value=False)
                show_obv = st.checkbox("OBV", value=False)
            
            # Affichage des statistiques
            st.subheader("📊 Résumé")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Prix Actuel", f"${df['close'].iloc[-1]:.2f}")
            with col2:
                if 'RSI' in df.columns:
                    st.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
            with col3:
                if 'ADX' in df.columns:
                    st.metric("ADX", f"{df['ADX'].iloc[-1]:.1f}")
            with col4:
                st.metric("Volatilité", f"{df['close'].pct_change().std()*100:.2f}%")
            
            # Graphiques détaillés
            if show_rsi and 'RSI' in df.columns:
                st.subheader("RSI (Relative Strength Index)")
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=df['RSI'], name='RSI', line=dict(color='purple')))
                fig.add_hline(y=30, line_dash="dash", line_color="red")
                fig.add_hline(y=70, line_dash="dash", line_color="green")
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            if show_macd and 'MACD' in df.columns:
                st.subheader("MACD (Moving Average Convergence Divergence)")
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=df['MACD'], name='MACD', line=dict(color='blue')))
                fig.add_trace(go.Scatter(y=df['MACD_Signal'], name='Signal', line=dict(color='red')))
                fig.add_trace(go.Bar(y=df['MACD_Hist'], name='Hist', marker_color='gray'))
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            if show_atr and 'ATR' in df.columns:
                st.subheader("ATR (Average True Range)")
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=df['ATR'], name='ATR', line=dict(color='orange')))
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            if show_adx and 'ADX' in df.columns:
                st.subheader("ADX (Average Directional Index)")
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=df['ADX'], name='ADX', line=dict(color='green')))
                fig.add_hline(y=25, line_dash="dash", line_color="orange", annotation_text="Seuil tendance")
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            if show_stoch and 'Stoch_K' in df.columns:
                st.subheader("Stochastique")
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=df['Stoch_K'], name='K', line=dict(color='blue')))
                fig.add_trace(go.Scatter(y=df['Stoch_D'], name='D', line=dict(color='red')))
                fig.add_hline(y=20, line_dash="dash", line_color="red")
                fig.add_hline(y=80, line_dash="dash", line_color="green")
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            if show_obv and 'OBV' in df.columns:
                st.subheader("OBV (On-Balance Volume)")
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=df['OBV'], name='OBV', line=dict(color='cyan')))
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(msg)
    else:
        st.error("Erreur lors du chargement des données")
