"""
Alert system for price and technical indicator notifications.
"""
import yfinance as yf
from typing import Optional
from mcp.server.fastmcp import FastMCP
from utils import load_alerts, save_alerts


def register_alert_tools(mcp: FastMCP):
    """Register alert tools with the MCP server."""
    
    @mcp.tool()
    def set_price_alert(ticker: str, target_price: float, alert_type: str = "above", alert_name: Optional[str] = None) -> str:
        """
        Set a price alert for a stock. You'll be notified when checking alerts if the condition is met.

        Args:
            ticker: The stock ticker symbol (e.g., 'AAPL').
            target_price: The price to trigger the alert.
            alert_type: Type of alert - 'above' (price goes above target) or 'below' (price goes below target).
            alert_name: Optional custom name for the alert.

        Returns:
            Confirmation message with alert details.
        """
        try:
            ticker = ticker.upper()
            if alert_type not in ['above', 'below']:
                return "Invalid alert_type. Must be 'above' or 'below'."
            
            # Get current price for reference
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            if not current_price:
                return f"Could not fetch current price for {ticker}. Please verify the ticker symbol."
            
            alerts = load_alerts()
            
            alert = {
                "ticker": ticker,
                "target_price": target_price,
                "alert_type": alert_type,
                "current_price": current_price,
                "alert_name": alert_name or f"{ticker} price {alert_type} ${target_price}",
                "status": "active"
            }
            
            alerts["price_alerts"].append(alert)
            save_alerts(alerts)
            
            return f"✅ Price alert set for {ticker}: Notify when price goes {alert_type} ${target_price:.2f} (Current: ${current_price:.2f})"
        
        except Exception as e:
            return f"Error setting price alert: {e}"

    @mcp.tool()
    def set_rsi_alert(ticker: str, rsi_threshold: float, alert_type: str = "above", alert_name: Optional[str] = None) -> str:
        """
        Set an RSI alert for a stock. Useful for overbought (RSI > 70) or oversold (RSI < 30) notifications.

        Args:
            ticker: The stock ticker symbol (e.g., 'TSLA').
            rsi_threshold: The RSI value to trigger the alert (0-100).
            alert_type: Type of alert - 'above' (RSI goes above threshold) or 'below' (RSI goes below threshold).
            alert_name: Optional custom name for the alert.

        Returns:
            Confirmation message with alert details.
        """
        try:
            ticker = ticker.upper()
            if alert_type not in ['above', 'below']:
                return "Invalid alert_type. Must be 'above' or 'below'."
            
            if not (0 <= rsi_threshold <= 100):
                return "RSI threshold must be between 0 and 100."
            
            # Calculate current RSI for reference
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if len(hist) < 15:
                return f"Not enough data to calculate RSI for {ticker}."
            
            # Calculate RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            alerts = load_alerts()
            
            alert = {
                "ticker": ticker,
                "rsi_threshold": rsi_threshold,
                "alert_type": alert_type,
                "current_rsi": round(current_rsi, 2),
                "alert_name": alert_name or f"{ticker} RSI {alert_type} {rsi_threshold}",
                "status": "active"
            }
            
            alerts["rsi_alerts"].append(alert)
            save_alerts(alerts)
            
            return f"✅ RSI alert set for {ticker}: Notify when RSI goes {alert_type} {rsi_threshold:.0f} (Current RSI: {current_rsi:.2f})"
        
        except Exception as e:
            return f"Error setting RSI alert: {e}"

    @mcp.tool()
    def check_alerts() -> str:
        """
        Check all active alerts and see which ones have been triggered.

        Returns:
            Summary of triggered alerts and all active alerts.
        """
        try:
            alerts = load_alerts()
            
            if not alerts["price_alerts"] and not alerts["rsi_alerts"]:
                return "No alerts configured. Use set_price_alert() or set_rsi_alert() to create alerts."
            
            result = "🔔 ALERT STATUS CHECK\n"
            result += "="*70 + "\n\n"
            
            triggered = []
            
            # Check price alerts
            if alerts["price_alerts"]:
                result += "💰 PRICE ALERTS\n"
                for i, alert in enumerate(alerts["price_alerts"]):
                    if alert["status"] != "active":
                        continue
                    
                    ticker = alert["ticker"]
                    stock = yf.Ticker(ticker)
                    current_price = stock.info.get('regularMarketPrice', 0)
                    
                    if current_price:
                        target = alert["target_price"]
                        alert_type = alert["alert_type"]
                        
                        is_triggered = (
                            (alert_type == "above" and current_price >= target) or
                            (alert_type == "below" and current_price <= target)
                        )
                        
                        if is_triggered:
                            status = "🔴 TRIGGERED!"
                            triggered.append(alert["alert_name"])
                            alerts["price_alerts"][i]["status"] = "triggered"
                        else:
                            status = "🟢 Active"
                        
                        result += f"   {status} - {alert['alert_name']}\n"
                        result += f"      Target: ${target:.2f} ({alert_type}) | Current: ${current_price:.2f}\n"
                    else:
                        result += f"   ⚠️ Could not check - {alert['alert_name']}\n"
                
                result += "\n"
            
            # Check RSI alerts
            if alerts["rsi_alerts"]:
                result += "📊 RSI ALERTS\n"
                for i, alert in enumerate(alerts["rsi_alerts"]):
                    if alert["status"] != "active":
                        continue
                    
                    ticker = alert["ticker"]
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="3mo")
                    
                    if len(hist) >= 15:
                        # Calculate current RSI
                        delta = hist['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        current_rsi = rsi.iloc[-1]
                        
                        threshold = alert["rsi_threshold"]
                        alert_type = alert["alert_type"]
                        
                        is_triggered = (
                            (alert_type == "above" and current_rsi >= threshold) or
                            (alert_type == "below" and current_rsi <= threshold)
                        )
                        
                        if is_triggered:
                            status = "🔴 TRIGGERED!"
                            triggered.append(alert["alert_name"])
                            alerts["rsi_alerts"][i]["status"] = "triggered"
                        else:
                            status = "🟢 Active"
                        
                        result += f"   {status} - {alert['alert_name']}\n"
                        result += f"      Threshold: {threshold:.0f} ({alert_type}) | Current RSI: {current_rsi:.2f}\n"
                    else:
                        result += f"   ⚠️ Could not check - {alert['alert_name']}\n"
                
                result += "\n"
            
            # Save any status updates
            save_alerts(alerts)
            
            # Summary
            if triggered:
                result += "="*70 + "\n"
                result += f"🚨 {len(triggered)} ALERT(S) TRIGGERED!\n"
                for alert_name in triggered:
                    result += f"   • {alert_name}\n"
            else:
                result += "="*70 + "\n"
                result += "✅ No alerts triggered at this time.\n"
            
            return result
        
        except Exception as e:
            return f"Error checking alerts: {e}"

    @mcp.tool()
    def list_alerts() -> str:
        """
        List all configured alerts (active and triggered).

        Returns:
            Summary of all alerts.
        """
        try:
            alerts = load_alerts()
            
            if not alerts["price_alerts"] and not alerts["rsi_alerts"]:
                return "No alerts configured. Use set_price_alert() or set_rsi_alert() to create alerts."
            
            result = "📋 ALL CONFIGURED ALERTS\n"
            result += "="*70 + "\n\n"
            
            # Price alerts
            if alerts["price_alerts"]:
                result += "💰 PRICE ALERTS\n"
                for alert in alerts["price_alerts"]:
                    status_emoji = "🟢" if alert["status"] == "active" else "🔴"
                    result += f"{status_emoji} {alert['alert_name']} - {alert['status'].upper()}\n"
                    result += f"   {alert['ticker']}: Price {alert['alert_type']} ${alert['target_price']:.2f}\n\n"
            
            # RSI alerts
            if alerts["rsi_alerts"]:
                result += "📊 RSI ALERTS\n"
                for alert in alerts["rsi_alerts"]:
                    status_emoji = "🟢" if alert["status"] == "active" else "🔴"
                    result += f"{status_emoji} {alert['alert_name']} - {alert['status'].upper()}\n"
                    result += f"   {alert['ticker']}: RSI {alert['alert_type']} {alert['rsi_threshold']:.0f}\n\n"
            
            total_alerts = len(alerts["price_alerts"]) + len(alerts["rsi_alerts"])
            result += "="*70 + "\n"
            result += f"Total alerts: {total_alerts}\n"
            
            return result
        
        except Exception as e:
            return f"Error listing alerts: {e}"

    @mcp.tool()
    def clear_triggered_alerts() -> str:
        """
        Clear all triggered alerts from the system.

        Returns:
            Confirmation message with count of cleared alerts.
        """
        try:
            alerts = load_alerts()
            
            initial_price_count = len(alerts["price_alerts"])
            initial_rsi_count = len(alerts["rsi_alerts"])
            
            # Filter out triggered alerts
            alerts["price_alerts"] = [a for a in alerts["price_alerts"] if a["status"] == "active"]
            alerts["rsi_alerts"] = [a for a in alerts["rsi_alerts"] if a["status"] == "active"]
            
            cleared_price = initial_price_count - len(alerts["price_alerts"])
            cleared_rsi = initial_rsi_count - len(alerts["rsi_alerts"])
            total_cleared = cleared_price + cleared_rsi
            
            save_alerts(alerts)
            
            if total_cleared > 0:
                return f"✅ Cleared {total_cleared} triggered alert(s): {cleared_price} price alerts, {cleared_rsi} RSI alerts."
            else:
                return "No triggered alerts to clear."
        
        except Exception as e:
            return f"Error clearing alerts: {e}"

    @mcp.tool()
    def delete_all_alerts() -> str:
        """
        Delete ALL alerts (both active and triggered). Use with caution!

        Returns:
            Confirmation message.
        """
        try:
            alerts = load_alerts()
            total = len(alerts["price_alerts"]) + len(alerts["rsi_alerts"])
            
            alerts["price_alerts"] = []
            alerts["rsi_alerts"] = []
            save_alerts(alerts)
            
            return f"🗑️ Deleted all {total} alert(s)."
        
        except Exception as e:
            return f"Error deleting alerts: {e}"
