"""Dashboard principal de la plateforme."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.data_loader import load_data, validate_data
from utils.indicators import TechnicalIndicators
from config import DEFAULT_SYMBOL, DEFAULT_PERIOD, TIMEFRAMES, PERIODS, COLORS

st.set_page_config(
    page_title="Trading AI Platform - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Trading AI")
st.markdown("Plateforme complète d'aide à la décision pour le trading assisté par IA")

# Initialiser session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'current_symbol' not in st.session_state:
    st.session_state.current_symbol = DEFAULT_SYMBOL
if 'current_period' not in st.session_state:
    st.session_state.current_period = DEFAULT_PERIOD

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    symbol = st.text_input("Symbole", value=DEFAULT_SYMBOL).upper()
    period = st.selectbox("Période", options=PERIODS.keys(), format_func=lambda x: PERIODS[x])
    
    if st.button("📥 Charger les données", use_container_width=True):
        with st.spinner("Chargement..."):
            df = load_data(symbol, period=period, interval="1d")
            if df is not None:
                df = TechnicalIndicators.add_all_indicators(df)
                st.session_state.data = df
                st.session_state.current_symbol = symbol
                st.success(f"✅ {len(df)} candles chargées")
            else:
                st.error("❌ Erreur lors du chargement")

# Affichage principal
if st.session_state.data is not None:
    df = st.session_state.data
    
    # Validation des données
    is_valid, validation_msg = validate_data(df)
    
    if is_valid:
        st.success(validation_msg)
        
        # Métriques principales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            price = df['close'].iloc[-1]
            st.metric("Prix Actuel", f"${price:.2f}")
        
        with col2:
            change = df['close'].iloc[-1] - df['close'].iloc[-5]
            change_pct = (change / df['close'].iloc[-5]) * 100
            st.metric("Changement 5j", f"{change_pct:.2f}%")
        
        with col3:
            vol = df['volume'].iloc[-1]
            st.metric("Volume", f"{vol/1e6:.1f}M")
        
        with col4:
            if 'RSI' in df.columns:
                rsi = df['RSI'].iloc[-1]
                st.metric("RSI", f"{rsi:.1f}")
        
        with col5:
            if 'ADX' in df.columns:
                adx = df['ADX'].iloc[-1]
                st.metric("ADX", f"{adx:.1f}")
        
        st.divider()
        
        # Graphique principal OHLCV
        st.subheader("📈 Graphique OHLCV")
        
        fig = go.Figure()
        
        # Bougies
        fig.add_trace(go.Candlestick(
            x=df.index if 'date' not in df.columns else df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLCV'
        ))
        
        # Moyennes mobiles
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index if 'date' not in df.columns else df['date'],
                y=df['SMA_20'],
                name='SMA 20',
                line=dict(color='blue', width=1)
            ))
        
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index if 'date' not in df.columns else df['date'],
                y=df['SMA_50'],
                name='SMA 50',
                line=dict(color='red', width=1)
            ))
        
        fig.update_layout(
            title=f"{st.session_state.current_symbol} - Graphique OHLC",
            xaxis_title="Date",
            yaxis_title="Prix",
            template="plotly_dark",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Indicateurs techniques en onglets
        st.subheader("📊 Indicateurs Techniques")
        
        tab1, tab2, tab3, tab4 = st.tabs(["RSI", "MACD", "Bollinger", "Volume"])
        
        with tab1:
            if 'RSI' in df.columns:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=df.index if 'date' not in df.columns else df['date'],
                    y=df['RSI'],
                    name='RSI',
                    line=dict(color='purple')
                ))
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Suracheté")
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Survendu")
                fig_rsi.update_layout(title="RSI (14)", xaxis_title="Date", yaxis_title="RSI", template="plotly_dark", height=400)
                st.plotly_chart(fig_rsi, use_container_width=True)
        
        with tab2:
            if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(
                    x=df.index if 'date' not in df.columns else df['date'],
                    y=df['MACD'],
                    name='MACD',
                    line=dict(color='blue')
                ))
                fig_macd.add_trace(go.Scatter(
                    x=df.index if 'date' not in df.columns else df['date'],
                    y=df['MACD_Signal'],
                    name='Signal',
                    line=dict(color='red')
                ))
                if 'MACD_Hist' in df.columns:
                    fig_macd.add_trace(go.Bar(
                        x=df.index if 'date' not in df.columns else df['date'],
                        y=df['MACD_Hist'],
                        name='Historique',
                        marker_color='gray'
                    ))
                fig_macd.update_layout(title="MACD", xaxis_title="Date", yaxis_title="MACD", template="plotly_dark", height=400)
                st.plotly_chart(fig_macd, use_container_width=True)
        
        with tab3:
            if 'BB_High' in df.columns and 'BB_Low' in df.columns:
                fig_bb = go.Figure()
                fig_bb.add_trace(go.Scatter(
                    x=df.index if 'date' not in df.columns else df['date'],
                    y=df['close'],
                    name='Close',
                    line=dict(color='black')
                ))
                fig_bb.add_trace(go.Scatter(
                    x=df.index if 'date' not in df.columns else df['date'],
                    y=df['BB_High'],
                    name='BB High',
                    line=dict(color='blue')
                ))
                fig_bb.add_trace(go.Scatter(
                    x=df.index if 'date' not in df.columns else df['date'],
                    y=df['BB_Low'],
                    name='BB Low',
                    line=dict(color='red')
                ))
                fig_bb.update_layout(title="Bandes de Bollinger", xaxis_title="Date", yaxis_title="Prix", template="plotly_dark", height=400)
                st.plotly_chart(fig_bb, use_container_width=True)
        
        with tab4:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(
                x=df.index if 'date' not in df.columns else df['date'],
                y=df['volume'],
                name='Volume',
                marker_color='steelblue'
            ))
            fig_vol.update_layout(title="Volume", xaxis_title="Date", yaxis_title="Volume", template="plotly_dark", height=400)
            st.plotly_chart(fig_vol, use_container_width=True)
        
    else:
        st.error(validation_msg)

else:
    st.info("👈 Sélectionnez un symbole et chargez les données")
