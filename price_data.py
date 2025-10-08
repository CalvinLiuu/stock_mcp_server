"""
Functions for retrieving stock price data and basic information.
"""
import yfinance as yf
from mcp.server.fastmcp import FastMCP


def register_price_tools(mcp: FastMCP):
    """Register price data tools with the MCP server."""
    
    @mcp.tool()
    def get_latest_price(ticker: str) -> str:
        """
        Gets the most recent market price for a given stock ticker.

        Args:
            ticker: The stock ticker symbol (e.g., 'AAPL', 'GOOGL').

        Returns:
            A string containing the latest price and currency, or an error message.
        """
        try:
            stock = yf.Ticker(ticker)
            # Use 'regularMarketPrice' for live/recent price
            price = stock.info.get('regularMarketPrice')
            currency = stock.info.get('currency', 'USD')
            if price:
                return f"The latest price for {ticker.upper()} is {price} {currency}."
            else:
                return f"Could not retrieve the price for {ticker.upper()}. Please check the ticker symbol."
        except Exception as e:
            return f"An error occurred: {e}"

    @mcp.tool()
    def get_historical_data(ticker: str, period: str = "1y") -> dict:
        """
        Gets historical price data (Open, High, Low, Close, Volume) for a stock.

        Args:
            ticker: The stock ticker symbol (e.g., 'MSFT').
            period: The time period for the data (e.g., '1mo', '6mo', '1y', '5y'). Defaults to '1y'.

        Returns:
            A dictionary containing the historical data, or an error message.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                return {"error": f"No data found for ticker {ticker}."}
            # Convert dataframe to dictionary for easy JSON serialization
            return hist.reset_index().to_dict(orient='records')
        except Exception as e:
            return {"error": f"An error occurred: {e}"}

    @mcp.tool()
    def get_stock_info(ticker: str) -> str:
        """
        Get comprehensive information about a stock including fundamentals and key metrics.

        Args:
            ticker: The stock ticker symbol.

        Returns:
            Detailed information about the stock including price, market cap, P/E ratio, etc.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            result = f"📊 {info.get('longName', ticker.upper())} ({ticker.upper()})\n"
            result += "="*70 + "\n\n"
            
            # Price Information
            result += "💰 PRICE INFORMATION\n"
            result += f"   Current Price: ${info.get('regularMarketPrice', 'N/A')} {info.get('currency', '')}\n"
            result += f"   Previous Close: ${info.get('previousClose', 'N/A')}\n"
            result += f"   Day Range: ${info.get('dayLow', 'N/A')} - ${info.get('dayHigh', 'N/A')}\n"
            result += f"   52 Week Range: ${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}\n\n"
            
            # Market Data
            result += "📈 MARKET DATA\n"
            result += f"   Market Cap: ${info.get('marketCap', 0):,.0f}\n"
            result += f"   Volume: {info.get('volume', 'N/A'):,}\n"
            result += f"   Avg Volume: {info.get('averageVolume', 'N/A'):,}\n\n"
            
            # Fundamental Metrics
            result += "🔍 FUNDAMENTAL METRICS\n"
            result += f"   P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
            result += f"   Forward P/E: {info.get('forwardPE', 'N/A')}\n"
            result += f"   EPS: ${info.get('trailingEps', 'N/A')}\n"
            result += f"   Dividend Yield: {info.get('dividendYield', 0)*100:.2f}%\n"
            result += f"   Beta: {info.get('beta', 'N/A')}\n\n"
            
            # Company Info
            result += "🏢 COMPANY INFO\n"
            result += f"   Sector: {info.get('sector', 'N/A')}\n"
            result += f"   Industry: {info.get('industry', 'N/A')}\n"
            result += f"   Website: {info.get('website', 'N/A')}\n"
            
            return result
        
        except Exception as e:
            return f"Error getting stock info: {e}"
