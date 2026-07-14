"""Configuration du logging pour la plateforme."""

import logging
import os
from config import LOGS_DIR, LOG_FORMAT, LOG_LEVEL


def setup_logging():
    """Configurer le logging de l'application."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    
    # Handler fichier
    fh = logging.FileHandler(f"{LOGS_DIR}/trading_ai.log")
    fh.setLevel(LOG_LEVEL)
    
    # Handler console
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
