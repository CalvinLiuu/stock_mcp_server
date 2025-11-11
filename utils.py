"""
Shared utility functions for the stock market analyzer.
"""
import json
import os
from typing import Dict

# Portfolio file path
PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "data", "portfolio.json")

# Alerts file path
ALERTS_FILE = os.path.join(os.path.dirname(__file__), "data", "alerts.json")

# Sentiment history file path
SENTIMENT_FILE = os.path.join(os.path.dirname(__file__), "data", "sentiment_history.json")


def load_portfolio() -> Dict:
    """Load portfolio from JSON file."""
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {"holdings": {}, "transactions": []}


def save_portfolio(portfolio: Dict) -> None:
    """Save portfolio to JSON file."""
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)


def load_alerts() -> Dict:
    """Load alerts from JSON file."""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return {"price_alerts": [], "rsi_alerts": []}


def save_alerts(alerts: Dict) -> None:
    """Save alerts to JSON file."""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)


def load_sentiment_history() -> Dict:
    """Load sentiment history from JSON file."""
    if os.path.exists(SENTIMENT_FILE):
        with open(SENTIMENT_FILE, 'r') as f:
            return json.load(f)
    return {"daily_scores": []}


def save_sentiment_history(history: Dict) -> None:
    """Save sentiment history to JSON file."""
    with open(SENTIMENT_FILE, 'w') as f:
        json.dump(history, f, indent=2)
