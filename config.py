"""Configuration centralisée de l'application Trading AI Platform."""

import os
from datetime import datetime, timedelta

# Configuration Streamlit
STREAMLIT_PAGE_TITLE = "Trading AI Platform"
STREAMLIT_PAGE_ICON = "📊"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_INITIAL_SIDEBAR_STATE = "expanded"

# Configuration API
YFINANCE_TIMEOUT = 30
YFINANCE_RETRIES = 3

# Configuration des données
DEFAULT_SYMBOL = "AAPL"
DEFAULT_TIMEFRAME = "1d"  # 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
DEFAULT_PERIOD = "1y"
MAX_PERIOD = "10y"

# Configuration du portefeuille
DEFAULT_CAPITAL = 10000
DEFAULT_COMMISSION = 0.001  # 0.1%
DEFAULT_SPREAD = 0.0005  # 0.05%
DEFAULT_LEVERAGE = 1.0
DEFAULT_RISK_PERCENT = 2.0  # 2% par trade

# Configuration IA
AI_MODELS = {
    "Random Forest": {"n_estimators": 100, "max_depth": 10, "random_state": 42},
    "Gradient Boosting": {"n_estimators": 100, "learning_rate": 0.1, "random_state": 42},
    "Linear Regression": {},
}

MIN_CONFIDENCE_THRESHOLD = 0.5
MIN_DATA_POINTS = 50

# Configuration Signal Engine
SIGNAL_WEIGHTS = {
    "technical_analysis": 0.40,  # 40 points
    "ai_prediction": 0.30,       # 30 points
    "trend_strength": 0.20,      # 20 points
    "risk_reward": 0.10,         # 10 points
}

# Configuration Backtesting
BACKTEST_STRATEGIES = [
    "RSI",
    "MACD",
    "Moving Average",
    "Breakout",
    "Bollinger",
    "AI"
]

# Configuration des indicateurs techniques
TECHNICAL_INDICATORS = {
    "RSI": {"period": 14},
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
    "ATR": {"period": 14},
    "ADX": {"period": 14},
    "Bollinger Bands": {"period": 20, "std_dev": 2},
    "Ichimoku": {"period1": 9, "period2": 26, "period3": 52},
    "VWAP": {},
    "OBV": {},
    "Stochastic": {"period": 14, "smooth_k": 3, "smooth_d": 3},
}

# Chemins
LOGS_DIR = "logs"
MODELS_DIR = "models"
DATA_DIR = "data"
CACHE_DIR = ".streamlit/cache"

# Créer les répertoires s'ils n'existent pas
for dir_path in [LOGS_DIR, MODELS_DIR, DATA_DIR, CACHE_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Configuration Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Couleurs du thème
COLORS = {
    "up": "#26a69a",  # Vert (hausse)
    "down": "#ef5350",  # Rouge (baisse)
    "neutral": "#9e9e9e",  # Gris (neutre)
    "primary": "#1f77b4",  # Bleu primaire
    "secondary": "#ff7f0e",  # Orange secondaire
}

# Devises supportées
DEFAULT_CURRENCY = "USD"
SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]

# Configuration des alertes
ALERT_THRESHOLD_PRICE_CHANGE = 5.0  # % de changement pour déclencher une alerte
ALERT_THRESHOLD_VOLUME = 200.0  # % de changement de volume

# Configuration des notifications
NOTIFICATIONS_ENABLED = True
NOTIFICATION_SOUND = True

# Symboles populaires
POPULAR_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "TSLA", "META", "NFLX", "PYPL", "UBER",
    "SPY", "QQQ", "IWM", "VTI", "BRK.B"
]

# Timeframes disponibles
TIMEFRAMES = {
    "1m": "1 minute",
    "5m": "5 minutes",
    "15m": "15 minutes",
    "30m": "30 minutes",
    "1h": "1 heure",
    "1d": "1 jour",
    "1wk": "1 semaine",
    "1mo": "1 mois",
}

# Périodes disponibles
PERIODS = {
    "1mo": "1 mois",
    "3mo": "3 mois",
    "6mo": "6 mois",
    "1y": "1 an",
    "2y": "2 ans",
    "5y": "5 ans",
    "10y": "10 ans",
    "ytd": "Année à ce jour",
    "max": "Depuis le début",
}
