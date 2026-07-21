
"""
Signal Engine professionnel pour Trading AI Platform V2.

Génération de signaux :
- STRONG BUY 🟢
- BUY 🔼
- BUY & SELL ⚖️
- SELL 🔽
- STRONG SELL 🔴

Score de conviction :
0 - 100

Pondération :
- Analyse technique : 40 points
- Analyse IA : 30 points
- Analyse tendance : 20 points
- Risk Reward : 10 points
"""

import logging
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class SignalEngine:
    """
    Moteur principal de génération de signaux Trading AI Platform V2.
    """

    def __init__(self):
        self.last_analysis = {}

    # ==========================================================
    # FONCTION PRINCIPALE
    # ==========================================================

    def generate_signal(
        self,
        df: pd.DataFrame,
        ai_prediction: float | None = None
    ) -> Dict:
        """
        Génère un signal complet exploitable par monitoring.py.
        """

        try:
            df = self._normalize_dataframe(df)

            if df.empty or "Close" not in df.columns:
                return self._empty_signal()

            technical = self.analyze_technical(df)
            ai = self.analyze_ai(ai_prediction)
            trend = self.analyze_trend(df)
            risk = self.analyze_risk_reward(df)

            coherence_bonus = self.check_coherence(
                ai_prediction,
                trend["score"]
            )

            total_score = (
                technical["score"]
                + ai["score"]
                + trend["score"]
                + risk["score"]
                + coherence_bonus
            )

            total_score = max(0, min(100, total_score))

            signal, emoji, direction = self._classify_signal(
                total_score
            )

            entry_price = risk["entry_price"]
            stop_loss = risk["stop_loss"]
            take_profit = risk["take_profit"]

            result = {
                "signal": signal,
                "emoji": emoji,
                "direction": direction,
                "conviction": total_score,

                "technical_score": technical["score"],
                "ai_score": ai["score"],
                "trend_score": trend["score"],
                "risk_score": risk["score"],

                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "rr_ratio": risk["rr_ratio"],

                "analysis": {
                    "technical": technical["comment"],
                    "ai": ai["comment"],
                    "trend": trend["comment"],
                    "risk_reward": risk["comment"]
                },

                "comments": [
                    technical["comment"],
                    ai["comment"],
                    trend["comment"],
                    risk["comment"]
                ]
            }

            self.last_analysis = result

            return result

        except Exception as exc:
            logger.exception(
                "Erreur génération signal : %s",
                exc
            )
            return self._empty_signal()

    # ==========================================================
    # ANALYSE TECHNIQUE
    # ==========================================================

    def analyze_technical(
        self,
        df: pd.DataFrame
    ) -> Dict:

        score = 0
        comments = []

        try:

            close = df["Close"]

            # RSI
            if "RSI" in df.columns:
                rsi = float(df["RSI"].iloc[-1])

                if rsi < 30:
                    score += 12
                    comments.append(
                        "RSI survendu : opportunité acheteuse"
                    )

                elif rsi > 70:
                    score -= 12
                    comments.append(
                        "RSI suracheté : pression vendeuse"
                    )

                else:
                    score += 5

            # MACD
            if "MACD" in df.columns:

                macd = df["MACD"].iloc[-1]

                if macd > 0:
                    score += 10
                    comments.append(
                        "MACD positif"
                    )

                else:
                    score -= 5
                    comments.append(
                        "MACD négatif"
                    )

            # ADX
            if "ADX" in df.columns:

                adx = float(df["ADX"].iloc[-1])

                if adx > 25:
                    score += 8
                    comments.append(
                        "Tendance forte détectée"
                    )

            # EMA
            if "EMA" in df.columns:

                if close.iloc[-1] > df["EMA"].iloc[-1]:
                    score += 5

            # SMA
            if "SMA" in df.columns:

                if close.iloc[-1] > df["SMA"].iloc[-1]:
                    score += 5


            score = max(0, min(40, score))

            return {
                "score": score,
                "comment": " | ".join(comments)
                if comments
                else "Analyse technique neutre"
            }

        except Exception as exc:

        logger.error(
            "Erreur analyse tendance V2 : %s",
            exc
        )

        return {
            "score": 0,
            "comment": "Analyse tendance indisponible"
        }

    # ==========================================================
    # ANALYSE IA
    # ==========================================================

    def analyze_ai(
        self,
        ai_prediction: float | None
    ) -> Dict:

        try:

            if ai_prediction is None:

                return {
                    "score": 15,
                    "comment":
                    "Aucune prédiction IA disponible"
                }

            prediction = max(
                -1,
                min(1, float(ai_prediction))
            )

            score = int(
                ((prediction + 1) / 2) * 30
            )

            if prediction > 0.5:

                comment = (
                    "IA fortement haussière"
                )

            elif prediction < -0.5:

                comment = (
                    "IA fortement baissière"
                )

            else:

                comment = (
                    "IA neutre"
                )

            return {
                "score": score,
                "comment": comment
            }

        except Exception as exc:

            logger.error(
                "Erreur analyse IA : %s",
                exc
            )

            return {
                "score": 15,
                "comment":
                "Erreur analyse IA"
            }

    # ==========================================================
    # ANALYSE TENDANCE
    # ==========================================================

      def analyze_trend(
        self,
        df: pd.DataFrame
    ) -> Dict:

        score = 0
        comments = []

        try:

            if df.empty or "Close" not in df.columns:
                return {
                    "score": 0,
                    "comment": "Données insuffisantes pour analyser la tendance"
                }

            close = float(df["Close"].iloc[-1])

            sma = None
            ema = None


            if "SMA" in df.columns:

                sma = float(df["SMA"].iloc[-1])

                if close > sma:
                    score += 5
                    comments.append("Prix au-dessus de la SMA")
                else:
                    score -= 2
                    comments.append("Prix sous la SMA")


            if "EMA" in df.columns:

                ema = float(df["EMA"].iloc[-1])

                if close > ema:
                    score += 5
                    comments.append("Prix au-dessus de l'EMA")
                else:
                    score -= 2
                    comments.append("Prix sous l'EMA")


            if sma is not None and ema is not None:

                if ema > sma:
                    score += 3
                    comments.append("EMA supérieure à SMA")
                else:
                    score -= 1
                    comments.append("EMA inférieure à SMA")


            if "MACD" in df.columns:

                macd = float(df["MACD"].iloc[-1])

                if macd > 0:
                    score += 4
                    comments.append("MACD haussier")
                else:
                    score -= 3
                    comments.append("MACD baissier")


            if "ADX" in df.columns:

                adx = float(df["ADX"].iloc[-1])

                if adx >= 25:
                    score += 3
                    comments.append("ADX tendance forte")


            score = max(0, min(20, score))


            if score >= 15:
                trend_comment = "Tendance fortement haussière"

            elif score >= 10:
                trend_comment = "Tendance légèrement haussière"

            elif score <= 5:
                trend_comment = "Tendance baissière ou faible"

            else:
                trend_comment = "Tendance neutre"


            return {
                "score": score,
                "comment": trend_comment + " | " + " | ".join(comments)
            }


        except Exception as exc:

            logger.error(
                "Erreur analyse tendance V2 : %s",
                exc
            )

            return {
                "score": 0,
                "comment": "Analyse tendance indisponible"
            
    # ==========================================================
    # RISK REWARD
    # ==========================================================

    def analyze_risk_reward(
        self,
        df: pd.DataFrame
    ) -> Dict:

        try:

            entry = float(
                df["Close"].iloc[-1]
            )

            stop_loss = entry * 0.98

            take_profit = entry * 1.04

            risk = entry - stop_loss

            reward = take_profit - entry

            rr_ratio = (
                reward / risk
                if risk > 0
                else 0
            )

            score = 10 if rr_ratio >= 2 else 5

            return {

                "score": score,

                "entry_price": round(
                    entry,
                    6
                ),

                "stop_loss": round(
                    stop_loss,
                    6
                ),

                "take_profit": round(
                    take_profit,
                    6
                ),

                "rr_ratio": round(
                    rr_ratio,
                    2
                ),

                "comment":
                f"Ratio risque/rendement {rr_ratio:.2f}"

            }


        except Exception as exc:

            logger.error(
                "Erreur Risk Reward : %s",
                exc
            )

            return {

                "score": 0,

                "entry_price": 0,

                "stop_loss": 0,

                "take_profit": 0,

                "rr_ratio": 0,

                "comment":
                "Risk Reward indisponible"

            }

    # ==========================================================
    # COHERENCE IA / TENDANCE
    # ==========================================================

    def check_coherence(
        self,
        ai_prediction: Optional[float],
        trend_score: int
    ) -> int:

        try:

            if ai_prediction is None:
                return 0


            if ai_prediction > 0 and trend_score >= 10:

                return 10


            if ai_prediction < 0 and trend_score <= 5:

                return 10


            if (
                ai_prediction > 0
                and trend_score <= 5
            ):

                return -10


            if (
                ai_prediction < 0
                and trend_score >= 10
            ):

                return -10


            return 0


        except Exception:

            return 0

    # ==========================================================
    # CLASSIFICATION SIGNAL
    # ==========================================================

    def _classify_signal(
        self,
        conviction: int
    ) -> Tuple[str, str, str]:

        if conviction >= 80:

            return (
                "STRONG BUY",
                "🟢",
                "BUY"
            )

        if conviction >= 60:

            return (
                "BUY",
                "🔼",
                "BUY"
            )

        if conviction >= 40:

            return (
                "BUY & SELL",
                "⚖️",
                "NEUTRAL"
            )

        if conviction >= 20:

            return (
                "SELL",
                "🔽",
                "SELL"
            )

        return (
            "STRONG SELL",
            "🔴",
            "SELL"
        )

    # ==========================================================
    # SIGNAL VIDE
    # ==========================================================

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

            "comments": [
                "Données insuffisantes pour générer un signal"
            ]

        }

    # ==========================================================
    # NORMALISATION DATAFRAME
    # ==========================================================

    def _normalize_dataframe(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        try:

            if df is None:
                return pd.DataFrame()

            df = df.copy()

            mapping = {

                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close"

            }

            df.rename(
                columns={
                    k: v
                    for k, v in mapping.items()
                    if k in df.columns
                },
                inplace=True
            )

            return df


        except Exception as exc:

            logger.error(
                "Erreur normalisation dataframe : %s",
                exc
            )

            return pd.DataFrame()
