"""
Signal Engine V2.2 Pro
Trading AI Platform

Moteur professionnel de génération de signaux.

Signaux :
- STRONG BUY 🟢
- BUY 🔼
- BUY & SELL ⚖️
- SELL 🔽
- STRONG SELL 🔴

Score conviction :
- Analyse technique : 40
- Analyse IA : 30
- Analyse tendance : 20
- Risk Reward : 10
"""

import logging
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class SignalEngine:
    """
    Moteur principal de génération de signaux.
    Compatible actions, crypto et forex.
    """

    TECHNICAL_WEIGHT = 40
    AI_WEIGHT = 30
    TREND_WEIGHT = 20
    RISK_WEIGHT = 10


    # =====================================================
    # GENERATION PRINCIPALE
    # =====================================================

    def generate_signal(
        self,
        df: pd.DataFrame,
        ai_prediction: Optional[Union[float, Dict]] = None
    ) -> Dict:

        try:

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



            conviction = int(
                np.clip(
                    technical_score
                    + ai_score
                    + trend_score
                    + risk_score,
                    0,
                    100
                )
            )



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


                "entry_price":
                    risk_data["entry_price"],


                "stop_loss":
                    risk_data["stop_loss"],


                "take_profit":
                    risk_data["take_profit"],


                "rr_ratio":
                    risk_data["rr_ratio"],



                "analysis": {

                    "technical":
                        technical_analysis,


                    "ai":
                        ai_analysis,


                    "trend":
                        trend_analysis,


                    "risk_reward":
                        risk_data["analysis"]

                }

            }



        except Exception as e:

            logger.exception(
                f"Erreur génération signal : {e}"
            )

            return self._empty_signal()



    # =====================================================
    # NORMALISATION DES DONNEES
    # =====================================================

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


        # Uniformiser les noms de colonnes
        df.columns = [
            str(col).strip()
            for col in df.columns
        ]


        rename_map = {

            "close": "Close",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "volume": "Volume",

            "ema_12": "EMA_12",
            "ema_26": "EMA_26"

        }


        df = df.rename(
            columns=rename_map
        )


        return df.dropna(
            how="all"
        )


    except Exception as e:

        logger.error(
            f"Erreur normalisation DF : {e}"
        )

        return pd.DataFrame()
    # =====================================================
    # ANALYSE TECHNIQUE 40 POINTS
    # =====================================================

    def analyze_technical(
        self,
        df: pd.DataFrame
    ) -> Tuple[int, str]:

        score = 0
        comments = []


        try:

            # -----------------------------
            # RSI
            # -----------------------------

            rsi = self._get_indicator(
                df,
                [
                    "RSI",
                    "rsi"
                ]
            )


            if rsi is not None:

                if rsi < 30:

                    score += 6

                    comments.append(
                        "RSI survendu - potentiel rebond."
                    )


                elif rsi > 70:

                    score -= 4

                    comments.append(
                        "RSI suracheté - risque correction."
                    )


                else:

                    score += 3

                    comments.append(
                        "RSI zone neutre."
                    )



            # -----------------------------
            # MACD
            # -----------------------------

            macd = self._get_indicator(
                df,
                [
                    "MACD"
                ]
            )


            macd_signal = self._get_indicator(
                df,
                [
                    "MACD_Signal",
                    "MACD_signal"
                ]
            )


            if (
                macd is not None
                and macd_signal is not None
            ):


                if macd > macd_signal:

                    score += 8

                    comments.append(
                        "MACD haussier."
                    )


                else:

                    score -= 5

                    comments.append(
                        "MACD baissier."
                    )



            # -----------------------------
            # MOYENNES MOBILES
            # -----------------------------

            close = self._get_indicator(
                df,
                [
                    "Close"
                ]
            )


            ma_fast = self._get_indicator(
                df,
                [
                    "EMA_12",
                    "EMA12",
                    "EMA20",
                    "SMA_20"
                ]
            )


            ma_slow = self._get_indicator(
                df,
                [
                    "EMA_26",
                    "EMA26",
                    "EMA50",
                    "SMA_50"
                ]
            )



            if (
                close is not None
                and ma_fast is not None
                and ma_slow is not None
            ):


                if close > ma_fast > ma_slow:

                    score += 8

                    comments.append(
                        "Structure mobile haussière."
                    )


                elif close < ma_fast < ma_slow:

                    score -= 5

                    comments.append(
                        "Structure mobile baissière."
                    )



            # -----------------------------
            # BOLLINGER
            # -----------------------------

            bb_high = self._get_indicator(
                df,
                [
                    "BB_High",
                    "BB_Upper"
                ]
            )


            bb_low = self._get_indicator(
                df,
                [
                    "BB_Low",
                    "BB_Lower"
                ]
            )



            if (
                close is not None
                and bb_low is not None
                and close <= bb_low
            ):

                score += 4

                comments.append(
                    "Prix proche support Bollinger."
                )



            if (
                close is not None
                and bb_high is not None
                and close >= bb_high
            ):

                score -= 2

                comments.append(
                    "Prix proche résistance Bollinger."
                )



            # -----------------------------
            # VOLUME
            # -----------------------------

            volume = self._get_indicator(
                df,
                [
                    "Volume"
                ]
            )


            if volume is not None and volume > 0:

                score += 2

                comments.append(
                    "Volume disponible."
                )



            score = int(
                np.clip(
                    score,
                    0,
                    self.TECHNICAL_WEIGHT
                )
            )



            if not comments:

                comments.append(
                    "Analyse technique limitée."
                )



            return (
                score,
                " ".join(comments)
            )



        except Exception as e:

            logger.error(
                f"Erreur analyse technique : {e}"
            )


            return (
                0,
                "Analyse technique indisponible."
            )
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



            if isinstance(
                ai_prediction,
                dict
            ):


                probability = (
                    ai_prediction.get(
                        "probability"
                    )
                )


                direction = (
                    ai_prediction.get(
                        "prediction"
                    )
                )



            else:

                probability = float(
                    ai_prediction
                )



            if probability is not None:


                probability = float(
                    probability
                )



                # Cas probabilité entre 0 et 1

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
    ) -> Tuple[int, str]:

        score = 0
        comments = []


        try:


            close = self._get_indicator(
                df,
                [
                    "Close"
                ]
            )


            ema_short = self._get_indicator(
                df,
                [
                    "EMA_12",
                    "EMA12",
                    "EMA20",
                    "SMA_20"
                ]
            )


            ema_long = self._get_indicator(
                df,
                [
                    "EMA_26",
                    "EMA26",
                    "EMA50",
                    "SMA_50"
                ]
            )


            ema_200 = self._get_indicator(
                df,
                [
                    "EMA_200",
                    "EMA200",
                    "SMA_200"
                ]
            )


            adx = self._get_indicator(
                df,
                [
                    "ADX",
                    "adx"
                ]
            )



            # Tendance court terme

            if (
                close is not None
                and ema_short is not None
            ):


                if close > ema_short:

                    score += 5

                    comments.append(
                        "Tendance court terme haussière."
                    )


                else:

                    score -= 3

                    comments.append(
                        "Tendance court terme baissière."
                    )



            # Tendance moyenne

            if (
                close is not None
                and ema_long is not None
            ):


                if close > ema_long:

                    score += 5

                    comments.append(
                        "Prix au-dessus moyenne mobile."
                    )


                else:

                    score -= 3



            # Tendance longue

            if (
                close is not None
                and ema_200 is not None
            ):


                if close > ema_200:

                    score += 4

                    comments.append(
                        "Tendance long terme positive."
                    )



            # Force tendance ADX

            if adx is not None:


                if adx > 25:

                    score += 4

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



            if not comments:

                comments.append(
                    "Tendance non déterminée."
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
                0,
                "Tendance indisponible."
            )
    # =====================================================
    # ANALYSE RISK / REWARD 10 POINTS
    # =====================================================

    def analyze_risk_reward(
        self,
        df: pd.DataFrame,
        technical_score: int,
        trend_score: int
    ) -> Tuple[int, Dict]:


        try:


            close = self._get_indicator(
                df,
                [
                    "Close"
                ]
            )


            if close is None:

                return (
                    0,
                    {
                        "entry_price": 0,
                        "stop_loss": 0,
                        "take_profit": 0,
                        "rr_ratio": 0,
                        "analysis":
                            "Prix indisponible."
                    }
                )



            atr = self._get_indicator(
                df,
                [
                    "ATR",
                    "atr",
                    "Average_True_Range"
                ]
            )



            if atr is None or atr <= 0:

                atr = close * 0.02



            # Détermination du sens

            bullish = (
                technical_score
                +
                trend_score
            ) >= 35



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



            if risk > 0:

                rr_ratio = (
                    reward / risk
                )

            else:

                rr_ratio = 0



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



            return (

                score,

                {

                    "entry_price":
                        round(close, 4),


                    "stop_loss":
                        round(stop_loss, 4),


                    "take_profit":
                        round(take_profit, 4),


                    "rr_ratio":
                        round(rr_ratio, 2),


                    "analysis":
                        (
                            f"Ratio Risk Reward "
                            f"{round(rr_ratio,2)}"
                        )

                }

            )



        except Exception as e:


            logger.error(
                f"Erreur Risk Reward : {e}"
            )


            return (

                0,

                {

                    "entry_price": 0,

                    "stop_loss": 0,

                    "take_profit": 0,

                    "rr_ratio": 0,

                    "analysis":
                        "Risk Reward indisponible."

                }

            )




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
    # LECTURE INDICATEURS INTELLIGENTE
    # =====================================================

    def _get_indicator(
        self,
        df: pd.DataFrame,
        columns: list
    ):

        """
        Recherche automatiquement une valeur
        parmi plusieurs noms possibles.

        Exemple :
        EMA_12 / EMA12 / EMA20
        RSI / rsi
        Close / close
        """

        try:

            if df.empty:

                return None



            last = df.iloc[-1]



            for column in columns:


                if column in last.index:


                    value = last[column]



                    if pd.isna(value):

                        continue



                    return float(value)



            return None



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



            "analysis":

                {


                    "technical":

                        "N/A",


                    "ai":

                        "N/A",


                    "trend":

                        "N/A",


                    "risk_reward":

                        "N/A"

                },



            "comments":

                "Données insuffisantes."

        }
