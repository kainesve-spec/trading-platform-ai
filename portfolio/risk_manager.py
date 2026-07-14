"""Gestion du risque et dimensionnement des positions."""

import numpy as np
import pandas as pd
import logging
from typing import Dict, Optional
from config import DEFAULT_RISK_PERCENT

logger = logging.getLogger(__name__)


class RiskManager:
    """Géreur du risque professionnel."""
    
    @staticmethod
    def calculate_position_size(capital: float, risk_percent: float = DEFAULT_RISK_PERCENT,
                               entry_price: float = 1, stop_loss: float = 0) -> Dict:
        """Calculer la taille de position avec Kelly Criterion."""
        try:
            if entry_price <= 0 or capital <= 0:
                return {"error": "Prix ou capital invalide"}
            
            if stop_loss <= 0 or stop_loss >= entry_price:
                return {"error": "Stop loss invalide"}
            
            # Risque en montant
            risk_amount = capital * (risk_percent / 100)
            
            # Distance au stop loss
            stop_loss_distance = entry_price - stop_loss
            
            # Nombre de titres
            quantity = risk_amount / stop_loss_distance
            
            # Montant risqué
            risk_amount_actual = quantity * stop_loss_distance
            
            # Pourcentage de risque réel
            risk_percent_actual = (risk_amount_actual / capital) * 100
            
            return {
                "quantity": max(0, int(quantity)),
                "risk_amount": risk_amount_actual,
                "risk_percent": risk_percent_actual,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul position: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def calculate_take_profit(entry_price: float, stop_loss: float, 
                             risk_reward_ratio: float = 2.0) -> float:
        """Calculer le take profit en fonction du ratio Risk/Reward."""
        try:
            if entry_price <= 0 or stop_loss <= 0:
                return 0
            
            risk = entry_price - stop_loss
            reward = risk * risk_reward_ratio
            take_profit = entry_price + reward
            
            return take_profit
            
        except Exception as e:
            logger.error(f"Erreur calcul TP: {str(e)}")
            return 0
    
    @staticmethod
    def calculate_kelly_criterion(win_rate: float, avg_win: float, 
                                 avg_loss: float) -> float:
        """Calculer le Kelly Criterion pour la taille optimale de position."""
        try:
            if avg_loss <= 0 or avg_win <= 0:
                return 0.02  # Par défaut 2%
            
            # F* = (bp - q) / b
            # F* = (p * (avg_win/avg_loss) - (1-p)) / (avg_win/avg_loss)
            
            p = win_rate
            q = 1 - p
            b = avg_win / avg_loss
            
            kelly = (p * b - q) / b
            
            # Limiter à 25% pour la prudence
            kelly = max(0, min(0.25, kelly))
            
            return kelly
            
        except Exception as e:
            logger.error(f"Erreur Kelly: {str(e)}")
            return 0.02
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Calculer le drawdown maximal."""
        try:
            if equity_curve.empty:
                return 0
            
            cummax = equity_curve.expanding().max()
            drawdown = (equity_curve - cummax) / cummax
            max_dd = drawdown.min()
            
            return abs(max_dd) * 100
            
        except Exception as e:
            logger.error(f"Erreur drawdown: {str(e)}")
            return 0
    
    @staticmethod
    def calculate_trailing_stop(current_price: float, highest_price: float,
                               trailing_percent: float = 2.0) -> float:
        """Calculer le trailing stop."""
        try:
            trailing_amount = highest_price * (trailing_percent / 100)
            trailing_stop = highest_price - trailing_amount
            return trailing_stop
            
        except Exception as e:
            logger.error(f"Erreur trailing stop: {str(e)}")
            return 0
    
    @staticmethod
    def get_risk_metrics(df: pd.DataFrame, capital: float) -> Dict:
        """Obtenir les métriques de risque complètes."""
        try:
            if df.empty or 'close' not in df.columns:
                return {}
            
            returns = df['close'].pct_change()
            
            metrics = {
                "volatility": returns.std() * 100,
                "sharpe_ratio": (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
                "var_95": returns.quantile(0.05) * capital,
                "cvar_95": returns[returns <= returns.quantile(0.05)].mean() * capital,
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur métriques risque: {str(e)}")
            return {}
