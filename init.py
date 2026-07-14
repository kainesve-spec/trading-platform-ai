"""Script pour initialiser l'application."""

import os
import sys

def check_dependencies():
    """Vérifier que toutes les dépendances sont installées."""
    try:
        import streamlit
        import pandas
        import numpy
        import yfinance
        import sklearn
        import plotly
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Veuillez exécuter: pip install -r requirements.txt")
        return False

def create_directories():
    """Créer les répertoires nécessaires."""
    dirs = ['logs', 'models', 'data', '.streamlit']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("✅ Répertoires créés")

def main():
    """Initialiser l'application."""
    print("🚀 Initialisation de Trading AI Platform...")
    
    if not check_dependencies():
        sys.exit(1)
    
    create_directories()
    
    print("✅ Application prête!")
    print("👇 Lancez: streamlit run app.py")

if __name__ == "__main__":
    main()
