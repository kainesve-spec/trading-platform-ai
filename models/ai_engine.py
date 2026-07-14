"""Moteur d'intelligence artificielle pour prédiction et analyse."""

import numpy as np
import pandas as pd
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict, Tuple, Optional
import joblib
from config import AI_MODELS, MIN_DATA_POINTS, MODELS_DIR
import os

logger = logging.getLogger(__name__)


class AIEngine:
    """Moteur IA avec multiple modèles pour prédiction."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importances = {}
        self.models_dir = MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series]]:
        """Préparer les features et target pour l'IA."""
        try:
            if df.empty or len(df) < MIN_DATA_POINTS:
                return None, None
            
            df_copy = df.copy()
            
            # Features: indicateurs techniques
            features = ['SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'RSI', 'MACD', 
                       'MACD_Signal', 'BB_High', 'BB_Low', 'ATR', 'ADX', 
                       'Stoch_K', 'OBV', 'VWAP']
            
            # Vérifier quelles features sont disponibles
            available_features = [f for f in features if f in df_copy.columns]
            
            if len(available_features) < 5:
                logger.warning("Pas assez de features disponibles")
                return None, None
            
            X = df_copy[available_features].dropna()
            
            if X.empty:
                return None, None
            
            # Target: direction du prix
            df_copy['Price_Change'] = df_copy['close'].pct_change() * 100
            y = (df_copy['Price_Change'] > 0).astype(int)
            
            # Aligner X et y
            common_idx = X.index.intersection(y.index)
            X = X.loc[common_idx]
            y = y.loc[common_idx]
            
            if len(X) < MIN_DATA_POINTS:
                return None, None
            
            return X, y
            
        except Exception as e:
            logger.error(f"Erreur préparation features: {str(e)}")
            return None, None
    
    def train_models(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> bool:
        """Entraîner les modèles IA."""
        try:
            X, y = self.prepare_features(df)
            
            if X is None or y is None:
                logger.warning(f"Impossible d'entraîner les modèles: features insuffisantes")
                return False
            
            # Split données
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entraîner Random Forest
            try:
                rf = RandomForestRegressor(**AI_MODELS["Random Forest"])
                rf.fit(X_train_scaled, y_train)
                score_rf = rf.score(X_test_scaled, y_test)
                self.models['Random Forest'] = rf
                self.feature_importances['Random Forest'] = dict(zip(
                    X.columns, rf.feature_importances_
                ))
                logger.info(f"Random Forest trainé: score={score_rf:.3f}")
            except Exception as e:
                logger.error(f"Erreur Random Forest: {str(e)}")
            
            # Entraîner Gradient Boosting
            try:
                gb = GradientBoostingRegressor(**AI_MODELS["Gradient Boosting"])
                gb.fit(X_train_scaled, y_train)
                score_gb = gb.score(X_test_scaled, y_test)
                self.models['Gradient Boosting'] = gb
                self.feature_importances['Gradient Boosting'] = dict(zip(
                    X.columns, gb.feature_importances_
                ))
                logger.info(f"Gradient Boosting trainé: score={score_gb:.3f}")
            except Exception as e:
                logger.error(f"Erreur Gradient Boosting: {str(e)}")
            
            # Entraîner Linear Regression
            try:
                lr = LinearRegression()
                lr.fit(X_train_scaled, y_train)
                score_lr = lr.score(X_test_scaled, y_test)
                self.models['Linear Regression'] = lr
                logger.info(f"Linear Regression trainée: score={score_lr:.3f}")
            except Exception as e:
                logger.error(f"Erreur Linear Regression: {str(e)}")
            
            self.scalers['scaler'] = scaler
            self.save_models(symbol)
            
            return len(self.models) > 0
            
        except Exception as e:
            logger.error(f"Erreur entraînement: {str(e)}")
            return False
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """Faire une prédiction avec tous les modèles."""
        try:
            if df.empty or len(self.models) == 0:
                return {"error": "Modèles non disponibles"}
            
            X, _ = self.prepare_features(df)
            
            if X is None:
                return {"error": "Features insuffisantes"}
            
            # Prendre la dernière ligne
            X_latest = X.iloc[-1:]
            
            # Scaler
            if 'scaler' in self.scalers:
                X_scaled = self.scalers['scaler'].transform(X_latest)
            else:
                X_scaled = X_latest.values
            
            predictions = {}
            confidences = {}
            
            for model_name, model in self.models.items():
                try:
                    pred = model.predict(X_scaled)[0]
                    predictions[model_name] = pred
                    
                    # Confiance basée sur la prédiction
                    confidence = abs(pred - 0.5) * 200 if 0 <= pred <= 1 else 50
                    confidences[model_name] = max(0, min(100, confidence))
                except Exception as e:
                    logger.error(f"Erreur prédiction {model_name}: {str(e)}")
            
            if not predictions:
                return {"error": "Aucune prédiction disponible"}
            
            # Consensus
            avg_prediction = np.mean(list(predictions.values()))
            direction = "HAUTÊSE" if avg_prediction > 0.5 else "BAISSE"
            avg_confidence = np.mean(list(confidences.values()))
            
            return {
                "predictions": predictions,
                "confidences": confidences,
                "consensus": avg_prediction,
                "direction": direction,
                "average_confidence": avg_confidence,
                "feature_importances": self.feature_importances,
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction: {str(e)}")
            return {"error": str(e)}
    
    def save_models(self, symbol: str = "default"):
        """Sauvegarder les modèles entraînés."""
        try:
            for model_name, model in self.models.items():
                path = f"{self.models_dir}/{symbol}_{model_name.replace(' ', '_')}.pkl"
                joblib.dump(model, path)
            
            scaler_path = f"{self.models_dir}/{symbol}_scaler.pkl"
            if 'scaler' in self.scalers:
                joblib.dump(self.scalers['scaler'], scaler_path)
            
            logger.info(f"Modèles sauvegardés pour {symbol}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde modèles: {str(e)}")
    
    def load_models(self, symbol: str = "default"):
        """Charger les modèles entraînés."""
        try:
            for model_name in AI_MODELS.keys():
                path = f"{self.models_dir}/{symbol}_{model_name.replace(' ', '_')}.pkl"
                if os.path.exists(path):
                    self.models[model_name] = joblib.load(path)
            
            scaler_path = f"{self.models_dir}/{symbol}_scaler.pkl"
            if os.path.exists(scaler_path):
                self.scalers['scaler'] = joblib.load(scaler_path)
            
            logger.info(f"Modèles chargés pour {symbol}")
            
        except Exception as e:
            logger.error(f"Erreur chargement modèles: {str(e)}")
