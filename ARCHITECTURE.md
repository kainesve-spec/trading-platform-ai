"""Documentation complète du projet."""

# Architecture du Projet Trading AI Platform

## Vue d'ensemble

La plateforme Trading AI est une solution complète de trading assisté par IA développée en Python avec Streamlit.

## Structure du Projet

```
trading-platform-ai/
├── app.py                    # Application principale Streamlit
├── config.py                 # Configuration centralisée
├── init.py                  # Script d'initialisation
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
├── .gitignore                # Fichiers à ignorer
├── .streamlit/               # Configuration Streamlit
├── pages/                    # Pages Streamlit multi-pages
├── utils/                    # Utilitaires
├── models/                   # Moteurs IA
├── signals/                  # Signal Engine
├── portfolio/                # Gestion du portefeuille
├── backtests/                # Backtesting engine
├── logs/                     # Fichiers journaux
├── models/                   # Modèles sauvegardés
├── data/                     # Données
└── assets/                   # Ressources
```

## Modules Principaux

### app.py
Application principale avec interface d'accueil et navigation.

### config.py
Configuration centralisée de l'application:
- Paramètres API (YFinance)
- Configuration des modèles IA
- Poids du Signal Engine
- Chemins de fichiers

### Pages Streamlit (pages/)

1. **01_dashboard.py** - Dashboard principal
   - Métriques en temps réel
   - Graphique OHLCV
   - Indicateurs clés

2. **02_technical_analysis.py** - Analyse technique
   - RSI, MACD, Bollinger, ADX, ATR, Stoch, OBV
   - Graphiques interactifs

3. **03_signal_engine.py** - Génération de signaux
   - Score de conviction 0-100
   - Signaux: BUY, SELL, WAIT

4. **04_portfolio.py** - Gestion du portefeuille
   - Ajouter/fermer positions
   - Historique des trades
   - Export CSV

5. **05_risk_management.py** - Gestion du risque
   - Position Size calculator
   - Take Profit calculator
   - Kelly Criterion

6. **06_backtesting.py** - Backtesting
   - 6 stratégies incluses
   - Métriques complètes

7. **07_monitoring.py** - Monitoring et alertes
   - Watchlist
   - Suivi des prix

8. **08_data_validation.py** - Validation de données
   - Détection d'anomalies
   - Score qualité

9. **09_ai_models.py** - Modélisation IA
   - Entraînement des modèles
   - Prédictions

### Utils (utils/)

- **data_loader.py** - Chargement et nettoyage des données
- **indicators.py** - Calcul des indicateurs techniques
- **logger.py** - Configuration du logging
- **metrics.py** - Calcul des métriques de performance

### Models (models/)

- **ai_engine.py** - Moteur IA avec 3 modèles:
  - Random Forest
  - Gradient Boosting
  - Linear Regression

### Signals (signals/)

- **signal_engine.py** - Génération de signaux avec:
  - Analyse technique (40%)
  - Prédiction IA (30%)
  - Force tendance (20%)
  - Risk/Reward (10%)

### Portfolio (portfolio/)

- **manager.py** - Gestion complète du portefeuille
- **risk_manager.py** - Calculs de risque avancés

### Backtests (backtests/)

- **engine.py** - Moteur de backtesting avec 6 stratégies

## Installation

### Prérequis
- Python 3.12+
- pip

### Étapes

1. Cloner le repository
```bash
git clone https://github.com/kainesve-spec/trading-platform-ai.git
cd trading-platform-ai
```

2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Initialiser l'application
```bash
python init.py
```

5. Lancer l'application
```bash
streamlit run app.py
```

## Utilisation

### Démarrage Rapide

1. Accédez au **Dashboard**
2. Sélectionnez un symbole (AAPL, MSFT, TSLA, etc.)
3. Chargez les données
4. Explorez les différentes pages

### Workflow Typique

1. **Analyse** - Utilisez l'Analyse Technique pour comprendre le marché
2. **Signal** - Générez un signal avec le Signal Engine
3. **Dimensionnement** - Calculez votre position size avec Risk Manager
4. **Backtest** - Testez votre stratégie sur données historiques
5. **Execution** - Ajoutez votre position au Portfolio Manager
6. **Monitoring** - Suivi réel avec la page Monitoring

## Indicateurs Techniques

### Inclus
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bandes de Bollinger
- ATR (Average True Range)
- ADX (Average Directional Index)
- Stochastique
- OBV (On-Balance Volume)
- VWAP (Volume Weighted Average Price)
- Moyennes mobiles simples et exponentielles

## Stratégies de Backtesting

1. **RSI** - Surachat/Survente
2. **MACD** - Crossovers
3. **Moving Average** - SMA 20/50
4. **Bollinger Bands** - Breakouts
5. **Breakout** - Hauteur 20 jours
6. **IA** - Prédictions du modèle

## Correctifs Robustesse

### Inclus
- ❌ Protection contre DataFrames vides
- ❌ Vérification présence colonnes OHLC
- ❌ Gestion volume zéro ou absent
- ❌ Remplacement valeurs infinies
- ❌ Lissage exponentiel Wilder pour RSI
- ❌ Clip valeurs Stochastique 0-100
- ❌ Nettoyage automatique doublons
- ❌ Élimination UI dupliquée

## Configuration Par Défaut

```python
DEFAULT_CAPITAL = 10000          # USD
DEFAULT_COMMISSION = 0.001       # 0.1%
DEFAULT_SPREAD = 0.0005          # 0.05%
DEFAULT_LEVERAGE = 1.0           # Sans levier
DEFAULT_RISK_PERCENT = 2.0       # 2% par trade
```

## Métriques de Performance

- Win Rate (%)
- Profit/Loss total
- Profit Factor
- Sharpe Ratio
- Drawdown maximal
- Sortino Ratio
- Average Trade Duration

## Architecture IA

### Modèles
- Random Forest (100 arbres)
- Gradient Boosting (100 estimateurs)
- Linear Regression

### Features
- SMA 20, SMA 50
- EMA 12, EMA 26
- RSI
- MACD et signal
- Bandes de Bollinger
- ATR, ADX
- Stochastique
- OBV, VWAP

### Consensus
Moyenne des prédictions des 3 modèles

## Qualité du Code

- ✅ PEP8 compliante
- ✅ Architecture modulaire
- ✅ Fonctions documentées
- ✅ Gestion des exceptions
- ✅ Logging complet
- ✅ Optimisation performance

## Fichiers Journaux

Les logs sont sauvegardés dans `logs/trading_ai.log`

## Support

Pour les problèmes:
1. Vérifiez les logs
2. Assurez-vous que toutes les dépendances sont installées
3. Consultez la documentation

## Licence

MIT

## Auteur

kainesve-spec

## Remerciements

- Streamlit pour l'interface
- YFinance pour les données
- Scikit-Learn pour le ML
- Plotly pour les graphiques
