"""
Moteur professionnel de génération de signaux de trading.

Signaux générés :
- STRONG BUY 🟢
- BUY 🔼
- BUY & SELL ⚖️
- SELL 🔽
- STRONG SELL 🔴

Score de conviction : 0 - 100

Pondération :
- Analyse technique : 40 points
- Analyse IA : 30 points
- Analyse tendance : 20 points
- Risk Reward : 10 points
"""

import logging
from typing import Dict, Optional, Tuple

import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class SignalEngine:
    """
    Moteur professionnel de signaux de trading.
    Compatible crypto, actions et forex.
    """

    TECHNICAL_WEIGHT = 40
    AI_WEIGHT = 30
    TREND_WEIGHT = 20
    RISK_WEIGHT = 10

    def __init__(self):
        self.logger = logger

    def generate_signal(
        self,
        df: pd.DataFrame,
        ai_prediction: Optional[float] = None
    ) -> Dict:

        try:
            df = self._normalize_dataframe(df)

            if df.empty:
                return self._empty_signal()

            technical_score, technical_comments = self.analyze_technical(df)

            ai_score, ai_comments = self.analyze_ai(ai_prediction)

            trend_score, trend_comments = self.analyze_trend(df)

            risk_score, risk_data = self.analyze_risk_reward(df)

            conviction = (
                technical_score
                + ai_score
                + trend_score
                + risk_score
            )

            conviction = int(np.clip(conviction, 0, 100))

            coherence_bonus = self.check_coherence(
                technical_score,
                ai_score,
                trend_score
            )

            conviction += coherence_bonus
            conviction = int(np.clip(conviction, 0, 100))

            signal, emoji, direction = self._classify_signal(conviction)

            entry_price = risk_data["entry_price"]
            stop_loss = risk_data["stop_loss"]
            take_profit = risk_data["take_profit"]
            rr_ratio = risk_data["rr_ratio"]

            analysis = {
                "technical": technical_comments,
                "ai": ai_comments,
                "trend": trend_comments,
                "risk_reward": risk_data["analysis"]
            }

            comments = self._generate_comments(
                signal,
                conviction,
                technical_score,
                ai_score,
                trend_score,
                rr_ratio
            )

            return {
                "signal": signal,
                "emoji": emoji,
                "direction": direction,
                "conviction": conviction,

                "technical_score": technical_score,
                "ai_score": ai_score,
                "trend_score": trend_score,
                "risk_score": risk_score,

                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "rr_ratio": rr_ratio,

                "analysis": analysis,
                "comments": comments
            }

        except Exception as e:
            logger.exception(
                f"Erreur génération signal : {e}"
            )
            return self._empty_signal()

    def analyze_technical(
        self,
        df: pd.DataFrame
    ) -> Tuple[int, str]:

        score = 0
        comments = []

        try:
            last = df.iloc[-1]

            rsi = self._get_value(last, "RSI")
            macd = self._get_value(last, "MACD")
            macd_signal = self._get_value(last, "MACD_Signal")

            close = self._get_value(last, "Close")
            ema20 = self._get_value(last, "EMA20")
            ema50 = self._get_value(last, "EMA50")

            if rsi is not None:
                if rsi < 30:
                    score += 12
                    comments.append(
                        "RSI en zone survendue, potentiel rebond."
                    )
                elif rsi > 70:
                    score -= 10
                    comments.append(
                        "RSI en zone de surachat."
                    )
                else:
                    score += 5

            if macd is not None and macd_signal is not None:
                if macd > macd_signal:
                    score += 10
                    comments.append(
                        "MACD positif."
                    )
                else:
                    score -= 8
                    comments.append(
                        "MACD baissier."
                    )

            if close and ema20 and ema50:
                if close > ema20 > ema50:
                    score += 12
                    comments.append(
                        "Prix au-dessus des moyennes mobiles."
                    )
                elif close < ema20 < ema50:
                    score -= 10
                    comments.append(
                        "Tendance mobile négative."
                    )

            score = int(
                np.clip(
                    score,
                    0,
                    self.TECHNICAL_WEIGHT
                )
            )

            return score, " ".join(comments)

        except Exception as e:
            logger.error(
                f"Erreur analyse technique : {e}"
            )
            return 0, "Analyse technique indisponible."

    def analyze_ai(
        self,
        ai_prediction: Optional[float]
    ) -> Tuple[int, str]:

        if ai_prediction is None:
            return 15, "Aucune prédiction IA disponible."

        try:
            prediction = float(ai_prediction)

            if prediction >= 0.75:
                return 30, "IA fortement haussière."

            if prediction >= 0.55:
                return 22, "IA légèrement haussière."

            if prediction <= 0.25:
                return 5, "IA fortement baissière."

            if prediction <= 0.45:
                return 10, "IA légèrement baissière."

            return 15, "IA neutre."

        except Exception as e:
            logger.error(
                f"Erreur analyse IA : {e}"
            )
            return 15, "Analyse IA indisponible."

    def analyze_trend(
        self,
        df: pd.DataFrame
    ) -> Tuple[int, str]:

        score = 10
        comments = []

        try:
            last = df.iloc[-1]

            close = self._get_value(last, "Close")
            ema50 = self._get_value(last, "EMA50")
            ema200 = self._get_value(last, "EMA200")
            adx = self._get_value(last, "ADX")

            if close and ema50:
                if close > ema50:
                    score += 5
                    comments.append(
                        "Tendance court terme positive."
                    )
                else:
                    score -= 5
                    comments.append(
                        "Pression vendeuse court terme."
                    )

            if close and ema200:
                if close > ema200:
                    score += 3
                    comments.append(
                        "Structure long terme haussière."
                    )
                else:
                    score -= 3

            if adx:
                if adx > 25:
                    score += 2
                    comments.append(
                        "Tendance confirmée par ADX."
                    )

            score = int(
                np.clip(
                    score,
                    0,
                    self.TREND_WEIGHT
                )
            )

            return score, " ".join(comments)

        except Exception as e:
            logger.error(
                f"Erreur analyse tendance : {e}"
            )
            return 10, "Analyse tendance indisponible."

    def analyze_risk_reward(
        self,
        df: pd.DataFrame
    ) -> Tuple[int, Dict]:

        try:
            close = float(df["Close"].iloc[-1])

            atr = None

            if "ATR" in df.columns:
                atr = float(df["ATR"].iloc[-1])

            if not atr or np.isnan(atr):
                atr = close * 0.02

            stop_loss = close - atr
            take_profit = close + (atr * 2)

            risk = abs(close - stop_loss)
            reward = abs(take_profit - close)

            rr_ratio = (
                reward / risk
                if risk > 0
                else 0
            )

            if rr_ratio >= 2:
                score = 10
            elif rr_ratio >= 1.5:
                score = 7
            elif rr_ratio >= 1:
                score = 5
            else:
                score = 2

            return score, {
                "entry_price": round(close, 4),
                "stop_loss": round(stop_loss, 4),
                "take_profit": round(take_profit, 4),
                "rr_ratio": round(rr_ratio, 2),
                "analysis": (
                    f"Ratio risque rendement : {round(rr_ratio,2)}"
                )
            }

        except Exception as e:
            logger.error(
                f"Erreur Risk Reward : {e}"
            )

            return 0, {
                "entry_price": 0,
                "stop_loss": 0,
                "take_profit": 0,
                "rr_ratio": 0,
                "analysis": "Risk Reward indisponible."
            }

    def check_coherence(
        self,
        technical_score: int,
        ai_score: int,
        trend_score: int
    ) -> int:

        try:
            bonus = 0

            if (
                technical_score > 25
                and ai_score > 20
                and trend_score > 12
            ):
                bonus = 5

            elif (
                technical_score < 10
                and ai_score < 10
                and trend_score < 8
            ):
                bonus = -5

            return bonus

        except Exception:
            return 0

    def _classify_signal(
        self,
        conviction: int
    ) -> Tuple[str, str, str]:

        if conviction >= 80:
            return "STRONG BUY", "🟢", "BUY"

        if conviction >= 60:
            return "BUY", "🔼", "BUY"

        if conviction >= 45:
            return "BUY & SELL", "⚖️", "NEUTRAL"

        if conviction >= 25:
            return "SELL", "🔽", "SELL"

        return "STRONG SELL", "🔴", "SELL"

    def _normalize_dataframe(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        try:
            if df is None:
                return pd.DataFrame()

            if not isinstance(df, pd.DataFrame):
                return pd.DataFrame()

            df = df.copy()

            df.columns = [
                str(col).strip()
                for col in df.columns
            ]

            return df.dropna(
                how="all"
            )

        except Exception as e:
            logger.error(
                f"Erreur normalisation dataframe : {e}"
            )
            return pd.DataFrame()

    def _empty_signal(self) -> Dict:

        return {
            "signal": "BUY & SELL",
            "emoji": "⚖️",
            "direction": "NEUTRAL",
            "conviction": 0,

            "technical_score": 0,
            "ai_score": 0,
            "trend_score": 0,
            "risk_score": 0,

            "entry_price": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "rr_ratio": 0,

            "analysis": {},
            "comments": "Données insuffisantes."
        }

    def _get_value(
        self,
        row,
        column
    ):

        try:
            if column not in row.index:
                return None

            value = row[column]

            if pd.isna(value):
                return None

            return float(value)

        except Exception:
            return None

     def _generate_comments(
        self,
        signal,
        conviction,
        technical,
        ai,
        trend,
        rr
    ) -> str:

        return (
            f"Signal {signal} avec une conviction de "
            f"{conviction}/100. "
            f"Technique: {technical}/40, "
            f"IA: {ai}/30, "
            f"Tendance: {trend}/20, "
            f"Risk Reward: {rr}."
        )
        
