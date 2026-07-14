"""Page d'IA et modélisation."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data
from utils.indicators import TechnicalIndicators
from models.ai_engine import AIEngine
from config import DEFAULT_SYMBOL, POPULAR_SYMBOLS, AI_MODELS

st.set_page_config(
    page_title="AI Models",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Modélisation IA")

st.markdown("Entraînement et prédiction avec multiple modèles d'IA")

with st.sidebar:
    st.header("⚙️ Configuration")
    symbol = st.selectbox("Symbole", options=POPULAR_SYMBOLS)
    
    if st.button("💫 Entraîner Modéles", use_container_width=True):
        st.session_state.ai_symbol = symbol
        st.session_state.ai_train = True

if 'ai_symbol' not in st.session_state:
    st.session_state.ai_symbol = DEFAULT_SYMBOL
if 'ai_train' not in st.session_state:
    st.session_state.ai_train = False

with st.spinner("Chargement et préparation..."):
    df = load_data(st.session_state.ai_symbol, period="2y", interval="1d")
    
    if df is not None and not df.empty:
        df = TechnicalIndicators.add_all_indicators(df)
        
        if st.session_state.ai_train:
            st.subheader("💫 Entraînement des Modéles")
            
            ai_engine = AIEngine()
            
            with st.spinner("Entraînement en cours..."):
                success = ai_engine.train_models(df, st.session_state.ai_symbol)
            
            if success:
                st.success("✅ Modéles entraînés avec succès")
                
                # Afficher les importances
                if ai_engine.feature_importances:
                    st.subheader("📈 Importance des Features")
                    
                    for model_name, importances in ai_engine.feature_importances.items():
                        with st.expander(model_name):
                            if importances:
                                df_imp = pd.DataFrame([
                                    {"Feature": k, "Importance": v}
                                    for k, v in sorted(importances.items(), key=lambda x: x[1], reverse=True)
                                ])
                                
                                fig = go.Figure(data=[
                                    go.Bar(x=df_imp['Importance'], y=df_imp['Feature'], orientation='h')
                                ])
                                fig.update_layout(template="plotly_dark", height=400)
                                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ Erreur lors de l'entraînement")
            
            st.session_state.ai_train = False
        
        # Prédictions
        st.divider()
        st.subheader("🔭 Prédictions")
        
        ai_engine = AIEngine()
        ai_engine.load_models(st.session_state.ai_symbol)
        
        if ai_engine.models:
            predictions = ai_engine.predict(df)
            
            if "error" not in predictions:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Direction",
                        predictions.get('direction', 'N/A'),
                        predictions.get('consensus', 0.5)
                    )
                
                with col2:
                    st.metric(
                        "Confiance",
                        f"{predictions.get('average_confidence', 0):.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Consensus",
                        f"{predictions.get('consensus', 0.5):.2f}"
                    )
                
                # Détails par modèle
                st.subheader("📄 Détails par Modèle")
                
                df_preds = pd.DataFrame([
                    {
                        "Modèle": model,
                        "Prédiction": f"{pred:.3f}",
                        "Confiance": f"{predictions.get('confidences', {}).get(model, 0):.1f}%"
                    }
                    for model, pred in predictions.get('predictions', {}).items()
                ])
                
                st.dataframe(df_preds, use_container_width=True)
            else:
                st.error(predictions.get('error', 'Erreur inconnue'))
        else:
            st.info("Aucun modèle entraîné. Cliquez sur 'Entraîner Modéles' d'abord.")
    else:
        st.error("Erreur lors du chargement des données")
