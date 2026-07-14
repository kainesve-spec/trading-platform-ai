"""Calcul des indicateurs techniques avec robustesse."""

import numpy as np
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Classe pour calculer les indicateurs techniques."""
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Ajouter tous les indicateurs au DataFrame."""
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            # Moyennes mobiles
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_50'] = df['close'].rolling(window=50).mean()
            df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # RSI
            df = TechnicalIndicators.calculate_rsi(df)
            
            # MACD
            df = TechnicalIndicators.calculate_macd(df)
            
            # Bandes de Bollinger
            df = TechnicalIndicators.calculate_bollinger_bands(df)
            
            # ATR
            df = TechnicalIndicators.calculate_atr(df)
            
            # ADX
            df = TechnicalIndicators.calculate_adx(df)
            
            # Stochastic
            df = TechnicalIndicators.calculate_stochastic(df)
            
            # OBV
            df = TechnicalIndicators.calculate_obv(df)
            
            # VWAP
            df = TechnicalIndicators.calculate_vwap(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des indicateurs: {str(e)}")
            return df
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculer le RSI avec lissage exponentiel de Wilder."""
        try:
            if df.empty or 'close' not in df.columns or len(df) < period:
                df['RSI'] = np.nan
                return df
            
            close = df['close'].astype(float)
            delta = close.diff()
            
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Wilder's smoothing
            gain_ema = gain.ewm(span=period, adjust=False).mean()
            loss_ema = loss.ewm(span=period, adjust=False).mean()
            
            rs = gain_ema / loss_ema.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))
            df['RSI'] = df['RSI'].fillna(50).clip(0, 100)
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur RSI: {str(e)}")
            df['RSI'] = np.nan
            return df
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculer le MACD."""
        try:
            if df.empty or 'close' not in df.columns:
                df['MACD'] = np.nan
                df['MACD_Signal'] = np.nan
                df['MACD_Hist'] = np.nan
                return df
            
            close = df['close'].astype(float)
            ema_fast = close.ewm(span=fast, adjust=False).mean()
            ema_slow = close.ewm(span=slow, adjust=False).mean()
            
            df['MACD'] = ema_fast - ema_slow
            df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur MACD: {str(e)}")
            return df
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """Calculer les bandes de Bollinger."""
        try:
            if df.empty or 'close' not in df.columns or len(df) < period:
                df['BB_Mid'] = np.nan
                df['BB_High'] = np.nan
                df['BB_Low'] = np.nan
                return df
            
            close = df['close'].astype(float)
            sma = close.rolling(window=period).mean()
            std = close.rolling(window=period).std()
            
            df['BB_Mid'] = sma
            df['BB_High'] = sma + (std * std_dev)
            df['BB_Low'] = sma - (std * std_dev)
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur Bollinger: {str(e)}")
            return df
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculer l'ATR (Average True Range)."""
        try:
            if df.empty or not all(col in df.columns for col in ['high', 'low', 'close']):
                df['ATR'] = np.nan
                return df
            
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            close = df['close'].astype(float)
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=period).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur ATR: {str(e)}")
            df['ATR'] = np.nan
            return df
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculer l'ADX (Average Directional Index)."""
        try:
            if df.empty or not all(col in df.columns for col in ['high', 'low']):
                df['ADX'] = np.nan
                return df
            
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            
            up_move = high.diff()
            down_move = -low.diff()
            
            pos_di = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
            neg_di = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
            
            tr = TechnicalIndicators.calculate_atr(df.copy(), period)['ATR']
            
            di_pos = 100 * (pd.Series(pos_di).rolling(window=period).mean() / tr)
            di_neg = 100 * (pd.Series(neg_di).rolling(window=period).mean() / tr)
            
            dx = 100 * abs(di_pos - di_neg) / (di_pos + di_neg)
            df['ADX'] = dx.rolling(window=period).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur ADX: {str(e)}")
            df['ADX'] = np.nan
            return df
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> pd.DataFrame:
        """Calculer le Stochastique."""
        try:
            if df.empty or not all(col in df.columns for col in ['high', 'low', 'close']) or len(df) < period:
                df['Stoch_K'] = np.nan
                df['Stoch_D'] = np.nan
                return df
            
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            close = df['close'].astype(float)
            
            lowest_low = low.rolling(window=period).min()
            highest_high = high.rolling(window=period).max()
            
            k = 100 * (close - lowest_low) / (highest_high - lowest_low)
            k = k.rolling(window=smooth_k).mean()
            
            df['Stoch_K'] = k.clip(0, 100)
            df['Stoch_D'] = k.rolling(window=smooth_d).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur Stochastic: {str(e)}")
            return df
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculer l'OBV (On Balance Volume)."""
        try:
            if df.empty or not all(col in df.columns for col in ['close', 'volume']):
                df['OBV'] = np.nan
                return df
            
            close = df['close'].astype(float)
            volume = df['volume'].astype(float)
            
            obv = np.where(close.diff() > 0, volume, np.where(close.diff() < 0, -volume, 0))
            df['OBV'] = pd.Series(obv).cumsum()
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur OBV: {str(e)}")
            df['OBV'] = np.nan
            return df
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """Calculer le VWAP (Volume Weighted Average Price)."""
        try:
            if df.empty or not all(col in df.columns for col in ['high', 'low', 'close', 'volume']):
                df['VWAP'] = np.nan
                return df
            
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            df['VWAP'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur VWAP: {str(e)}")
            df['VWAP'] = np.nan
            return df
