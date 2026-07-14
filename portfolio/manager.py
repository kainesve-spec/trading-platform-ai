"""Géstion du portefeuille et des positions."""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PortfolioManager:
    """Géreur complet du portefeuille."""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = []
        self.trades_history = []
        self.last_update = datetime.now()
    
    def add_position(self, symbol: str, quantity: float, entry_price: float, 
                    stop_loss: float, take_profit: float, signal: str = "MANUAL") -> bool:
        """Ajouter une position au portefeuille."""
        try:
            position = {
                "id": len(self.positions) + 1,
                "symbol": symbol,
                "quantity": quantity,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "entry_time": datetime.now(),
                "status": "OPEN",
                "signal": signal,
                "profit_loss": 0,
                "profit_loss_pct": 0,
            }
            
            self.positions.append(position)
            logger.info(f"Position ajoutée: {symbol} x{quantity}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout position: {str(e)}")
            return False
    
    def close_position(self, position_id: int, exit_price: float) -> bool:
        """Fermer une position."""
        try:
            for pos in self.positions:
                if pos["id"] == position_id:
                    entry_cost = pos["quantity"] * pos["entry_price"]
                    exit_value = pos["quantity"] * exit_price
                    profit_loss = exit_value - entry_cost
                    profit_loss_pct = (profit_loss / entry_cost) * 100 if entry_cost > 0 else 0
                    
                    pos["exit_price"] = exit_price
                    pos["exit_time"] = datetime.now()
                    pos["status"] = "CLOSED"
                    pos["profit_loss"] = profit_loss
                    pos["profit_loss_pct"] = profit_loss_pct
                    
                    self.trades_history.append(pos.copy())
                    self.current_capital += profit_loss
                    
                    logger.info(f"Position fermée: {pos['symbol']} P/L: {profit_loss:.2f}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur fermeture position: {str(e)}")
            return False
    
    def update_position_price(self, position_id: int, current_price: float):
        """Mettre à jour le prix actuel d'une position."""
        try:
            for pos in self.positions:
                if pos["id"] == position_id and pos["status"] == "OPEN":
                    entry_cost = pos["quantity"] * pos["entry_price"]
                    current_value = pos["quantity"] * current_price
                    
                    pos["current_price"] = current_price
                    pos["profit_loss"] = current_value - entry_cost
                    pos["profit_loss_pct"] = (pos["profit_loss"] / entry_cost) * 100 if entry_cost > 0 else 0
                    
        except Exception as e:
            logger.error(f"Erreur mise à jour prix: {str(e)}")
    
    def get_portfolio_stats(self) -> Dict:
        """Obtenir les statistiques du portefeuille."""
        try:
            open_positions = [p for p in self.positions if p["status"] == "OPEN"]
            closed_trades = [t for t in self.trades_history]
            
            total_profit_loss = sum([t.get("profit_loss", 0) for t in closed_trades])
            total_profit_loss += sum([p.get("profit_loss", 0) for p in open_positions])
            
            total_profit_loss_pct = (total_profit_loss / self.initial_capital) * 100 if self.initial_capital > 0 else 0
            
            wins = len([t for t in closed_trades if t.get("profit_loss", 0) > 0])
            losses = len([t for t in closed_trades if t.get("profit_loss", 0) < 0])
            win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            
            stats = {
                "open_positions": len(open_positions),
                "closed_trades": len(closed_trades),
                "current_capital": self.current_capital,
                "initial_capital": self.initial_capital,
                "total_profit_loss": total_profit_loss,
                "total_profit_loss_pct": total_profit_loss_pct,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "gross_profit": sum([t.get("profit_loss", 0) for t in closed_trades if t.get("profit_loss", 0) > 0]),
                "gross_loss": abs(sum([t.get("profit_loss", 0) for t in closed_trades if t.get("profit_loss", 0) < 0])),
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur stats portefeuille: {str(e)}")
            return {}
    
    def get_positions_df(self) -> pd.DataFrame:
        """Obtenir les positions en DataFrame."""
        try:
            if not self.positions:
                return pd.DataFrame()
            
            df = pd.DataFrame(self.positions)
            return df
            
        except Exception as e:
            logger.error(f"Erreur conversion positions: {str(e)}")
            return pd.DataFrame()
    
    def export_to_csv(self, filename: str = "portfolio.csv") -> bool:
        """Exporter le portefeuille en CSV."""
        try:
            df = self.get_positions_df()
            df.to_csv(filename, index=False)
            logger.info(f"Portefeuille exporté: {filename}")
            return True
        except Exception as e:
            logger.error(f"Erreur export CSV: {str(e)}")
            return False
