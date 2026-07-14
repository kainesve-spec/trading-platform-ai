"""Application principale Trading AI Platform.

Plateforme complète de trading assisté par IA avec:
- Dashboard en temps réel
- Analyse technique avancée
- Signal Engine (BUY/SELL/WAIT)
- Portfolio Manager
- Gestion du risque
- Backtesting
- Monitoring & Alertes
- Validation des données
- Modélisation IA multi-modèles
"""

import streamlit as st
import logging
from utils.logger import setup_logging
from config import (
    STREAMLIT_PAGE_TITLE,
    STREAMLIT_PAGE_ICON,
    STREAMLIT_LAYOUT,
    STREAMLIT_INITIAL_SIDEBAR_STATE,
)

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout=STREAMLIT_LAYOUT,
    initial_sidebar_state=STREAMLIT_INITIAL_SIDEBAR_STATE,
)

# Thème personnalisé
st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Page d'accueil
def main():
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📈 Trading AI Platform")
        st.markdown("### Plateforme d'aide à la décision pour le trading assisté par IA")
    
    with col2:
        st.markdown("")
        st.markdown("")
        mode = st.selectbox(
            "Mode d'affichage",
            ["Light", "Dark"],
            key="theme"
        )
    
    st.divider()
    
    # Présentation
    st.markdown("""
    ## 🌟 Bienvenue!
    
    Cette plateforme offre une solution complète pour l'analyse technique et le trading assisté par IA.
    
    ### 📈 Caractéristiques principales:
    
    1. **Dashboard** - Vue d'ensemble avec métriques en temps réel
    2. **Analyse Technique** - Indicateurs avancés (RSI, MACD, Bollinger, ADX, ATR, etc.)
    3. **Signal Engine** - Génération de signaux avec score de conviction 0-100
    4. **Portfolio Manager** - Gestion complète des positions
    5. **Gestion du Risque** - Calculateurs automatiques (Position Size, Stop Loss, Take Profit, Kelly)
    6. **Backtesting** - Test de stratégies sur données historiques
    7. **Monitoring** - Watchlist et alertes
    8. **IA Multi-modèles** - Random Forest, Gradient Boosting, Linear Regression
    9. **Validation de Données** - Contrôle qualité automatique
    
    ### 🚀 Démarrage rapide:
    
    1. Accédez au **Dashboard** pour commencer
    2. Sélectionnez un symbole (AAPL, MSFT, TSLA, etc.)
    3. Explorez l'**Analyse Technique**
    4. Générez un **Signal** avec le Signal Engine
    5. Testez votre stratégie avec le **Backtesting**
    
    ### ⚙️ Configuration:
    
    - **Capital par défaut**: 10,000 USD
    - **Risque par trade**: 2%
    - **Commission**: 0.1%
    - **Spread**: 0.05%
    
    ### 🔗 Liens rapides:
    
    - [Documentation](https://github.com/kainesve-spec/trading-platform-ai)
    - [Signal Engine](/?page=signal_engine)
    - [Backtesting](/?page=backtesting)
    """)
    
    st.divider()
    
    # Statistiques
    st.subheader("📊 Statistiques de la Plateforme")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Indicateurs",
            value="13+",
            delta="RSI, MACD, Bollinger, ADX, ATR, ..."
        )
    
    with col2:
        st.metric(
            label="Modèles IA",
            value="3",
            delta="RF, GB, LR"
        )
    
    with col3:
        st.metric(
            label="Stratégies",
            value="6",
            delta="RSI, MACD, MA, Bollinger, Breakout, IA"
        )
    
    with col4:
        st.metric(
            label="Symboles",
            value="15+",
            delta="Stocks, ETFs"
        )
    
    st.divider()
    
    # Guide d'utilisation
    with st.expander("📚 Guide d'Utilisation Complet"):
        st.markdown("""
        ### 📊 Dashboard
        Le dashboard fournit une vue d'ensemble complète avec:
        - Prix actuel et tendance
        - Volume de trading
        - Indicateurs clés (RSI, ADX)
        - Graphique OHLCV interactif
        - Moyennes mobiles (SMA 20, SMA 50)
        
        ### 📈 Analyse Technique
        Explorez les indicateurs techniques avancés:
        - RSI avec zones de surachat/survente
        - MACD avec signal et historique
        - Bandes de Bollinger
        - ADX pour la force de tendance
        - ATR pour la volatilité
        - Stochastique
        - OBV pour le volume
        
        ### 🎯 Signal Engine
        Générez des signaux de trading précis:
        - Score de conviction 0-100
        - Répartition: 40% technique, 30% IA, 20% tendance, 10% RR
        - Signaux: BUY, SELL, WAIT
        - Analyse détaillée
        
        ### 💼 Portfolio Manager
        Gérez vos positions:
        - Ajouter/fermer positions
        - Suivi des P/L
        - Historique des trades
        - Export CSV
        
        ### ⚠️ Gestion du Risque
        Calculateurs automatiques:
        - Position Size en fonction du capital et du risque
        - Take Profit en fonction du ratio Risk/Reward
        - Kelly Criterion
        - Métriques de risque (VaR, CVaR, Sharpe)
        
        ### 🔄 Backtesting
        Testez vos stratégies:
        - 6 stratégies incluses
        - Métriques: Win Rate, Profit Factor, Drawdown
        - Comparaison des stratégies
        - Optimisation paramétrée
        
        ### 📡 Monitoring
        Suivi en temps réel:
        - Watchlist personnalisée
        - Alertes de prix
        - Alertes de volume
        - Suivi des indicateurs
        
        ### 🔍 Validation de Données
        Vérification qualité:
        - Détection d'anomalies
        - Score de qualité
        - Inspection des colonnes
        - Export des données
        
        ### 🤖 Modélisation IA
        Machine Learning avancé:
        - Entraînement de modèles
        - Feature importance
        - Prédictions multi-modèles
        - Consensus d'ensemble
        """)
    
    st.divider()
    
    # Informations pratiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        ### 💵 Configuration par défaut
        - **Capital**: 10,000 USD
        - **Risque/trade**: 2%
        - **Commission**: 0.1%
        - **Spread**: 0.05%
        - **Levier**: 1x
        """)
    
    with col2:
        st.success("""
        ### ✅ Correctifs Inclus
        - Protection DataFrame vide
        - Vérification colonnes
        - Gestion volume zéro
        - Clip valeurs Stoch
        - RSI avec Wilder
        - Pas de duplication UI
        """)
    
    st.divider()
    
    # Footer
    st.markdown("""
    ---
    **Trading AI Platform** v1.0 | Plateforme de trading assisté par IA en Python
    
    Créée avec: Streamlit | Pandas | Scikit-Learn | YFinance | Plotly
    """)

if __name__ == "__main__":
    main()
