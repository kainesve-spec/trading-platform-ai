"""
Signal Engine V2.1 Pro
Trading AI Platform

Génération de signaux :
- STRONG BUY 🟢
- BUY 🔼
- BUY & SELL ⚖️
- SELL 🔽
- STRONG SELL 🔴

Score conviction :
- Technique : 40
- IA : 30
- Tendance : 20
- Risk Reward : 10
"""

import logging
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class SignalEngine:

    TECHNICAL_WEIGHT = 40
    AI_WEIGHT = 30
    TREND_WEIGHT = 20
    RISK_WEIGHT = 10

    def __init__(self):
        self.logger = logger


    def generate_signal(
        self,
        df: pd.DataFrame,
        ai_prediction: Optional[Union[float, Dict]] = None
    ) -> Dict:

        try:
            print("VERSION SIGNAL ENGINE V2.1 ACTIVE")
            df = self._normalize_dataframe(df)

            if df.empty or "Close" not in df.columns:
                return self._empty_signal()


            technical_score, technical_analysis = (
                self.analyze_technical(df)
            )

            ai_score, ai_analysis = (
                self.analyze_ai(ai_prediction)
            )

            trend_score, trend_analysis = (
                self.analyze_trend(df)
            )

            risk_score, risk_data = (
                self.analyze_risk_reward(
                    df,
                    technical_score,
                    trend_score
                )
            )


            conviction = int(np.clip(
                technical_score
                + ai_score
                + trend_score
                + risk_score,
                0,
                100
            ))


            signal, emoji, direction = (
                self._classify_signal(
                    conviction
                )
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

                "entry_price": risk_data["entry_price"],
                "stop_loss": risk_data["stop_loss"],
                "take_profit": risk_data["take_profit"],

                "rr_ratio": risk_data["rr_ratio"],

                "analysis": {

                    "technical": technical_analysis,

                    "ai": ai_analysis,

                    "trend": trend_analysis,

                    "risk_reward":
                        risk_data["analysis"]
                }

            }


        except Exception as e:

            logger.exception(
                f"Erreur Signal Engine : {e}"
            )

            return self._empty_signal()



    # =====================================================
    # ANALYSE TECHNIQUE 40 POINTS
    # =====================================================

    def analyze_technical(
        self,
        df: pd.DataFrame
    ) -> Tuple[int,str]:

        score = 0
        comments = []

        try:

            last = df.iloc[-1]


            rsi = self._get_value(last,"RSI")
            macd = self._get_value(last,"MACD")
            macd_signal = self._get_value(
                last,
                "MACD_Signal"
            )

            close = self._get_value(
                last,
                "Close"
            )

            ema20 = self._get_value(
                last,
                "EMA20"
            )

            ema50 = self._get_value(
                last,
                "EMA50"
            )


            # RSI (8 points)

            if rsi is not None:

                if rsi < 30:

                    score += 5

                    comments.append(
                        "RSI survendu."
                    )

                elif rsi > 70:

                    score -= 5

                    comments.append(
                        "RSI suracheté."
                    )

                else:

                    score += 3



            # MACD (8 points)

            if (
                macd is not None
                and macd_signal is not None
            ):

                if macd > macd_signal:

                    score += 6

                    comments.append(
                        "MACD haussier."
                    )

                else:

                    score -= 4

                    comments.append(
                        "MACD baissier."
                    )



            # Moyennes mobiles (8 points)

            if (
                close
                and ema20
                and ema50
            ):

                if close > ema20 > ema50:

                    score += 8

                    comments.append(
                        "Structure EMA positive."
                    )

                elif close < ema20 < ema50:

                    score -= 6

                    comments.append(
                        "Structure EMA négative."
                    )


            score = int(np.clip(
                score,
                0,
                self.TECHNICAL_WEIGHT
            ))


            return score, " ".join(comments)



        except Exception as e:

            logger.error(
                f"Erreur technique : {e}"
            )

            return 20, "Analyse technique limitée."
    # =====================================================
    # ANALYSE IA 30 POINTS
    # =====================================================

    def analyze_ai(
        self,
        ai_prediction=None
    ) -> Tuple[int, str]:

        try:

            if ai_prediction is None:
                return (
                    15,
                    "Aucune prédiction IA disponible."
                )


            probability = None
            direction = None


            if isinstance(ai_prediction, dict):

                probability = ai_prediction.get(
                    "probability"
                )

                direction = ai_prediction.get(
                    "prediction"
                )


            else:

                probability = float(
                    ai_prediction
                )


            if probability is not None:

                probability = float(
                    probability
                )


                if probability >= 0.80:

                    return (
                        30,
                        "IA fortement haussière."
                    )

                elif probability >= 0.60:

                    return (
                        24,
                        "IA légèrement haussière."
                    )

                elif probability <= 0.20:

                    return (
                        30,
                        "IA fortement baissière."
                    )

                elif probability <= 0.40:

                    return (
                        10,
                        "IA légèrement baissière."
                    )


            if direction:

                direction = str(
                    direction
                ).upper()


                if direction == "BUY":

                    return (
                        25,
                        "IA signale un achat."
                    )

                if direction == "SELL":

                    return (
                        10,
                        "IA signale une vente."
                    )


            return (
                15,
                "IA neutre."
            )


        except Exception as e:

            logger.error(
                f"Erreur IA : {e}"
            )

            return (
                15,
                "IA indisponible."
            )



    # =====================================================
    # ANALYSE TENDANCE 20 POINTS
    # =====================================================

    def analyze_trend(
        self,
        df: pd.DataFrame
    ) -> Tuple[int,str]:

        score = 0
        comments = []

        try:

            last = df.iloc[-1]


            close = self._get_value(
                last,
                "Close"
            )

            ema50 = self._get_value(
                last,
                "EMA50"
            )

            ema200 = self._get_value(
                last,
                "EMA200"
            )

            adx = self._get_value(
                last,
                "ADX"
            )



            if close and ema50:

                if close > ema50:

                    score += 4

                    comments.append(
                        "Tendance court terme haussière."
                    )

                else:

                    score -= 4

                    comments.append(
                        "Tendance court terme baissière."
                    )



            if close and ema200:

                if close > ema200:

                    score += 4

                    comments.append(
                        "Tendance long terme positive."
                    )

                else:

                    score -= 4



            if adx:

                if adx > 25:

                    score += 2

                    comments.append(
                        "ADX confirme une tendance forte."
                    )



            score = int(
                np.clip(
                    score,
                    0,
                    self.TREND_WEIGHT
                )
            )


            return (
                score,
                " ".join(comments)
            )


        except Exception as e:

            logger.error(
                f"Erreur tendance : {e}"
            )

            return (
                10,
                "Tendance indisponible."
            )



    # =====================================================
    # RISK REWARD 10 POINTS
    # =====================================================

    def analyze_risk_reward(
        self,
        df: pd.DataFrame,
        technical_score: int,
        trend_score: int
    ) -> Tuple[int, Dict]:

        try:

            close = float(
                df["Close"].iloc[-1]
            )


            atr = None

            atr_columns = [
                "ATR",
                "atr",
                "Average_True_Range"
            ]

            for col in atr_columns:

                if col in df.columns:

                    atr = float(
                        df[col].iloc[-1]
                    )

                    break


            if atr is None or np.isnan(atr):

                atr = close * 0.02



            bullish = (
                technical_score
                + trend_score
            ) >= 40



            if bullish:

                stop_loss = (
                    close - atr
                )

                take_profit = (
                    close + (atr * 2.5)
                )


            else:

                stop_loss = (
                    close + atr
                )

                take_profit = (
                    close - (atr * 2.5)
                )



            risk = abs(
                close - stop_loss
            )

            reward = abs(
                take_profit - close
            )



            rr_ratio = (

                reward / risk

                if risk > 0

                else 0

            )



            if rr_ratio >= 3:

                score = 10

            elif rr_ratio >= 2:

                score = 8

            elif rr_ratio >= 1.5:

                score = 6

            elif rr_ratio >= 1:

                score = 4

            else:

                score = 0



            return score, {

                "entry_price":
                    round(close,4),

                "stop_loss":
                    round(stop_loss,4),

                "take_profit":
                    round(take_profit,4),

                "rr_ratio":
                    round(rr_ratio,2),

                "analysis":
                    f"Ratio Risk Reward {round(rr_ratio,2)}"

            }



        except Exception as e:

            logger.error(
                f"Erreur Risk Reward : {e}"
            )


            return 0, {

                "entry_price":0,

                "stop_loss":0,

                "take_profit":0,

                "rr_ratio":0,

                "analysis":
                    "Risk Reward indisponible."

            }
    # =====================================================
    # CLASSIFICATION DU SIGNAL
    # =====================================================

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


        elif conviction >= 60:

            return (
                "BUY",
                "🔼",
                "BUY"
            )


        elif conviction >= 45:

            return (
                "BUY & SELL",
                "⚖️",
                "NEUTRAL"
            )


        elif conviction >= 30:

            return (
                "SELL",
                "🔽",
                "SELL"
            )


        else:

            return (
                "STRONG SELL",
                "🔴",
                "SELL"
            )



    # =====================================================
    # NORMALISATION DATAFRAME
    # =====================================================

    def _normalize_dataframe(
    self,
    df: pd.DataFrame
) -> pd.DataFrame:

    try:

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()

        # Renommer automatiquement les colonnes
        rename_map = {
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }

        df.rename(columns=rename_map, inplace=True)

        return df

    except Exception as e:

        logger.error(
            f"Erreur normalisation DF : {e}"
        )

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
                f"Erreur normalisation DF : {e}"
            )

            return pd.DataFrame()



    # =====================================================
    # VALEUR SECURISEE
    # =====================================================

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



    # =====================================================
    # SIGNAL VIDE
    # =====================================================

    def _empty_signal(
        self
    ) -> Dict:


        return {

            "signal":
                "BUY & SELL",

            "emoji":
                "⚖️",

            "direction":
                "NEUTRAL",


            "conviction":
                0,


            "technical_score":
                0,

            "ai_score":
                0,

            "trend_score":
                0,

            "risk_score":
                0,


            "entry_price":
                0,

            "stop_loss":
                0,

            "take_profit":
                0,


            "rr_ratio":
                0,


            "analysis": {},


            "comments":
                "Données insuffisantes."

        }



    # =====================================================
    # ANALYSE AVANCEE OPTIONNELLE
    # =====================================================

    def analyze_extra_indicators(
        self,
        df: pd.DataFrame
    ) -> Dict:


        """
        Analyse complémentaire :
        Bollinger
        Volume
        Momentum

        Peut être utilisée par
        analyze_technical()
        """

        result = {

            "bollinger":
                "Non disponible",

            "volume":
                "Non disponible",

            "momentum":
                "Non disponible"

        }


        try:

            last = df.iloc[-1]



            close = self._get_value(
                last,
                "Close"
            )


            upper = self._get_value(
                last,
                "BB_Upper"
            )


            lower = self._get_value(
                last,
                "BB_Lower"
            )


            volume = self._get_value(
                last,
                "Volume"
            )


            momentum = self._get_value(
                last,
                "Momentum"
            )



            if close and upper:

                if close >= upper:

                    result["bollinger"] = (
                        "Prix proche résistance Bollinger."
                    )


            if close and lower:

                if close <= lower:

                    result["bollinger"] = (
                        "Prix proche support Bollinger."
                    )



            if volume:

                result["volume"] = (
                    "Volume disponible."
                )



            if momentum:

                if momentum > 0:

                    result["momentum"] = (
                        "Momentum positif."
                    )

                else:

                    result["momentum"] = (
                        "Momentum négatif."
                    )


            return result



        except Exception as e:

            logger.error(
                f"Erreur indicateurs avancés : {e}"
            )


            return result
