"""
Portfolio management functions for tracking stock holdings and transactions.
"""
import yfinance as yf
from datetime import datetime
from typing import Optional
from mcp.server.fastmcp import FastMCP
from utils import load_portfolio, save_portfolio


def register_portfolio_tools(mcp: FastMCP):
    """Register portfolio management tools with the MCP server."""
    
    @mcp.tool()
    def add_holding(ticker: str, shares: float, purchase_price: float, purchase_date: Optional[str] = None) -> str:
        """
        Add a stock holding to your portfolio.

        Args:
            ticker: The stock ticker symbol (e.g., 'AAPL').
            shares: Number of shares purchased.
            purchase_price: Price per share at purchase.
            purchase_date: Date of purchase in YYYY-MM-DD format (defaults to today).

        Returns:
            A confirmation message with the updated holding.
        """
        try:
            ticker = ticker.upper()
            if purchase_date is None:
                purchase_date = datetime.now().strftime("%Y-%m-%d")
            
            portfolio = load_portfolio()
            
            # Add or update holding
            if ticker in portfolio["holdings"]:
                existing = portfolio["holdings"][ticker]
                total_shares = existing["shares"] + shares
                total_cost = (existing["shares"] * existing["avg_price"]) + (shares * purchase_price)
                new_avg_price = total_cost / total_shares
                
                portfolio["holdings"][ticker] = {
                    "shares": total_shares,
                    "avg_price": round(new_avg_price, 2),
                    "last_updated": purchase_date
                }
            else:
                portfolio["holdings"][ticker] = {
                    "shares": shares,
                    "avg_price": purchase_price,
                    "last_updated": purchase_date
                }
            
            # Record transaction
            portfolio["transactions"].append({
                "type": "BUY",
                "ticker": ticker,
                "shares": shares,
                "price": purchase_price,
                "date": purchase_date,
                "total": round(shares * purchase_price, 2)
            })
            
            save_portfolio(portfolio)
            
            holding = portfolio["holdings"][ticker]
            return f"Added {shares} shares of {ticker} at ${purchase_price}/share. Total holding: {holding['shares']} shares at avg price ${holding['avg_price']}."
        
        except Exception as e:
            return f"Error adding holding: {e}"

    @mcp.tool()
    def remove_holding(ticker: str, shares: float, sale_price: float, sale_date: Optional[str] = None) -> str:
        """
        Remove (sell) shares from your portfolio.

        Args:
            ticker: The stock ticker symbol.
            shares: Number of shares to sell.
            sale_price: Price per share at sale.
            sale_date: Date of sale in YYYY-MM-DD format (defaults to today).

        Returns:
            A confirmation message with profit/loss information.
        """
        try:
            ticker = ticker.upper()
            if sale_date is None:
                sale_date = datetime.now().strftime("%Y-%m-%d")
            
            portfolio = load_portfolio()
            
            if ticker not in portfolio["holdings"]:
                return f"You don't own any shares of {ticker}."
            
            holding = portfolio["holdings"][ticker]
            
            if shares > holding["shares"]:
                return f"Cannot sell {shares} shares. You only own {holding['shares']} shares of {ticker}."
            
            # Calculate profit/loss
            cost_basis = shares * holding["avg_price"]
            sale_value = shares * sale_price
            profit_loss = sale_value - cost_basis
            profit_loss_pct = (profit_loss / cost_basis) * 100
            
            # Update or remove holding
            if shares == holding["shares"]:
                del portfolio["holdings"][ticker]
                remaining_msg = f"All shares of {ticker} sold."
            else:
                portfolio["holdings"][ticker]["shares"] = holding["shares"] - shares
                portfolio["holdings"][ticker]["last_updated"] = sale_date
                remaining_msg = f"Remaining: {portfolio['holdings'][ticker]['shares']} shares."
            
            # Record transaction
            portfolio["transactions"].append({
                "type": "SELL",
                "ticker": ticker,
                "shares": shares,
                "price": sale_price,
                "date": sale_date,
                "total": round(sale_value, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_loss_pct": round(profit_loss_pct, 2)
            })
            
            save_portfolio(portfolio)
            
            return f"Sold {shares} shares of {ticker} at ${sale_price}/share. Profit/Loss: ${round(profit_loss, 2)} ({round(profit_loss_pct, 2)}%). {remaining_msg}"
        
        except Exception as e:
            return f"Error removing holding: {e}"

    @mcp.tool()
    def view_portfolio() -> str:
        """
        View all current holdings with current prices and profit/loss.

        Returns:
            A formatted summary of your portfolio with current values and performance.
        """
        try:
            portfolio = load_portfolio()
            
            if not portfolio["holdings"]:
                return "Your portfolio is empty. Use add_holding() to add stocks."
            
            result = "📊 PORTFOLIO SUMMARY\n" + "="*70 + "\n\n"
            
            total_invested = 0
            total_current_value = 0
            
            for ticker, holding in portfolio["holdings"].items():
                shares = holding["shares"]
                avg_price = holding["avg_price"]
                invested = shares * avg_price
                
                # Get current price
                stock = yf.Ticker(ticker)
                current_price = stock.info.get('regularMarketPrice', 0)
                
                if current_price:
                    current_value = shares * current_price
                    gain_loss = current_value - invested
                    gain_loss_pct = (gain_loss / invested) * 100 if invested > 0 else 0
                    
                    result += f"🏢 {ticker}\n"
                    result += f"   Shares: {shares}\n"
                    result += f"   Avg Cost: ${avg_price:.2f}/share | Current: ${current_price:.2f}/share\n"
                    result += f"   Invested: ${invested:.2f} | Current Value: ${current_value:.2f}\n"
                    result += f"   Gain/Loss: ${gain_loss:.2f} ({gain_loss_pct:+.2f}%)\n"
                    result += f"   Last Updated: {holding['last_updated']}\n\n"
                    
                    total_invested += invested
                    total_current_value += current_value
                else:
                    result += f"🏢 {ticker}\n"
                    result += f"   Shares: {shares} @ ${avg_price:.2f}/share\n"
                    result += f"   ⚠️ Could not fetch current price\n\n"
                    total_invested += invested
            
            # Portfolio totals
            total_gain_loss = total_current_value - total_invested
            total_gain_loss_pct = (total_gain_loss / total_invested) * 100 if total_invested > 0 else 0
            
            result += "="*70 + "\n"
            result += f"💰 Total Invested: ${total_invested:.2f}\n"
            result += f"💵 Current Value: ${total_current_value:.2f}\n"
            result += f"📈 Total Gain/Loss: ${total_gain_loss:.2f} ({total_gain_loss_pct:+.2f}%)\n"
            
            return result
        
        except Exception as e:
            return f"Error viewing portfolio: {e}"

    @mcp.tool()
    def view_transactions(limit: int = 10) -> str:
        """
        View recent transaction history.

        Args:
            limit: Maximum number of recent transactions to display (default: 10).

        Returns:
            A formatted list of recent transactions.
        """
        try:
            portfolio = load_portfolio()
            
            if not portfolio["transactions"]:
                return "No transactions recorded yet."
            
            transactions = portfolio["transactions"][-limit:]  # Get last N transactions
            transactions.reverse()  # Show most recent first
            
            result = f"📋 RECENT TRANSACTIONS (Last {min(limit, len(portfolio['transactions']))})\n"
            result += "="*70 + "\n\n"
            
            for txn in transactions:
                emoji = "🟢" if txn["type"] == "BUY" else "🔴"
                result += f"{emoji} {txn['type']} - {txn['ticker']}\n"
                result += f"   Date: {txn['date']}\n"
                result += f"   Shares: {txn['shares']} @ ${txn['price']:.2f}/share\n"
                result += f"   Total: ${txn['total']:.2f}\n"
                
                if txn["type"] == "SELL" and "profit_loss" in txn:
                    pl_emoji = "📈" if txn["profit_loss"] >= 0 else "📉"
                    result += f"   {pl_emoji} P/L: ${txn['profit_loss']:.2f} ({txn['profit_loss_pct']:+.2f}%)\n"
                
                result += "\n"
            
            return result
        
        except Exception as e:
            return f"Error viewing transactions: {e}"
