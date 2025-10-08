# Stock Market Analysis MCP Server

A comprehensive Model Context Protocol (MCP) server for advanced stock market analysis, trend identification, portfolio management, dividend tracking, sector analysis, and risk metrics.

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Setup](#step-1-get-the-code)
  - [MCP Configuration](#step-4-configure-mcp-in-cursor)
  - [Troubleshooting](#-troubleshooting)
- [Usage Examples](#-usage-examples)
- [Technical Indicators](#-technical-indicators-explained)
- [Architecture](#️-architecture)
- [Data Storage & Privacy](#-data-storage--privacy)
- [Best Practices](#-best-practices)
- [Dependencies](#-dependencies)

## 🚀 Features

### 📈 Price & Data Tools (`price_data.py`)
- **`get_latest_price(ticker)`** - Get the most recent market price for any stock
- **`get_historical_data(ticker, period)`** - Retrieve historical OHLC data (Open, High, Low, Close, Volume)
- **`get_stock_info(ticker)`** - Comprehensive stock information including fundamentals, P/E ratio, market cap, dividend yield, etc.

### 💼 Portfolio Management (`portfolio.py`)
- **`add_holding(ticker, shares, purchase_price, purchase_date?)`** - Add stocks to your portfolio with automatic cost basis tracking
- **`remove_holding(ticker, shares, sale_price, sale_date?)`** - Sell stocks with automatic profit/loss calculation
- **`view_portfolio()`** - See all your holdings with real-time valuations and P&L
- **`view_transactions(limit?)`** - Review your transaction history

### 🔍 Technical Analysis (`analysis.py`)
- **`analyze_buy_opportunity(ticker)`** - Simple SMA crossover strategy (20/50 day)
- **`calculate_rsi(ticker, period?, timeframe?)`** - Relative Strength Index to identify overbought/oversold conditions
- **`calculate_macd(ticker, timeframe?)`** - Moving Average Convergence Divergence for trend momentum
- **`analyze_trends(ticker, timeframe?)`** - Multi-indicator comprehensive trend analysis
- **`compare_stocks(tickers[])`** - Side-by-side comparison of multiple stocks

### 🔔 Alert System (`alerts.py`)
- **`set_price_alert(ticker, target_price, alert_type, alert_name?)`** - Set price alerts (above/below thresholds)
- **`set_rsi_alert(ticker, rsi_threshold, alert_type, alert_name?)`** - Set RSI alerts for overbought/oversold conditions
- **`check_alerts()`** - Check all active alerts and see which ones have been triggered
- **`list_alerts()`** - View all configured alerts
- **`clear_triggered_alerts()`** - Remove triggered alerts
- **`delete_all_alerts()`** - Delete all alerts

### 💰 Dividend Tracking (`dividends.py`)
- **`get_dividend_history(ticker, period?)`** - View dividend payment history with trends
- **`get_dividend_yield(ticker)`** - Get current dividend yield and related metrics
- **`calculate_portfolio_dividend_income()`** - Calculate expected annual dividend income from your portfolio
- **`find_high_dividend_stocks(min_yield?, sector?)`** - Discover high-yield dividend stocks

### 🏢 Sector Analysis (`sector.py`)
- **`analyze_sector(sector_name)`** - Comprehensive analysis of a specific market sector
- **`compare_sectors()`** - Compare performance across all major market sectors
- **`get_sector_leaders(sector_name, metric?)`** - Get top performing stocks in a sector
- **`analyze_portfolio_sector_allocation()`** - Analyze your portfolio's sector diversification

### ⚠️ Risk Metrics (`risk.py`)
- **`calculate_sharpe_ratio(ticker, risk_free_rate?, period?)`** - Measure risk-adjusted returns
- **`calculate_beta(ticker, benchmark?, period?)`** - Calculate stock volatility vs market
- **`calculate_portfolio_risk()`** - Comprehensive portfolio risk analysis with recommendations
- **`calculate_var(ticker, confidence_level?, period?, position_size?)`** - Value at Risk calculation
- **`calculate_drawdown(ticker, period?)`** - Maximum drawdown and peak-to-trough analysis

## 📦 Installation

### Prerequisites

Before you begin, ensure you have:
- **Python 3.8 or higher** installed on your system
- **Cursor IDE** (or another MCP-compatible client)
- **Git** (optional, for cloning the repository)
- Internet connection for fetching stock market data

### Step 1: Get the Code

**Option A: Clone from GitHub**
```bash
git clone https://github.com/CalvinLiuu/stock_mcp_server.git
cd stock_mcp_server
```

**Option B: Download ZIP**
- Download the repository as a ZIP file
- Extract it to your desired location
- Open a terminal and navigate to the extracted folder

### Step 2: Set Up Virtual Environment

Create and activate a virtual environment (recommended):

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `yfinance` - For real-time stock market data
- `pandas` - For data analysis
- `numpy` - For numerical computations
- `fastmcp` - For MCP server functionality

### Step 4: Configure MCP in Cursor

To use this server with Cursor IDE, you need to add it to your MCP configuration file.

#### Locate Your MCP Configuration

The MCP configuration file is typically located at:
- **macOS/Linux**: `~/.cursor/mcp.json`
- **Windows**: `%USERPROFILE%\.cursor\mcp.json`

#### Add the Server Configuration

Open the `mcp.json` file and add the following configuration (adjust the path to match your installation):

**Option A: Using Python Module (Recommended)**
```json
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "/absolute/path/to/stock_mcp_server/.venv/bin/python",
      "args": [
        "-m",
        "mcp.server.fastmcp",
        "run",
        "/absolute/path/to/stock_mcp_server/stock.server.py"
      ],
      "env": {}
    }
  }
}
```

**Option B: Using fastmcp CLI**
```json
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "/absolute/path/to/stock_mcp_server/.venv/bin/fastmcp",
      "args": [
        "dev",
        "/absolute/path/to/stock_mcp_server/stock.server.py"
      ],
      "env": {}
    }
  }
}
```

**Important:** 
- Replace `/absolute/path/to/stock_mcp_server/` with the actual full path to where you installed the server
- On Windows, use backslashes and the appropriate paths (e.g., `C:\\Users\\YourName\\...`)
- Make sure to use the Python interpreter from your virtual environment (`.venv/bin/python`)

**Example for macOS:**
```json
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "/Users/johndoe/Documents/stock_mcp_server/.venv/bin/python",
      "args": [
        "-m",
        "mcp.server.fastmcp",
        "run",
        "/Users/johndoe/Documents/stock_mcp_server/stock.server.py"
      ],
      "env": {}
    }
  }
}
```

**Example for Windows:**
```json
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "C:\\Users\\JohnDoe\\Documents\\stock_mcp_server\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "mcp.server.fastmcp",
        "run",
        "C:\\Users\\JohnDoe\\Documents\\stock_mcp_server\\stock.server.py"
      ],
      "env": {}
    }
  }
}
```

### Step 5: Restart Cursor

After updating your `mcp.json` configuration:
1. **Save the file**
2. **Completely restart Cursor** (close and reopen)
3. The MCP server should automatically start when Cursor launches

### Step 6: Verify Installation

You can verify the installation by checking the MCP logs in Cursor or by trying to use one of the tools:

**In Cursor's AI chat, try:**
```
Can you get the latest price for AAPL using the stock analyzer?
```

You should see the server responding with real-time stock data.

**Or check available tools:**
```
What tools are available in the stock-analyzer MCP server?
```

### 🧪 Testing the Server Manually (Optional)

To test the server outside of Cursor:

```bash
# Activate your virtual environment first
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Run the server in development mode
fastmcp dev stock.server.py
```

You should see output like:
```
Registering price data tools...
Registering portfolio management tools...
Registering technical analysis tools...
Registering alert system tools...
Registering dividend tracking tools...
Registering sector analysis tools...
Registering risk analysis tools...
✅ All tools registered successfully!
📊 Stock Market Analyzer v0.3.0 is ready!
```

### 🔧 Troubleshooting

**Server not starting?**
- Verify the paths in your `mcp.json` are absolute paths (not relative)
- Ensure you're using the Python from your virtual environment (`.venv/bin/python`)
- Check that all dependencies are installed: `pip list` should show yfinance, pandas, numpy, fastmcp

**"Module not found" errors?**
- Make sure your virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Can't fetch stock data?**
- Check your internet connection
- Some stocks may have delayed data or require different ticker symbols
- Try a common stock like "AAPL" or "MSFT" first

**MCP server not appearing in Cursor?**
- Ensure the `mcp.json` file is valid JSON (no trailing commas, proper syntax)
- Check Cursor's MCP logs for error messages
- Try restarting Cursor completely

**Permission errors on macOS/Linux?**
- Make sure the Python executable is executable: `chmod +x .venv/bin/python`

### 📱 Quick Start After Installation

Once installed and configured, you can immediately start using the tools through Cursor's AI chat:

```
# Check a stock price
"Get the latest price for Tesla"

# Add to your portfolio
"Add 10 shares of AAPL at $150 to my portfolio"

# View your portfolio
"Show me my current portfolio"

# Set an alert
"Alert me when TSLA goes below $250"

# Analyze a stock
"Analyze trends for NVDA"
```

## 🎯 Usage Examples

### Portfolio Management

```python
# Add stocks to your portfolio
add_holding("AAPL", 10, 150.00)
add_holding("MSFT", 5, 380.00)
add_holding("NVDA", 8, 450.00)

# View your portfolio with current valuations
view_portfolio()

# Sell some shares
remove_holding("AAPL", 5, 175.00)

# View transaction history
view_transactions(limit=20)
```

### Alert System

```python
# Set a price alert
set_price_alert("TSLA", 250.00, "below")

# Set an RSI alert for oversold conditions
set_rsi_alert("NVDA", 30, "below")

# Check if any alerts triggered
check_alerts()

# View all configured alerts
list_alerts()
```

### Dividend Analysis

```python
# View dividend history
get_dividend_history("JNJ", period="5y")

# Check dividend yield
get_dividend_yield("KO")

# Calculate portfolio dividend income
calculate_portfolio_dividend_income()

# Find high-yield stocks in utilities sector
find_high_dividend_stocks(min_yield=4.0, sector="Utilities")
```

### Sector Analysis

```python
# Analyze technology sector
analyze_sector("Technology")

# Compare all sectors
compare_sectors()

# Get sector leaders by performance
get_sector_leaders("Healthcare", metric="return")

# Check portfolio sector diversification
analyze_portfolio_sector_allocation()
```

### Risk Analysis

```python
# Calculate Sharpe ratio
calculate_sharpe_ratio("AAPL", risk_free_rate=0.04, period="1y")

# Calculate beta vs S&P 500
calculate_beta("TSLA", benchmark="SPY")

# Comprehensive portfolio risk analysis
calculate_portfolio_risk()

# Calculate Value at Risk
calculate_var("NVDA", confidence_level=0.95, position_size=10000)

# Analyze maximum drawdown
calculate_drawdown("MSFT", period="5y")
```

### Technical Analysis

```python
# Get detailed stock information
get_stock_info("GOOGL")

# Check RSI for overbought/oversold signals
calculate_rsi("TSLA", period=14, timeframe="3mo")

# Analyze MACD for momentum
calculate_macd("MSFT", timeframe="6mo")

# Comprehensive trend analysis
analyze_trends("NVDA", timeframe="1y")

# Compare multiple stocks
compare_stocks(["AAPL", "MSFT", "GOOGL"])
```

## 📊 Technical Indicators Explained

### RSI (Relative Strength Index)
- **Above 70**: Overbought - potential sell signal
- **Below 30**: Oversold - potential buy opportunity
- **30-70**: Neutral range

### MACD (Moving Average Convergence Divergence)
- **Bullish Crossover**: MACD line crosses above signal line
- **Bearish Crossover**: MACD line crosses below signal line
- Used to identify momentum and trend changes

### SMA Crossover Strategy
- **Buy Signal**: Short-term SMA (20-day) crosses above long-term SMA (50-day)
- **Sell Signal**: Short-term SMA crosses below long-term SMA

### Sharpe Ratio
- **> 2.0**: Excellent risk-adjusted returns
- **1.0-2.0**: Good
- **0-1.0**: Fair
- **< 0**: Poor (returns below risk-free rate)

### Beta
- **β > 1**: More volatile than market
- **β = 1**: Moves with market
- **0 < β < 1**: Less volatile than market
- **β < 0**: Moves opposite to market

## 🏗️ Architecture

```
stock_mcp_server/
├── stock.server.py         # Main server entry point
├── utils.py                # Shared utilities (load/save data)
├── price_data.py           # Price and stock information
├── portfolio.py            # Portfolio management
├── analysis.py             # Technical analysis tools
├── alerts.py               # Alert system
├── dividends.py            # Dividend tracking
├── sector.py               # Sector analysis
├── risk.py                 # Risk metrics
├── portfolio.json          # Portfolio data (auto-generated)
├── alerts.json             # Alert data (auto-generated)
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

### Modular Design

Each module is self-contained and can be updated independently:

- **`utils.py`**: Shared functions for data persistence
- **`price_data.py`**: Basic stock data retrieval
- **`portfolio.py`**: Holdings and transaction tracking
- **`analysis.py`**: Technical indicators and trend analysis
- **`alerts.py`**: Price and RSI alert system
- **`dividends.py`**: Dividend history and income tracking
- **`sector.py`**: Sector-wide analysis and comparison
- **`risk.py`**: Risk metrics and portfolio risk management

## 📁 Data Storage & Privacy

### 🔒 Local Storage Only

**Your data stays completely private and local:**
- ✅ All portfolio data is stored on your computer only
- ✅ No cloud storage or external servers
- ✅ No authentication or account required
- ✅ Full control over your data files
- ✅ Can backup/edit JSON files directly

**What gets stored locally:**
- Your stock holdings and transactions → `portfolio.json`
- Your price and RSI alerts → `alerts.json`

**What goes to the internet:**
- Only market data requests (stock prices, fundamentals, etc.) via Yahoo Finance API
- Your personal portfolio data is NEVER transmitted anywhere

### Portfolio Data (`portfolio.json`)

Location: Same directory as `stock.server.py`

Automatically created and saved with:
- Current holdings with average cost basis
- Complete transaction history (buy/sell)
- Profit/loss calculations
- Last update dates

**Example structure:**
```json
{
  "holdings": {
    "AAPL": {
      "shares": 10,
      "avg_price": 150.00,
      "last_updated": "2025-01-15"
    }
  },
  "transactions": [
    {
      "type": "BUY",
      "ticker": "AAPL",
      "shares": 10,
      "price": 150.00,
      "date": "2025-01-15",
      "total": 1500.00
    }
  ]
}
```

### Alert Data (`alerts.json`)

Location: Same directory as `stock.server.py`

Automatically created and saved with:
- Active price alerts (trigger above/below thresholds)
- Active RSI alerts (overbought/oversold conditions)
- Alert status and trigger history

**Example structure:**
```json
{
  "price_alerts": [
    {
      "id": "alert_123",
      "ticker": "TSLA",
      "target_price": 250.00,
      "alert_type": "below",
      "status": "active"
    }
  ],
  "rsi_alerts": []
}
```

### Backup Your Data

Since all data is stored locally in JSON files, you can easily:
- **Backup**: Copy `portfolio.json` and `alerts.json` to another location
- **Restore**: Replace the files with your backup
- **Edit**: Manually edit the JSON files if needed (be careful with formatting)
- **Version Control**: Add to Git (but remember to add to `.gitignore` if sharing publicly)

## 🆕 What's New in v0.3.0

### New Features
1. **🔔 Alert System** - Set price and RSI alerts, check status automatically
2. **💰 Dividend Tracking** - Track dividend history, yields, and portfolio income
3. **🏢 Sector Analysis** - Analyze entire sectors, compare performance, check diversification
4. **⚠️ Risk Metrics** - Sharpe ratio, beta, VaR, drawdown, comprehensive portfolio risk

### Enhanced Features
- Modular architecture for better maintainability
- Separated concerns into dedicated modules
- Improved error handling across all tools
- Better data persistence with separate files for alerts

### Previous Features (v0.2.0)
- Portfolio management with P&L tracking
- Technical indicators (RSI, MACD, SMA)
- Comprehensive trend analysis
- Stock comparison tools

### Original Features (v0.1.0)
- Basic price data retrieval
- Historical data access
- Simple SMA crossover analysis

## 🔧 Configuration

### Risk-Free Rate
Default: 4% (0.04) - Can be adjusted in Sharpe ratio calculations

### Available Sectors
- Technology
- Healthcare
- Financial Services
- Energy
- Consumer Cyclical
- Consumer Defensive
- Utilities
- Industrials
- Real Estate
- Materials
- Communication Services

### Alert Types
- **Price Alerts**: `above` or `below` target price
- **RSI Alerts**: `above` or `below` RSI threshold

## 📚 Dependencies

- **yfinance** (>=0.2.40): Real-time and historical market data
- **pandas** (>=2.0.0): Data manipulation and analysis
- **numpy** (>=1.24.0): Numerical computations for risk metrics
- **fastmcp** (>=0.1.0): MCP server framework

## 🎓 Best Practices

### Portfolio Management
- Diversify across 10-20 different stocks
- Keep largest position below 20% of portfolio
- Regular rebalancing (quarterly or annually)
- Track cost basis for tax purposes

### Risk Management
- Target Sharpe ratio > 1.0 for good risk-adjusted returns
- Keep portfolio beta between 0.8-1.2 for moderate risk
- Monitor maximum drawdown - be prepared for historical volatility
- Use VaR to understand daily loss potential

### Sector Allocation
- Diversify across at least 5 different sectors
- Avoid concentration > 35% in any single sector
- Consider sector rotation based on economic cycles
- Balance growth and defensive sectors

### Dividend Investing
- Look for payout ratios < 80% for sustainability
- Prefer dividend growth over just high yield
- Reinvest dividends for compound growth
- Track ex-dividend dates for planning

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It is NOT financial advice.

- Market data may be delayed
- Past performance doesn't guarantee future results
- Always do your own research before investing
- Consider consulting a financial advisor
- Be aware of tax implications

## 🚀 Future Enhancements

Potential additions:
- Options analysis and Greeks calculation
- Fibonacci retracement levels
- Support/resistance identification
- News sentiment analysis
- Backtesting capabilities
- Tax lot tracking for capital gains
- Portfolio rebalancing suggestions
- Correlation analysis between holdings
- Monte Carlo simulations
- Real-time streaming quotes

## 📄 License

MIT License - Feel free to use and modify as needed.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows the modular architecture
- New features are in appropriate modules
- Documentation is updated
- Error handling is comprehensive

## 📞 Support

For issues or questions:
1. Check the documentation above
2. Review the module-specific code
3. Ensure all dependencies are installed
4. Verify API data is accessible

---

**Version**: 0.3.0  
**Last Updated**: 2025  
**Author**: Stock Market Analysis MCP Server