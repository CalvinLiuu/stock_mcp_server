"""
Stock Market Analysis MCP Server

A comprehensive MCP server for stock market analysis with:
- Price data and stock information
- Portfolio management and tracking
- Technical analysis (RSI, MACD, SMA, trends)
- Alert system (price and RSI alerts)
- Dividend tracking and analysis
- Sector analysis and comparison
- Risk metrics (Sharpe ratio, beta, VaR, drawdown, portfolio risk)

Version: 0.3.0
"""

from mcp.server.fastmcp import FastMCP

# Import all module registration functions
from price_data import register_price_tools
from portfolio import register_portfolio_tools
from analysis import register_analysis_tools
from alerts import register_alert_tools
from dividends import register_dividend_tools
from sector import register_sector_tools
from risk import register_risk_tools

# Initialize the FastMCP server
mcp = FastMCP("Stock Market Analyzer")

# Register all tool categories
print("Registering price data tools...")
register_price_tools(mcp)

print("Registering portfolio management tools...")
register_portfolio_tools(mcp)

print("Registering technical analysis tools...")
register_analysis_tools(mcp)

print("Registering alert system tools...")
register_alert_tools(mcp)

print("Registering dividend tracking tools...")
register_dividend_tools(mcp)

print("Registering sector analysis tools...")
register_sector_tools(mcp)

print("Registering risk analysis tools...")
register_risk_tools(mcp)

print("✅ All tools registered successfully!")
print("📊 Stock Market Analyzer v0.3.0 is ready!")

# Note: All tool implementations are now in separate modules:
# - price_data.py: Price and stock information tools
# - portfolio.py: Portfolio management tools
# - analysis.py: Technical analysis tools
# - alerts.py: Alert system tools
# - dividends.py: Dividend tracking tools
# - sector.py: Sector analysis tools  
# - risk.py: Risk metrics and portfolio risk tools