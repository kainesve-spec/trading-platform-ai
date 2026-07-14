"""Calcul des métriques de performance."""

import numpy as np
import pandas as pd
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Classe pour calculer les métriques de performance."""
    
    @staticmethod
    def calculate_returns(df: pd.DataFrame, capital: float = 10000) -> Dict:
        """Calculer les métriques de rendement."""
        try:
            if df.empty or 'close' not in df.columns:
                return {}
            
            returns = df['close'].pct_change()
            
            total_return = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
            annual_return = ((df['close'].iloc[-1] / df['close'].iloc[0]) ** (252 / len(df)) - 1) * 100
            
            daily_returns = returns.dropna()
            cumulative_returns = (1 + daily_returns).cumprod() - 1
            
            metrics = {
                'total_return': total_return,
                'annual_return': annual_return,
                'daily_volatility': daily_returns.std() * 100,
                'annual_volatility': daily_returns.std() * np.sqrt(252) * 100,
                'sharpe_ratio': (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0,
                'max_drawdown': (cumulative_returns.min() * 100),
                'win_rate': (daily_returns > 0).sum() / len(daily_returns) * 100 if len(daily_returns) > 0 else 0,
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques: {str(e)}")
            return {}
    
    @staticmethod
    def calculate_drawdown(equity_curve: pd.Series) -> pd.Series:
        """Calculer le drawdown."""
        try:
            cummax = equity_curve.expanding().max()
            drawdown = (equity_curve - cummax) / cummax * 100
            return drawdown
        except Exception as e:
            logger.error(f"Erreur drawdown: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0) -> float:
        """Calculer le Sortino Ratio."""
        try:
            excess_returns = returns - target_return
            downside_returns = excess_returns[excess_returns < 0]
            downside_std = downside_returns.std()
            
            if downside_std == 0:
                return 0
            
            return (excess_returns.mean() / downside_std * np.sqrt(252))
        except Exception:
            return 0
    
    @staticmethod
    def calculate_profit_factor(wins: float, losses: float) -> float:
        """Calculer le Profit Factor."""
        try:
            if losses == 0:
                return wins if wins > 0 else 0
            return abs(wins / losses)
        except Exception:
            return 0
