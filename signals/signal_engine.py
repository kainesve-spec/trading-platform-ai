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
    # NORMALISATION DATAFRAME
    # =====================================================

    def _normalize_dataframe(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        """
        Normalisation du DataFrame avant analyse.

        Objectifs :
        - Vérifier que les données existent
        - Uniformiser les noms de colonnes
        - Convertir les colonnes OHLCV
        - Corriger les différences
          close / Close
        """

        try:

            if df is None:

                return pd.DataFrame()


            if not isinstance(
                df,
                pd.DataFrame
            ):

                return pd.DataFrame()



            df = df.copy()



            # Nettoyage noms colonnes

            df.columns = [

                str(col).strip()

                for col in df.columns

            ]



            # Conversion noms standards

            rename_map = {


                "open":
                    "Open",


                "high":
                    "High",


                "low":
                    "Low",


                "close":
                    "Close",


                "volume":
                    "Volume",



                "ema_12":
                    "EMA_12",


                "ema_26":
                    "EMA_26",


                "sma_20":
                    "SMA_20",


                "sma_50":
                    "SMA_50"

            }



            df = df.rename(
                columns=rename_map
            )



            # Suppression colonnes doubles

            df = df.loc[
                :,
                ~df.columns.duplicated()
            ]



            # Conversion numérique

            numeric_columns = [

                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "RSI",
                "MACD",
                "MACD_Signal",
                "ATR",
                "ADX",
                "EMA_12",
                "EMA_26"

            ]



            for col in numeric_columns:

                if col in df.columns:

                    df[col] = pd.to_numeric(
                        df[col],
                        errors="coerce"
                    )



            # Nettoyage valeurs infinies

            df = df.replace(
                [np.inf, -np.inf],
                np.nan
            )



            # Garder les lignes valides

            df = df.dropna(
                how="all"
            )



            return df



        except Exception as e:


            logger.error(
                f"Erreur normalisation DF : {e}"
            )


            return pd.DataFrame()
     # =====================================================
    # ANALYSE TECHNIQUE V2.2 PRO - 40 POINTS
    # =====================================================

    def analyze_technical(
        self,
        df: pd.DataFrame
    ) -> Tuple[int, str]:

        score = 0
        comments = []

        try:

            last = df.iloc[-1]


            close = self._get_value(
                last,
                "Close"
            )

            rsi = self._get_value(
                last,
                "RSI"
            )

            macd = self._get_value(
                last,
                "MACD"
            )

            macd_signal = self._get_value(
                last,
                "MACD_Signal"
            )

            ema12 = self._get_value(
                last,
                "EMA_12"
            )

            ema26 = self._get_value(
                last,
                "EMA_26"
            )

            stoch_k = self._get_value(
                last,
                "Stoch_K"
            )

            stoch_d = self._get_value(
                last,
                "Stoch_D"
            )

            bb_high = self._get_value(
                last,
                "BB_High"
            )

            bb_low = self._get_value(
                last,
                "BB_Low"
            )

            volume = self._get_value(
                last,
                "Volume"
            )

            obv = self._get_value(
                last,
                "OBV"
            )


            # ==========================
            # RSI - 8 points
            # ==========================

            if rsi is not None:

                if rsi < 30:

                    score += 8

                    comments.append(
                        "RSI survendu - potentiel rebond."
                    )

                elif 50 <= rsi <= 70:

                    score += 5

                    comments.append(
                        "RSI zone haussière."
                    )

                elif rsi > 70:

                    score -= 3

                    comments.append(
                        "RSI suracheté."
                    )

                else:

                    score += 2

                    comments.append(
                        "RSI neutre."
                    )


            # ==========================
            # MACD - 8 points
            # ==========================

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


            # ==========================
            # EMA Momentum - 8 points
            # ==========================

            if (
                ema12 is not None
                and ema26 is not None
            ):

                if ema12 > ema26:

                    score += 8

                    comments.append(
                        "Croisement EMA positif."
                    )

                else:

                    score -= 5

                    comments.append(
                        "Croisement EMA négatif."
                    )


            # ==========================
            # Stochastique - 5 points
            # ==========================

            if (
                stoch_k is not None
                and stoch_d is not None
            ):

                if stoch_k > stoch_d:

                    score += 5

                    comments.append(
                        "Stochastique haussier."
                    )

                else:

                    score -= 3

                    comments.append(
                        "Stochastique baissier."
                    )


            # ==========================
            # Bollinger - 6 points
            # ==========================

            if (
                close is not None
                and bb_high is not None
                and bb_low is not None
            ):

                if close <= bb_low:

                    score += 6

                    comments.append(
                        "Prix proche support Bollinger."
                    )

                elif close >= bb_high:

                    score -= 3

                    comments.append(
                        "Prix proche résistance Bollinger."
                    )


            # ==========================
            # Volume / OBV - 5 points
            # ==========================

            if volume is not None:

                avg_volume = df["Volume"].rolling(
                    20
                ).mean().iloc[-1] if "Volume" in df.columns else None


                if avg_volume and volume > avg_volume:

                    score += 3

                    comments.append(
                        "Volume supérieur à la moyenne."
                    )


            if obv is not None:

                score += 2

                comments.append(
                    "Flux OBV disponible."
                )


            score = int(
                np.clip(
                    score,
                    0,
                    self.TECHNICAL_WEIGHT
                )
            )


            return (
                score,
                " ".join(comments)
            )


        except Exception as e:

            logger.error(
                f"Erreur analyse technique V2.2 : {e}"
            )

            return (
                20,
                "Analyse technique limitée."
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
    # CLASSIFICATION SIGNAL V2.2 PRO
    # =====================================================

    def _classify_signal(
        self,
        conviction: int
    ) -> Tuple[str, str, str]:


        if conviction >= 86:

            return (
                "PREMIUM BUY",
                "🚀",
                "BUY"
            )


        elif conviction >= 71:

            return (
                "STRONG BUY",
                "🟢",
                "BUY"
            )


        elif conviction >= 56:

            return (
                "BUY",
                "🔼",
                "BUY"
            )


        elif conviction >= 41:

            return (
                "BUY & SELL",
                "⚖️",
                "NEUTRAL"
            )


        elif conviction >= 26:

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
