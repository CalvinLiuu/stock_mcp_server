# Stock Market MCP Server - Complete Tools Reference

## 📊 All Available Tools (40+ functions)

### 💰 Price & Data Tools (3)
| Tool | Description |
|------|-------------|
| `get_latest_price(ticker)` | Get current market price |
| `get_historical_data(ticker, period)` | Get OHLC historical data |
| `get_stock_info(ticker)` | Comprehensive stock fundamentals |

### 💼 Portfolio Management (4)
| Tool | Description |
|------|-------------|
| `add_holding(ticker, shares, price, date?)` | Add stock to portfolio |
| `remove_holding(ticker, shares, price, date?)` | Sell stock from portfolio |
| `view_portfolio()` | View all holdings with P&L |
| `view_transactions(limit?)` | View transaction history |

### 🔍 Technical Analysis (5)
| Tool | Description |
|------|-------------|
| `analyze_buy_opportunity(ticker)` | SMA crossover analysis |
| `calculate_rsi(ticker, period?, timeframe?)` | RSI indicator |
| `calculate_macd(ticker, timeframe?)` | MACD indicator |
| `analyze_trends(ticker, timeframe?)` | Multi-indicator analysis |
| `compare_stocks(tickers[])` | Compare multiple stocks |

### 🔔 Alert System (6)
| Tool | Description |
|------|-------------|
| `set_price_alert(ticker, price, type, name?)` | Set price alert |
| `set_rsi_alert(ticker, threshold, type, name?)` | Set RSI alert |
| `check_alerts()` | Check triggered alerts |
| `list_alerts()` | List all alerts |
| `clear_triggered_alerts()` | Remove triggered alerts |
| `delete_all_alerts()` | Delete all alerts |

### 💎 Dividend Tracking (4)
| Tool | Description |
|------|-------------|
| `get_dividend_history(ticker, period?)` | Dividend payment history |
| `get_dividend_yield(ticker)` | Current dividend metrics |
| `calculate_portfolio_dividend_income()` | Portfolio dividend income |
| `find_high_dividend_stocks(min_yield?, sector?)` | Find high-yield stocks |

### 🏢 Sector Analysis (4)
| Tool | Description |
|------|-------------|
| `analyze_sector(sector_name)` | Analyze specific sector |
| `compare_sectors()` | Compare all sectors |
| `get_sector_leaders(sector, metric?)` | Top stocks in sector |
| `analyze_portfolio_sector_allocation()` | Portfolio sector breakdown |

### ⚠️ Risk Metrics (5)
| Tool | Description |
|------|-------------|
| `calculate_sharpe_ratio(ticker, rate?, period?)` | Risk-adjusted returns |
| `calculate_beta(ticker, benchmark?, period?)` | Volatility vs market |
| `calculate_portfolio_risk()` | Complete portfolio risk |
| `calculate_var(ticker, confidence?, period?, size?)` | Value at Risk |
| `calculate_drawdown(ticker, period?)` | Maximum drawdown |

### 🤖 Stake Trading (5)
| Tool | Description |
|------|-------------|
| `configure_stake_connection(...)` | Store API endpoint and tokens |
| `stake_connection_status()` | View current (redacted) configuration |
| `stake_execute_graphql(query, variables?)` | Run custom GraphQL operations |
| `stake_place_order(symbol, side, qty, ...)` | Submit Stake trades |
| `stake_cancel_order(order_id)` / `stake_list_orders(status?)` | Manage existing orders |

## 🎯 Quick Start Examples

### Beginner: Basic Stock Research
```python
# Step 1: Get stock info
get_stock_info("AAPL")

# Step 2: Check current price
get_latest_price("AAPL")

# Step 3: Analyze trend
analyze_trends("AAPL", timeframe="1y")
```

### Intermediate: Portfolio Management
```python
# Add holdings
add_holding("AAPL", 10, 150.00)
add_holding("MSFT", 5, 380.00)

# View portfolio
view_portfolio()

# Set alerts
set_price_alert("AAPL", 200.00, "above")
check_alerts()
```

### Advanced: Risk Analysis
```python
# Individual stock risk
calculate_sharpe_ratio("AAPL", risk_free_rate=0.04)
calculate_beta("TSLA", benchmark="SPY")
calculate_drawdown("NVDA", period="5y")

# Portfolio risk
calculate_portfolio_risk()
analyze_portfolio_sector_allocation()
```

### Income Investor: Dividend Focus
```python
# Find dividend stocks
find_high_dividend_stocks(min_yield=4.0, sector="Utilities")

# Analyze dividend
get_dividend_history("JNJ", period="5y")
get_dividend_yield("KO")

# Portfolio income
calculate_portfolio_dividend_income()
```

### Technical Trader: Signals
```python
# Check technical indicators
calculate_rsi("TSLA", period=14)
calculate_macd("NVDA", timeframe="6mo")
analyze_buy_opportunity("MSFT")

# Set RSI alerts
set_rsi_alert("TSLA", 30, "below")  # Oversold
set_rsi_alert("NVDA", 70, "above")  # Overbought
```

### Sector Rotation: Macro View
```python
# Compare all sectors
compare_sectors()

# Deep dive into best sector
analyze_sector("Technology")
get_sector_leaders("Technology", metric="return")

# Check your diversification
analyze_portfolio_sector_allocation()
```

## 📈 Workflow Examples

### Daily Market Check
1. `check_alerts()` - See if any alerts triggered
2. `view_portfolio()` - Check portfolio performance
3. `compare_sectors()` - Identify sector trends
4. `analyze_trends("your_watchlist_stock")` - Check specific stocks

### Weekly Portfolio Review
1. `view_portfolio()` - Review overall performance
2. `calculate_portfolio_risk()` - Check risk metrics
3. `analyze_portfolio_sector_allocation()` - Verify diversification
4. `calculate_portfolio_dividend_income()` - Track income
5. `view_transactions(limit=20)` - Review recent activity

### Monthly Rebalancing
1. `calculate_portfolio_risk()` - Assess current risk
2. `analyze_portfolio_sector_allocation()` - Check sector weights
3. `compare_sectors()` - Identify opportunities
4. `get_sector_leaders("sector", "return")` - Find best performers
5. Adjust holdings based on analysis

### Research New Investment
1. `get_stock_info("TICKER")` - Basic information
2. `analyze_trends("TICKER")` - Trend analysis
3. `calculate_rsi("TICKER")` - Check if overbought/oversold
4. `calculate_sharpe_ratio("TICKER")` - Risk-adjusted returns
5. `calculate_beta("TICKER")` - Volatility assessment
6. `get_dividend_yield("TICKER")` - Income potential
7. `analyze_sector("sector")` - Sector context

## 🎓 Tool Categories by Use Case

### For Growth Investors
- `analyze_trends()` - Identify momentum
- `calculate_macd()` - Trend strength
- `compare_stocks()` - Compare opportunities
- `get_sector_leaders()` - Find leaders
- `calculate_beta()` - Volatility check

### For Value Investors
- `get_stock_info()` - Fundamentals
- `calculate_rsi()` - Entry points
- `calculate_drawdown()` - Downside risk
- `get_dividend_yield()` - Yield component
- `analyze_sector()` - Sector value

### For Income Investors
- `find_high_dividend_stocks()` - Discovery
- `get_dividend_history()` - Track record
- `get_dividend_yield()` - Current yield
- `calculate_portfolio_dividend_income()` - Income planning
- `analyze_sector()` - Sector yields

### For Risk-Conscious Investors
- `calculate_portfolio_risk()` - Overall risk
- `calculate_sharpe_ratio()` - Risk-adjusted returns
- `calculate_beta()` - Market correlation
- `calculate_var()` - Downside potential
- `calculate_drawdown()` - Historical losses
- `analyze_portfolio_sector_allocation()` - Diversification

## 🔥 Pro Tips

### Combining Tools
```python
# Complete stock analysis
get_stock_info("AAPL")
calculate_rsi("AAPL")
calculate_macd("AAPL")
analyze_trends("AAPL")
calculate_sharpe_ratio("AAPL")
calculate_beta("AAPL")
```

### Portfolio Health Check
```python
view_portfolio()
calculate_portfolio_risk()
analyze_portfolio_sector_allocation()
calculate_portfolio_dividend_income()
```

### Alert Strategy
```python
# Set multiple alert types
set_price_alert("AAPL", 150, "below")  # Support level
set_price_alert("AAPL", 200, "above")  # Resistance level
set_rsi_alert("AAPL", 30, "below")     # Oversold
set_rsi_alert("AAPL", 70, "above")     # Overbought
```

## 📚 Parameter Reference

### Common Parameters
- **ticker**: Stock symbol (e.g., 'AAPL', 'MSFT')
- **period/timeframe**: '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'
- **confidence_level**: 0.90, 0.95, 0.99 (for VaR)
- **risk_free_rate**: Typically 0.04 (4%) for current environment

### Alert Types
- **price alerts**: 'above' or 'below'
- **rsi alerts**: 'above' or 'below'

### Metric Types (for sector leaders)
- **'return'**: 3-month returns
- **'market_cap'**: Market capitalization
- **'volume'**: Trading volume
- **'dividend_yield'**: Dividend yield

### Sectors
Technology, Healthcare, Financial Services, Energy, Consumer Cyclical, Consumer Defensive, Utilities, Industrials, Real Estate, Materials, Communication Services

---

**Total Tools**: 31+ functions across 7 categories  
**Version**: 0.3.0
