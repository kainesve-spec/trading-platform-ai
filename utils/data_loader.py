"""Utilitaires pour le chargement et le nettoyage des données."""

import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

from config import (
    YFINANCE_TIMEOUT,
    YFINANCE_RETRIES,
    MIN_DATA_POINTS
)


logger = logging.getLogger(__name__)


def load_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
    progress_callback=None
) -> Optional[pd.DataFrame]:
    """
    Charger les données de marché depuis Yahoo Finance.
    """

    try:

        if progress_callback:
            progress_callback(
                "Téléchargement des données..."
            )


        ticker = yf.Ticker(symbol)


        df = ticker.history(
            period=period,
            interval=interval,
            timeout=YFINANCE_TIMEOUT
        )


        if df is None or df.empty:

            logger.error(
                f"Aucune donnée pour {symbol}"
            )

            return None



        df = clean_data(
            df,
            symbol
        )


        if df is None or df.empty:

            logger.error(
                f"Données invalides après nettoyage : {symbol}"
            )

            return None



        if len(df) < MIN_DATA_POINTS:

            logger.warning(
                f"Données insuffisantes pour {symbol}: {len(df)} points"
            )

            return None



        logger.info(
            f"Données chargées: {symbol} ({len(df)} candles)"
        )


        return df



    except Exception as e:

        logger.error(
            f"Erreur chargement {symbol}: {str(e)}"
        )

        return None




def clean_data(
    df: pd.DataFrame,
    symbol: str = ""
) -> pd.DataFrame:
    """
    Nettoyer et valider les données OHLCV.
    """

    try:

        if df is None or df.empty:

            return pd.DataFrame()



        df = df.copy()



        # Transformer index date en colonne

        if isinstance(
            df.index,
            pd.DatetimeIndex
        ):

            df = df.reset_index()



        # Normalisation des noms

        df.columns = [
            str(col).lower()
            for col in df.columns
        ]



        # Supprimer colonnes dupliquées

        df = df.loc[
            :,
            ~df.columns.duplicated()
        ]



        expected_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]



        for col in expected_cols:

            if col not in df.columns:

                if col == "volume":

                    df[col] = 0

                else:

                    df[col] = np.nan




        # Doublons

        if "date" in df.columns:

            df = df.drop_duplicates(
                subset=["date"],
                keep="last"
            )



        # Valeurs invalides

        df = df.replace(
            [np.inf, -np.inf],
            np.nan
        )



        # Correction pandas récente
        # Ancien : fillna(method="ffill")

        df = df.ffill()

        df = df.bfill()



        # Conversion OHLC

        for col in [
            "open",
            "high",
            "low",
            "close"
        ]:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

                df[col] = df[col].clip(
                    lower=0
                )



        # Volume

        if "volume" in df.columns:

            df["volume"] = pd.to_numeric(
                df["volume"],
                errors="coerce"
            )

            df["volume"] = df["volume"].clip(
                lower=0
            )

            df["volume"] = df["volume"].fillna(
                0
            )



        # Cohérence High / Low

        if all(
            col in df.columns
            for col in [
                "high",
                "low",
                "close",
                "open"
            ]
        ):

            df["high"] = df[
                [
                    "high",
                    "low",
                    "close",
                    "open"
                ]
            ].max(axis=1)



            df["low"] = df[
                [
                    "high",
                    "low",
                    "close",
                    "open"
                ]
            ].min(axis=1)



        # Supprimer lignes sans prix

        df = df.dropna(
            subset=["close"]
        )



        # Trier par date

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"]
            )

            df = df.sort_values(
                "date"
            )


        df = df.reset_index(
            drop=True
        )


        return df



    except Exception as e:

        logger.error(
            f"Erreur lors du nettoyage: {str(e)}"
        )

        return df




def validate_data(
    df: pd.DataFrame
) -> Tuple[bool, str]:
    """
    Valider la qualité des données.
    """

    try:

        if df is None or df.empty:

            return False, "❌ DataFrame vide"



        if len(df) < MIN_DATA_POINTS:

            return False, "❌ Données insuffisantes"



        required_cols = [
            "open",
            "high",
            "low",
            "close"
        ]



        missing_cols = [
            col
            for col in required_cols
            if col not in df.columns
        ]



        if missing_cols:

            return False, "❌ Colonnes manquantes"



        return True, "✅ Données valides"



    except Exception:

        return False, "❌ Erreur validation"




def get_data_quality_score(
    df: pd.DataFrame
) -> float:
    """
    Calculer un score qualité des données 0-100.
    """

    try:

        if df is None or df.empty:

            return 0.0



        score = 100.0



        nan_percent = (
            df.isna()
            .sum()
            .sum()
            /
            (len(df) * len(df.columns))
            * 100
        )



        score -= nan_percent * 0.5



        if len(df) < 100:

            score -= 10



        return max(
            0,
            min(
                100,
                score
            )
        )



    except Exception:

        return 0.0
