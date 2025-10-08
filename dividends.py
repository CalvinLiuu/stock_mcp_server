"""
Dividend tracking and analysis functions.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List
from mcp.server.fastmcp import FastMCP
from utils import load_portfolio


def register_dividend_tools(mcp: FastMCP):
    """Register dividend tracking tools with the MCP server."""
    
    @mcp.tool()
    def get_dividend_history(ticker: str, period: str = "5y") -> str:
        """
        Get dividend payment history for a stock.

        Args:
            ticker: The stock ticker symbol (e.g., 'AAPL').
            period: Time period for dividend history (default: '5y').

        Returns:
            Formatted dividend payment history.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            dividends = stock.dividends
            
            if dividends.empty:
                return f"No dividend history found for {ticker.upper()}. This stock may not pay dividends."
            
            # Filter by period if needed
            if period != "max":
                # Convert period to datetime
                period_map = {
                    "1mo": 1/12, "3mo": 0.25, "6mo": 0.5, 
                    "1y": 1, "2y": 2, "5y": 5, "10y": 10
                }
                years = period_map.get(period, 5)
                cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)
                dividends = dividends[dividends.index >= cutoff_date]
            
            result = f"💰 DIVIDEND HISTORY for {ticker.upper()}\n"
            result += "="*70 + "\n\n"
            
            # Summary stats
            total_dividends = dividends.sum()
            avg_dividend = dividends.mean()
            last_dividend = dividends.iloc[-1]
            last_date = dividends.index[-1].strftime("%Y-%m-%d")
            
            result += "📊 SUMMARY\n"
            result += f"   Total Dividends Paid: ${total_dividends:.2f}\n"
            result += f"   Average Dividend: ${avg_dividend:.2f}\n"
            result += f"   Last Dividend: ${last_dividend:.2f} on {last_date}\n"
            result += f"   Number of Payments: {len(dividends)}\n\n"
            
            # Recent dividends (last 10)
            result += "📋 RECENT DIVIDEND PAYMENTS (Last 10)\n"
            recent = dividends.tail(10).sort_index(ascending=False)
            for date, amount in recent.items():
                result += f"   {date.strftime('%Y-%m-%d')}: ${amount:.2f}\n"
            
            # Annual dividend trend
            result += "\n📈 ANNUAL DIVIDEND TREND\n"
            annual = dividends.groupby(dividends.index.year).sum()
            for year, total in annual.tail(5).items():
                result += f"   {year}: ${total:.2f}\n"
            
            return result
        
        except Exception as e:
            return f"Error getting dividend history: {e}"

    @mcp.tool()
    def get_dividend_yield(ticker: str) -> str:
        """
        Get current dividend yield and related metrics for a stock.

        Args:
            ticker: The stock ticker symbol.

        Returns:
            Dividend yield information and analysis.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            dividend_yield = info.get('dividendYield', 0)
            dividend_rate = info.get('dividendRate', 0)
            payout_ratio = info.get('payoutRatio', 0)
            five_year_avg_yield = info.get('fiveYearAvgDividendYield', 0)
            
            current_price = info.get('regularMarketPrice', 0)
            
            if dividend_yield == 0 and dividend_rate == 0:
                return f"{ticker.upper()} does not currently pay dividends."
            
            result = f"💎 DIVIDEND ANALYSIS for {ticker.upper()}\n"
            result += "="*70 + "\n\n"
            
            result += "📊 CURRENT METRICS\n"
            result += f"   Current Price: ${current_price:.2f}\n"
            result += f"   Dividend Yield: {dividend_yield * 100:.2f}%\n"
            result += f"   Annual Dividend Rate: ${dividend_rate:.2f}\n"
            result += f"   Payout Ratio: {payout_ratio * 100:.2f}%\n"
            if five_year_avg_yield:
                result += f"   5-Year Avg Yield: {five_year_avg_yield:.2f}%\n"
            
            result += "\n💡 INTERPRETATION\n"
            
            # Yield interpretation
            if dividend_yield * 100 > 5:
                result += "   Yield: 🟢 High yield - attractive for income investors\n"
            elif dividend_yield * 100 > 2:
                result += "   Yield: 🟡 Moderate yield - decent income potential\n"
            else:
                result += "   Yield: 🔴 Low yield - primarily a growth stock\n"
            
            # Payout ratio interpretation
            if payout_ratio > 0:
                if payout_ratio > 0.8:
                    result += "   Payout: 🔴 High payout ratio - dividend may be at risk\n"
                elif payout_ratio > 0.5:
                    result += "   Payout: 🟡 Moderate payout ratio - sustainable dividend\n"
                else:
                    result += "   Payout: 🟢 Low payout ratio - room for dividend growth\n"
            
            return result
        
        except Exception as e:
            return f"Error getting dividend yield: {e}"

    @mcp.tool()
    def calculate_portfolio_dividend_income() -> str:
        """
        Calculate expected annual dividend income from your portfolio holdings.

        Returns:
            Summary of dividend income from all holdings.
        """
        try:
            portfolio = load_portfolio()
            
            if not portfolio["holdings"]:
                return "Your portfolio is empty. Add holdings to calculate dividend income."
            
            result = "💰 PORTFOLIO DIVIDEND INCOME\n"
            result += "="*70 + "\n\n"
            
            total_annual_income = 0
            dividend_stocks = []
            
            for ticker, holding in portfolio["holdings"].items():
                shares = holding["shares"]
                
                stock = yf.Ticker(ticker)
                info = stock.info
                
                dividend_rate = info.get('dividendRate', 0)
                dividend_yield = info.get('dividendYield', 0)
                current_price = info.get('regularMarketPrice', 0)
                
                if dividend_rate > 0:
                    annual_income = shares * dividend_rate
                    total_annual_income += annual_income
                    
                    dividend_stocks.append({
                        'ticker': ticker,
                        'shares': shares,
                        'dividend_rate': dividend_rate,
                        'annual_income': annual_income,
                        'yield': dividend_yield * 100,
                        'current_value': shares * current_price
                    })
            
            if not dividend_stocks:
                return "None of your holdings currently pay dividends."
            
            # Display dividend-paying stocks
            for stock in dividend_stocks:
                result += f"🏢 {stock['ticker']}\n"
                result += f"   Shares: {stock['shares']}\n"
                result += f"   Dividend/Share: ${stock['dividend_rate']:.2f}\n"
                result += f"   Yield: {stock['yield']:.2f}%\n"
                result += f"   Annual Income: ${stock['annual_income']:.2f}\n\n"
            
            # Summary
            result += "="*70 + "\n"
            result += f"💵 Total Annual Dividend Income: ${total_annual_income:.2f}\n"
            result += f"💵 Monthly Income (estimated): ${total_annual_income / 12:.2f}\n"
            result += f"💵 Quarterly Income (estimated): ${total_annual_income / 4:.2f}\n"
            result += f"\n📊 Dividend-Paying Stocks: {len(dividend_stocks)} of {len(portfolio['holdings'])}\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating portfolio dividend income: {e}"

    @mcp.tool()
    def find_high_dividend_stocks(min_yield: float = 3.0, sector: str = None) -> str:
        """
        Find stocks with high dividend yields. Searches popular dividend-paying stocks.

        Args:
            min_yield: Minimum dividend yield percentage (default: 3.0%).
            sector: Optional sector filter (e.g., 'Technology', 'Financial Services', 'Utilities').

        Returns:
            List of high-yield dividend stocks.
        """
        try:
            # List of known dividend aristocrats and high-yield stocks
            dividend_stocks = [
                'JNJ', 'PG', 'KO', 'PEP', 'MCD', 'WMT', 'XOM', 'CVX',  # Dividend aristocrats
                'T', 'VZ', 'IBM', 'INTC', 'CSCO', 'BMY',  # Telecom/Tech dividends
                'JPM', 'BAC', 'C', 'WFC',  # Financial
                'NEE', 'DUK', 'SO', 'D',  # Utilities
                'O', 'STAG', 'MPW',  # REITs
                'MO', 'PM', 'BTI'  # Tobacco
            ]
            
            result = f"💎 HIGH DIVIDEND STOCKS (Yield ≥ {min_yield}%)\n"
            result += "="*70 + "\n\n"
            
            high_yield_stocks = []
            
            for ticker in dividend_stocks:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    dividend_yield = info.get('dividendYield', 0) * 100
                    stock_sector = info.get('sector', '')
                    
                    # Apply filters
                    if dividend_yield < min_yield:
                        continue
                    
                    if sector and sector.lower() not in stock_sector.lower():
                        continue
                    
                    high_yield_stocks.append({
                        'ticker': ticker,
                        'name': info.get('shortName', ticker),
                        'yield': dividend_yield,
                        'price': info.get('regularMarketPrice', 0),
                        'sector': stock_sector,
                        'payout_ratio': info.get('payoutRatio', 0) * 100
                    })
                except:
                    continue
            
            if not high_yield_stocks:
                return f"No stocks found with yield ≥ {min_yield}%{' in ' + sector + ' sector' if sector else ''}."
            
            # Sort by yield
            high_yield_stocks.sort(key=lambda x: x['yield'], reverse=True)
            
            for stock in high_yield_stocks[:15]:  # Show top 15
                result += f"🏢 {stock['ticker']} - {stock['name']}\n"
                result += f"   Yield: {stock['yield']:.2f}% | Price: ${stock['price']:.2f}\n"
                result += f"   Sector: {stock['sector']}\n"
                result += f"   Payout Ratio: {stock['payout_ratio']:.1f}%\n\n"
            
            result += "="*70 + "\n"
            result += f"Found {len(high_yield_stocks)} stocks matching criteria.\n"
            result += "⚠️ High yields may indicate higher risk. Always research before investing.\n"
            
            return result
        
        except Exception as e:
            return f"Error finding high dividend stocks: {e}"
