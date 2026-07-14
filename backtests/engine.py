"""Moteur de backtesting complet."""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Moteur de backtesting pour stratégies."""
    
    def __init__(self, df: pd.DataFrame, capital: float = 10000, commission: float = 0.001):
        self.df = df.copy()
        self.capital = capital
        self.commission = commission
        self.trades = []
        self.equity_curve = [capital]
    
    def backtest_strategy(self, strategy_name: str) -> Dict:
        """Lancer un backtest pour une stratégie."""
        try:
            if strategy_name == "RSI":
                return self._backtest_rsi()
            elif strategy_name == "MACD":
                return self._backtest_macd()
            elif strategy_name == "Moving Average":
                return self._backtest_ma()
            elif strategy_name == "Bollinger":
                return self._backtest_bollinger()
            elif strategy_name == "Breakout":
                return self._backtest_breakout()
            else:
                return {"error": f"Stratégie {strategy_name} non reconnue"}
            
        except Exception as e:
            logger.error(f"Erreur backtest: {str(e)}")
            return {"error": str(e)}
    
    def _backtest_rsi(self) -> Dict:
        """Backtest stratégie RSI."""
        try:
            if 'RSI' not in self.df.columns:
                return {"error": "RSI non disponible"}
            
            trades = []
            in_trade = False
            entry_price = 0
            
            for i in range(1, len(self.df)):
                rsi = self.df['RSI'].iloc[i]
                close = self.df['close'].iloc[i]
                
                # Signal d'achat
                if not in_trade and rsi < 30:
                    entry_price = close
                    in_trade = True
                    entry_idx = i
                
                # Signal de vente
                elif in_trade and rsi > 70:
                    profit = close - entry_price
                    profit_pct = (profit / entry_price) * 100
                    trades.append({
                        "entry": entry_price,
                        "exit": close,
                        "profit": profit,
                        "profit_pct": profit_pct,
                        "days": i - entry_idx,
                    })
                    in_trade = False
            
            return self._calculate_backtest_stats(trades, "RSI")
            
        except Exception as e:
            logger.error(f"Erreur RSI backtest: {str(e)}")
            return {"error": str(e)}
    
    def _backtest_macd(self) -> Dict:
        """Backtest stratégie MACD."""
        try:
            if 'MACD' not in self.df.columns or 'MACD_Signal' not in self.df.columns:
                return {"error": "MACD non disponible"}
            
            trades = []
            in_trade = False
            entry_price = 0
            
            for i in range(1, len(self.df)):
                macd = self.df['MACD'].iloc[i]
                signal = self.df['MACD_Signal'].iloc[i]
                close = self.df['close'].iloc[i]
                prev_macd = self.df['MACD'].iloc[i-1]
                prev_signal = self.df['MACD_Signal'].iloc[i-1]
                
                # Crossover
                if not in_trade and prev_macd <= prev_signal and macd > signal:
                    entry_price = close
                    in_trade = True
                    entry_idx = i
                
                elif in_trade and prev_macd >= prev_signal and macd < signal:
                    profit = close - entry_price
                    profit_pct = (profit / entry_price) * 100
                    trades.append({
                        "entry": entry_price,
                        "exit": close,
                        "profit": profit,
                        "profit_pct": profit_pct,
                        "days": i - entry_idx,
                    })
                    in_trade = False
            
            return self._calculate_backtest_stats(trades, "MACD")
            
        except Exception as e:
            logger.error(f"Erreur MACD backtest: {str(e)}")
            return {"error": str(e)}
    
    def _backtest_ma(self) -> Dict:
        """Backtest stratégie moyennes mobiles."""
        try:
            if 'SMA_20' not in self.df.columns or 'SMA_50' not in self.df.columns:
                return {"error": "Moyennes mobiles non disponibles"}
            
            trades = []
            in_trade = False
            entry_price = 0
            
            for i in range(1, len(self.df)):
                sma20 = self.df['SMA_20'].iloc[i]
                sma50 = self.df['SMA_50'].iloc[i]
                close = self.df['close'].iloc[i]
                prev_sma20 = self.df['SMA_20'].iloc[i-1]
                prev_sma50 = self.df['SMA_50'].iloc[i-1]
                
                if not in_trade and prev_sma20 <= prev_sma50 and sma20 > sma50:
                    entry_price = close
                    in_trade = True
                    entry_idx = i
                
                elif in_trade and prev_sma20 >= prev_sma50 and sma20 < sma50:
                    profit = close - entry_price
                    profit_pct = (profit / entry_price) * 100
                    trades.append({
                        "entry": entry_price,
                        "exit": close,
                        "profit": profit,
                        "profit_pct": profit_pct,
                        "days": i - entry_idx,
                    })
                    in_trade = False
            
            return self._calculate_backtest_stats(trades, "Moving Average")
            
        except Exception as e:
            logger.error(f"Erreur MA backtest: {str(e)}")
            return {"error": str(e)}
    
    def _backtest_bollinger(self) -> Dict:
        """Backtest stratégie Bollinger Bands."""
        try:
            if 'BB_Low' not in self.df.columns or 'BB_High' not in self.df.columns:
                return {"error": "Bandes de Bollinger non disponibles"}
            
            trades = []
            in_trade = False
            entry_price = 0
            
            for i in range(1, len(self.df)):
                close = self.df['close'].iloc[i]
                bb_low = self.df['BB_Low'].iloc[i]
                bb_high = self.df['BB_High'].iloc[i]
                
                if not in_trade and close < bb_low:
                    entry_price = close
                    in_trade = True
                    entry_idx = i
                
                elif in_trade and close > bb_high:
                    profit = close - entry_price
                    profit_pct = (profit / entry_price) * 100
                    trades.append({
                        "entry": entry_price,
                        "exit": close,
                        "profit": profit,
                        "profit_pct": profit_pct,
                        "days": i - entry_idx,
                    })
                    in_trade = False
            
            return self._calculate_backtest_stats(trades, "Bollinger Bands")
            
        except Exception as e:
            logger.error(f"Erreur Bollinger backtest: {str(e)}")
            return {"error": str(e)}
    
    def _backtest_breakout(self) -> Dict:
        """Backtest stratégie Breakout."""
        try:
            trades = []
            in_trade = False
            entry_price = 0
            window = 20
            
            for i in range(window, len(self.df)):
                high = self.df['high'].iloc[i]
                close = self.df['close'].iloc[i]
                prev_high = self.df['high'].iloc[i-window:i].max()
                
                if not in_trade and high > prev_high:
                    entry_price = high
                    in_trade = True
                    entry_idx = i
                
                elif in_trade and close < entry_price * 0.98:
                    profit = close - entry_price
                    profit_pct = (profit / entry_price) * 100
                    trades.append({
                        "entry": entry_price,
                        "exit": close,
                        "profit": profit,
                        "profit_pct": profit_pct,
                        "days": i - entry_idx,
                    })
                    in_trade = False
            
            return self._calculate_backtest_stats(trades, "Breakout")
            
        except Exception as e:
            logger.error(f"Erreur Breakout backtest: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_backtest_stats(self, trades: List[Dict], strategy: str) -> Dict:
        """Calculer les statistiques finales du backtest."""
        try:
            if not trades:
                return {
                    "strategy": strategy,
                    "trades": 0,
                    "win_rate": 0,
                    "total_profit": 0,
                    "profit_factor": 0,
                }
            
            trades_df = pd.DataFrame(trades)
            
            wins = len(trades_df[trades_df['profit'] > 0])
            losses = len(trades_df[trades_df['profit'] <= 0])
            total_trades = len(trades_df)
            
            gross_profit = trades_df[trades_df['profit'] > 0]['profit'].sum()
            gross_loss = abs(trades_df[trades_df['profit'] <= 0]['profit'].sum())
            
            total_profit = gross_profit - gross_loss
            total_profit_pct = (total_profit / self.capital) * 100
            
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            avg_win = trades_df[trades_df['profit'] > 0]['profit'].mean() if wins > 0 else 0
            avg_loss = trades_df[trades_df['profit'] <= 0]['profit'].mean() if losses > 0 else 0
            
            win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
            
            return {
                "strategy": strategy,
                "trades": total_trades,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "total_profit": total_profit,
                "total_profit_pct": total_profit_pct,
                "gross_profit": gross_profit,
                "gross_loss": gross_loss,
                "profit_factor": profit_factor,
                "avg_trade_duration": trades_df['days'].mean(),
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul stats: {str(e)}")
            return {}
