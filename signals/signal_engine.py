"""
Moteur de signaux professionnels pour Trading AI Platform V2.

Génération de signaux :
- STRONG BUY
- BUY
- BUY & SELL
- SELL
- STRONG SELL

Score de conviction : 0 - 100

Pondération :
- Analyse technique : 40 points
- Analyse IA : 30 points
- Analyse tendance : 20 points
- Risk / Reward : 10 points

Compatible Python 3.14
"""

import logging
from typing import Dict, Any

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class SignalEngine:
    """
    Moteur principal de génération de signaux.
    """

    TECH_WEIGHT = 40
    AI_WEIGHT = 30
    TREND_WEIGHT = 20
    RR_WEIGHT = 10


    @staticmethod
    def generate_signal(
        df: pd.DataFrame,
        ai_prediction: float | None = None
    ) -> Dict[str, Any]:
        """
        Génère un signal complet.

        Args:
            df:
                DataFrame contenant les données marché
                avec indicateurs techniques.

            ai_prediction:
                prédiction IA entre -1 et +1
                (-1 bearish, +1 bullish)

        Returns:
            dictionnaire signal complet
        """

        if df is None or df.empty:
            return SignalEngine._empty_signal()


        try:

            technical = SignalEngine.analyze_technical(df)

            ai = SignalEngine.analyze_ai(
                ai_prediction
            )

            trend = SignalEngine.analyze_trend(df)

            risk = SignalEngine.analyze_risk_reward(df)


            total_score = (
                technical["score"]
                + ai["score"]
                + trend["score"]
                + risk["score"]
            )


            conviction = int(
                np.clip(total_score, 0, 100)
            )


            signal = SignalEngine._classify_signal(
                conviction,
                technical,
                ai,
                trend
            )


            last_price = float(
                df["Close"].iloc[-1]
            )


            return {

                "signal": signal["name"],

                "emoji": signal["emoji"],

                "direction": signal["direction"],

                "conviction": conviction,

                "technical_score":
                    technical["score"],

                "ai_score":
                    ai["score"],

                "trend_score":
                    trend["score"],

                "risk_score":
                    risk["score"],

                "entry_price":
                    last_price,

                "stop_loss":
                    risk["stop_loss"],

                "take_profit":
                    risk["take_profit"],

                "rr_ratio":
                    risk["rr_ratio"],

                "analysis": {

                     "technical":
                         technical["comment"],

                     "ai":
                         ai["comment"],

                     "trend":
                         trend["comment"],

                     "risk":
                         risk["comment"]

                  },

                  "comments": [
                     technical["comment"],
                     ai["comment"],
                     trend["comment"],
                     risk["comment"]
                  ]

                  }




        except Exception as e:

            logger.error(
                f"Erreur génération signal : {e}"
            )

            return SignalEngine._empty_signal()



    @staticmethod
    def analyze_technical(
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyse indicateurs techniques.
        Maximum 40 points.
        """

        score = 20

        comment = []


        try:

            close = df["Close"].iloc[-1]


            rsi = (
                df["RSI"].iloc[-1]
                if "RSI" in df.columns
                else 50
            )


            macd = (
                df["MACD"].iloc[-1]
                if "MACD" in df.columns
                else 0
            )


            if rsi < 30:

                score += 10
                comment.append(
                    "RSI survendu"
                )


            elif rsi > 70:

                score -= 10
                comment.append(
                    "RSI suracheté"
                )


            else:

                comment.append(
                    "RSI neutre"
                )


            if macd > 0:

                score += 10
                comment.append(
                    "MACD positif"
                )

            else:

                score -= 5
                comment.append(
                    "MACD négatif"
                )


            score = int(
                np.clip(score,0,40)
            )


            return {

                "score": score,

                "comment":
                    " | ".join(comment)

            }


        except Exception:

            return {

                "score":20,

                "comment":
                    "Analyse technique neutre"

            }



    @staticmethod
    def analyze_ai(
        prediction: float | None
    ) -> Dict[str, Any]:
        """
        Analyse IA.
        Maximum 30 points.
        """

        if prediction is None:

            return {

                "score":15,

                "comment":
                    "Pas de prédiction IA"

            }


        try:

            prediction = float(
                prediction
            )


            score = int(
                15 + prediction * 15
            )


            score = int(
                np.clip(score,0,30)
            )


            if prediction > 0.4:

                comment = (
                    "IA fortement haussière"
                )


            elif prediction < -0.4:

                comment = (
                    "IA fortement baissière"
                )


            else:

                comment = (
                    "IA neutre"
                )


            return {

                "score":score,

                "comment":comment

            }


        except Exception:


            return {

                "score":15,

                "comment":
                    "IA indisponible"

            }



    @staticmethod
    def analyze_trend(
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyse tendance.
        Maximum 20 points.
        """

        score = 10


        try:


            if "Close" in df.columns:

                short = (
                    df["Close"]
                    .rolling(10)
                    .mean()
                    .iloc[-1]
                )


                long = (
                    df["Close"]
                    .rolling(30)
                    .mean()
                    .iloc[-1]
                )


                if short > long:

                    score += 10

                    comment = (
                        "Tendance haussière"
                    )

                else:

                    comment = (
                        "Tendance baissière"
                    )
                    score -= 5


            else:

                comment = (
                    "Données insuffisantes"
                )


            score = int(
                np.clip(score,0,20)
            )


            return {

                "score":score,

                "comment":comment

            }


        except Exception:


            return {

                "score":10,

                "comment":
                    "Tendance neutre"

            }



    @staticmethod
    def analyze_risk_reward(
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyse Risk Reward.
        Maximum 10 points.
        """

        try:

            price = float(
                df["Close"].iloc[-1]
            )


            stop_loss = round(
                price * 0.98,
                4
            )


            take_profit = round(
                price * 1.04,
                4
            )


            risk = price - stop_loss

            reward = take_profit - price


            rr = round(
                reward / risk,
                2
            )


            score = 10 if rr >= 2 else 5


            return {

                "score":score,

                "stop_loss":stop_loss,

                "take_profit":
                    take_profit,

                "rr_ratio":rr,

                "comment":
                    f"RR ratio {rr}"

            }


        except Exception:


            return {

                "score":5,

                "stop_loss":None,

                "take_profit":None,

                "rr_ratio":0,

                "comment":
                    "Risque non calculé"

            }



    @staticmethod
    def _classify_signal(
        conviction,
        technical,
        ai,
        trend
    ):

        if conviction >= 80:

            return {

                "name":
                    "STRONG BUY",

                "emoji":
                    "🟢",

                "direction":
                    "BUY"

            }


        if conviction >= 60:

            return {

                "name":
                    "BUY",

                "emoji":
                    "🔼",

                "direction":
                    "BUY"

            }


        if conviction <= 20:

            return {

                "name":
                    "STRONG SELL",

                "emoji":
                    "🔴",

                "direction":
                    "SELL"

            }


        if conviction <= 40:

            return {

                "name":
                    "SELL",

                "emoji":
                    "🔽",

                "direction":
                    "SELL"

            }


        return {

            "name":
                "BUY & SELL",

            "emoji":
                "⚖️",

            "direction":
                "NEUTRAL"

        }



    @staticmethod
    def _empty_signal():

        return {

            "signal":
                "BUY & SELL",

            "emoji":
                "⚖️",

            "direction":
                "NEUTRAL",

            "conviction":0,

            "technical_score":0,

            "ai_score":0,

            "trend_score":0,

            "risk_score":0,

            "entry_price":None,

            "stop_loss":None,

            "take_profit":None,

            "rr_ratio":0,

            "analysis":{}

        }
