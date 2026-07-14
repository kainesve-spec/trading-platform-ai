"""Page de validation et qualité des données."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data, validate_data, get_data_quality_score
from config import DEFAULT_SYMBOL, POPULAR_SYMBOLS

st.set_page_config(
    page_title="Data Validation",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Validation des Données")

with st.sidebar:
    st.header("Configuration")
    symbol = st.selectbox("Symbole", options=POPULAR_SYMBOLS)
    
    if st.button("Vérifier", use_container_width=True):
        st.session_state.validation_symbol = symbol

if 'validation_symbol' not in st.session_state:
    st.session_state.validation_symbol = DEFAULT_SYMBOL

df = load_data(st.session_state.validation_symbol, period="1y", interval="1d")

if df is not None and not df.empty:
    # Validation
    is_valid, msg = validate_data(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Résumé de Validation")
        st.write(msg)
        
        # Score de qualité
        quality_score = get_data_quality_score(df)
        st.metric("Score Qualité", f"{quality_score:.1f}/100")
        st.progress(quality_score / 100)
    
    with col2:
        st.subheader("📈 Statistiques")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("Nombre de candles", len(df))
            st.metric("Colonnes", len(df.columns))
        
        with col_b:
            st.metric("Doublons", df.duplicated().sum())
            st.metric("NaN", df.isna().sum().sum())
    
    st.divider()
    
    # Détails des colonnes
    st.subheader("📄 Inspection des Colonnes")
    
    for col in df.columns:
        with st.expander(f"Colonne: {col}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Type", str(df[col].dtype))
            with col2:
                st.metric("Non-Null", df[col].notna().sum())
            with col3:
                st.metric("Null", df[col].isna().sum())
            with col4:
                st.metric("Uniques", df[col].nunique())
            
            if df[col].dtype != 'object':
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Min", f"{df[col].min():.4f}")
                with col_b:
                    st.metric("Moyen", f"{df[col].mean():.4f}")
                with col_c:
                    st.metric("Max", f"{df[col].max():.4f}")
    
    st.divider()
    
    # Anomalies
    st.subheader("⚠️ Détection d'Anomalies")
    
    anomalies = []
    
    # Vérifier OHLC
    if all(col in df.columns for col in ['high', 'low', 'close', 'open']):
        invalid_ohlc = ((df['high'] < df['low']) | 
                       (df['high'] < df['close']) | 
                       (df['high'] < df['open'])).sum()
        if invalid_ohlc > 0:
            anomalies.append(f"❌ {invalid_ohlc} candles avec OHLC invalide")
    
    # Vérifier les prix négatifs
    if 'close' in df.columns:
        negative_prices = (df['close'] < 0).sum()
        if negative_prices > 0:
            anomalies.append(f"❌ {negative_prices} prix négatifs")
    
    # Vérifier les volumes manquants
    if 'volume' in df.columns:
        zero_volumes = (df['volume'] == 0).sum()
        if zero_volumes > 0:
            anomalies.append(f"❌ {zero_volumes} candles avec volume zéro")
    
    # Vérifier les valeurs infinies
    inf_count = df.isin([float('inf'), float('-inf')]).sum().sum()
    if inf_count > 0:
        anomalies.append(f"❌ {inf_count} valeurs infinies")
    
    if anomalies:
        for anomaly in anomalies:
            st.error(anomaly)
    else:
        st.success("✅ Aucune anomalie détectée")
    
    st.divider()
    
    # Affichage des données brutes
    st.subheader("📄 Aperçu des Données")
    st.dataframe(df.tail(10), use_container_width=True)
    
    # Export
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name=f"{st.session_state.validation_symbol}_data.csv",
        mime="text/csv"
    )
else:
    st.error("Erreur lors du chargement des données")
