"""Moteur de signaux pour générer les signaux de trading."""

import numpy as np
import pandas as pd
import logging
from typing import Dict, Optional
from config import SIGNAL_WEIGHTS

logger = logging.getLogger(__name__)


class SignalEngine:
    """Moteur de signaux professionnel avec scoring de conviction 0-100."""
    
    @staticmethod
    def generate_signal(df: pd.DataFrame, ai_prediction: Optional[Dict] = None) -> Dict:
        """Générer un signal complet avec score de conviction."""
        try:
            if df.empty or 'close' not in df.columns:
                return SignalEngine._empty_signal()
            
            # Analyse technique (40 points)
            tech_score, tech_comments = SignalEngine.analyze_technical(df)
            
            # Prédiction IA (30 points)
            ai_score, ai_comments = SignalEngine.analyze_ai(ai_prediction)
            
            # Force de tendance (20 points)
            trend_score, trend_comments = SignalEngine.analyze_trend(df)
            
            # Qualité Risk/Reward (10 points)
            rr_score, rr_comments = SignalEngine.analyze_risk_reward(df)
            
            # Score total de conviction
            total_score = (
                tech_score * SIGNAL_WEIGHTS["technical_analysis"] * 100 +
                ai_score * SIGNAL_WEIGHTS["ai_prediction"] * 100 +
                trend_score * SIGNAL_WEIGHTS["trend_strength"] * 100 +
                rr_score * SIGNAL_WEIGHTS["risk_reward"] * 100
            )
            
            total_score = max(0, min(100, total_score))
            
            # Déterminer le signal
            if total_score > 65:
                signal = "BUY"
                emoji = "🔼"
            elif total_score < 35:
                signal = "SELL"
                emoji = "🔽"
            else:
                signal = "WAIT"
                emoji = "⏸️"
            
            comments = [
                f"Analyse technique: {tech_comments}",
                f"Prédiction IA: {ai_comments}",
                f"Tendance: {trend_comments}",
                f"Risk/Reward: {rr_comments}"
            ]
            
            return {
                "signal": signal,
                "emoji": emoji,
                "conviction": total_score,
                "tech_score": tech_score * 40,
                "ai_score": ai_score * 30,
                "trend_score": trend_score * 20,
                "rr_score": rr_score * 10,
                "comments": comments,
                "analysis": {
                    "technical": tech_comments,
                    "ai": ai_comments,
                    "trend": trend_comments,
                    "risk_reward": rr_comments,
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur génération signal: {str(e)}")
            return SignalEngine._empty_signal()
    
    @staticmethod
    def analyze_technical(df: pd.DataFrame) -> tuple:
        """Analyser les indicateurs techniques."""
        try:
            if df.empty:
                return 0.5, "Données insuffisantes"
            
            score = 0.5  # Neutre
            comments = []
            
            # RSI
            if 'RSI' in df.columns:
                rsi = df['RSI'].iloc[-1]
                if 30 <= rsi <= 70:
                    score += 0.05
                    comments.append(f"RSI normal ({rsi:.1f})")
                elif rsi > 70:
                    score -= 0.1
                    comments.append(f"RSI survente ({rsi:.1f})")
                elif rsi < 30:
                    score += 0.1
                    comments.append(f"RSI surachat ({rsi:.1f})")
            
            # MACD
            if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
                macd = df['MACD'].iloc[-1]
                signal = df['MACD_Signal'].iloc[-1]
                if macd > signal:
                    score += 0.1
                    comments.append("MACD bullish")
                else:
                    score -= 0.1
                    comments.append("MACD bearish")
            
            # Bandes de Bollinger
            if 'BB_Low' in df.columns and 'BB_High' in df.columns:
                close = df['close'].iloc[-1]
                bb_low = df['BB_Low'].iloc[-1]
                bb_high = df['BB_High'].iloc[-1]
                
                if close < bb_low:
                    score += 0.1
                    comments.append("Prix en-dessous des bandes")
                elif close > bb_high:
                    score -= 0.1
                    comments.append("Prix au-dessus des bandes")
            
            # ADX
            if 'ADX' in df.columns:
                adx = df['ADX'].iloc[-1]
                if adx > 25:
                    score += 0.05
                    comments.append(f"Tendance forte (ADX: {adx:.1f})")
            
            score = max(0, min(1, score))
            comment_text = ", ".join(comments) if comments else "Signaux mixtes"
            
            return score, comment_text
            
        except Exception as e:
            logger.error(f"Erreur analyse technique: {str(e)}")
            return 0.5, "Erreur analyse"
    
    @staticmethod
    def analyze_ai(ai_prediction: Optional[Dict]) -> tuple:
        """Analyser la prédiction IA."""
        try:
            if not ai_prediction or "error" in ai_prediction:
                return 0.5, "IA non disponible"
            
            consensus = ai_prediction.get("consensus", 0.5)
            direction = ai_prediction.get("direction", "NEUTRE")
            confidence = ai_prediction.get("average_confidence", 50)
            
            # Score basé sur la confiance
            score = confidence / 100
            
            comment = f"{direction} ({confidence:.0f}% confiance)"
            
            return score, comment
            
        except Exception as e:
            logger.error(f"Erreur analyse IA: {str(e)}")
            return 0.5, "Erreur IA"
    
    @staticmethod
    def analyze_trend(df: pd.DataFrame) -> tuple:
        """Analyser la force de la tendance."""
        try:
            if df.empty or 'close' not in df.columns:
                return 0.5, "Données insuffisantes"
            
            close = df['close'].astype(float)
            
            # Calcul de la tendance simple
            pct_change = close.pct_change(20).iloc[-1] * 100 if len(close) >= 20 else 0
            
            score = 0.5
            
            if pct_change > 5:
                score = 0.8
                comment = f"Forte hausse (+{pct_change:.1f}%)"
            elif pct_change > 1:
                score = 0.6
                comment = f"Hausse modérée (+{pct_change:.1f}%)"
            elif pct_change < -5:
                score = 0.2
                comment = f"Forte baisse ({pct_change:.1f}%)"
            elif pct_change < -1:
                score = 0.4
                comment = f"Baisse modérée ({pct_change:.1f}%)"
            else:
                score = 0.5
                comment = "Tendance plate"
            
            return score, comment
            
        except Exception as e:
            logger.error(f"Erreur analyse tendance: {str(e)}")
            return 0.5, "Erreur tendance"
    
    @staticmethod
    def analyze_risk_reward(df: pd.DataFrame) -> tuple:
        """Analyser la qualité Risk/Reward."""
        try:
            if df.empty or 'ATR' not in df.columns:
                return 0.5, "ATR non disponible"
            
            atr = df['ATR'].iloc[-1]
            
            if atr > 0:
                score = 0.5 + (atr / (atr * 2)) * 0.5
                comment = f"ATR: {atr:.2f}"
            else:
                score = 0.5
                comment = "ATR non calculable"
            
            return score, comment
            
        except Exception as e:
            logger.error(f"Erreur analyse RR: {str(e)}")
            return 0.5, "Erreur RR"
    
    @staticmethod
    def _empty_signal() -> Dict:
        """Retourner un signal vide."""
        return {
            "signal": "WAIT",
            "emoji": "⏸️",
            "conviction": 50,
            "tech_score": 0,
            "ai_score": 0,
            "trend_score": 0,
            "rr_score": 0,
            "comments": ["Signal non disponible"],
            "analysis": {}
          }
