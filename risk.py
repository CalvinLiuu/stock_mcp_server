"""
Risk analysis and portfolio risk metrics.
"""
import yfinance as yf
import numpy as np
from mcp.server.fastmcp import FastMCP
from utils import load_portfolio


def register_risk_tools(mcp: FastMCP):
    """Register risk analysis tools with the MCP server."""
    
    @mcp.tool()
    def calculate_sharpe_ratio(ticker: str, risk_free_rate: float = 0.04, period: str = "1y") -> str:
        """
        Calculate the Sharpe Ratio for a stock. Measures risk-adjusted return.
        Higher Sharpe ratio indicates better risk-adjusted performance.

        Args:
            ticker: The stock ticker symbol.
            risk_free_rate: Annual risk-free rate (default: 4% or 0.04).
            period: Time period for calculation (default: '1y').

        Returns:
            Sharpe ratio and interpretation.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period=period)
            
            if len(hist) < 30:
                return f"Not enough data to calculate Sharpe ratio for {ticker.upper()}."
            
            # Calculate daily returns
            returns = hist['Close'].pct_change().dropna()
            
            # Annualize returns and volatility
            avg_return = returns.mean() * 252  # 252 trading days per year
            std_return = returns.std() * np.sqrt(252)
            
            # Calculate Sharpe ratio
            sharpe_ratio = (avg_return - risk_free_rate) / std_return
            
            result = f"📊 SHARPE RATIO ANALYSIS for {ticker.upper()}\n"
            result += "="*70 + "\n\n"
            
            result += "📈 METRICS\n"
            result += f"   Annualized Return: {avg_return * 100:.2f}%\n"
            result += f"   Annualized Volatility: {std_return * 100:.2f}%\n"
            result += f"   Risk-Free Rate: {risk_free_rate * 100:.2f}%\n"
            result += f"   Sharpe Ratio: {sharpe_ratio:.2f}\n\n"
            
            result += "💡 INTERPRETATION\n"
            if sharpe_ratio > 2:
                interpretation = "🟢 EXCELLENT - Very good risk-adjusted returns"
            elif sharpe_ratio > 1:
                interpretation = "🟢 GOOD - Favorable risk-adjusted returns"
            elif sharpe_ratio > 0:
                interpretation = "🟡 FAIR - Positive but modest risk-adjusted returns"
            else:
                interpretation = "🔴 POOR - Negative risk-adjusted returns"
            
            result += f"   {interpretation}\n"
            result += "\n   Sharpe Ratio Guide:\n"
            result += "   > 2.0: Excellent\n"
            result += "   1.0-2.0: Good\n"
            result += "   0-1.0: Fair\n"
            result += "   < 0: Poor (return < risk-free rate)\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating Sharpe ratio: {e}"

    @mcp.tool()
    def calculate_beta(ticker: str, benchmark: str = "SPY", period: str = "1y") -> str:
        """
        Calculate Beta - measures stock volatility relative to market.
        Beta > 1: More volatile than market
        Beta < 1: Less volatile than market
        Beta = 1: Moves with market

        Args:
            ticker: The stock ticker symbol.
            benchmark: Benchmark ticker (default: 'SPY' for S&P 500).
            period: Time period for calculation (default: '1y').

        Returns:
            Beta value and interpretation.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            market = yf.Ticker(benchmark.upper())
            
            stock_hist = stock.history(period=period)
            market_hist = market.history(period=period)
            
            if len(stock_hist) < 30 or len(market_hist) < 30:
                return f"Not enough data to calculate Beta for {ticker.upper()}."
            
            # Calculate returns
            stock_returns = stock_hist['Close'].pct_change().dropna()
            market_returns = market_hist['Close'].pct_change().dropna()
            
            # Align the data
            combined = np.array([stock_returns, market_returns]).T
            combined = combined[~np.isnan(combined).any(axis=1)]
            
            if len(combined) < 30:
                return f"Not enough aligned data to calculate Beta for {ticker.upper()}."
            
            stock_aligned = combined[:, 0]
            market_aligned = combined[:, 1]
            
            # Calculate beta using covariance
            covariance = np.cov(stock_aligned, market_aligned)[0][1]
            market_variance = np.var(market_aligned)
            beta = covariance / market_variance
            
            # Also get correlation
            correlation = np.corrcoef(stock_aligned, market_aligned)[0][1]
            
            result = f"📊 BETA ANALYSIS for {ticker.upper()}\n"
            result += "="*70 + "\n\n"
            
            result += "📈 METRICS\n"
            result += f"   Beta vs {benchmark.upper()}: {beta:.2f}\n"
            result += f"   Correlation: {correlation:.2f}\n"
            result += f"   Stock Volatility: {stock_aligned.std() * np.sqrt(252) * 100:.2f}%\n"
            result += f"   Market Volatility: {market_aligned.std() * np.sqrt(252) * 100:.2f}%\n\n"
            
            result += "💡 INTERPRETATION\n"
            if beta > 1.5:
                interpretation = "🔴 HIGH RISK - Much more volatile than market"
            elif beta > 1.2:
                interpretation = "🟡 MODERATE-HIGH RISK - More volatile than market"
            elif beta > 0.8:
                interpretation = "🟢 MODERATE RISK - Moves with market"
            elif beta > 0:
                interpretation = "🟢 LOW RISK - Less volatile than market"
            else:
                interpretation = "🔵 DEFENSIVE - Moves opposite to market"
            
            result += f"   {interpretation}\n\n"
            
            result += "   Beta Guide:\n"
            result += "   β > 1: More volatile than market\n"
            result += "   β = 1: Moves with market\n"
            result += "   0 < β < 1: Less volatile than market\n"
            result += "   β < 0: Moves opposite to market\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating Beta: {e}"

    @mcp.tool()
    def calculate_portfolio_risk() -> str:
        """
        Calculate comprehensive risk metrics for your entire portfolio.
        Includes volatility, beta, Sharpe ratio, and diversification metrics.

        Returns:
            Portfolio-wide risk analysis.
        """
        try:
            portfolio = load_portfolio()
            
            if not portfolio["holdings"]:
                return "Your portfolio is empty. Add holdings to analyze risk."
            
            result = "⚠️ PORTFOLIO RISK ANALYSIS\n"
            result += "="*70 + "\n\n"
            
            # Get portfolio data
            portfolio_data = []
            total_value = 0
            
            for ticker, holding in portfolio["holdings"].items():
                shares = holding["shares"]
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1y")
                
                if not hist.empty:
                    current_price = info.get('regularMarketPrice', 0)
                    position_value = shares * current_price
                    total_value += position_value
                    
                    # Calculate returns
                    returns = hist['Close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252)  # Annualized
                    
                    portfolio_data.append({
                        'ticker': ticker,
                        'value': position_value,
                        'weight': 0,  # Will calculate after total
                        'returns': returns,
                        'volatility': volatility,
                        'beta': info.get('beta', 1.0)
                    })
            
            if not portfolio_data:
                return "Could not retrieve sufficient data for risk analysis."
            
            # Calculate weights
            for stock in portfolio_data:
                stock['weight'] = stock['value'] / total_value
            
            # Calculate portfolio metrics
            portfolio_volatility = sum(stock['volatility'] * stock['weight'] for stock in portfolio_data)
            portfolio_beta = sum(stock['beta'] * stock['weight'] for stock in portfolio_data)
            
            # Calculate portfolio returns for Sharpe ratio
            # Simple weighted average approach
            total_return = 0
            for stock in portfolio_data:
                avg_return = stock['returns'].mean() * 252
                total_return += avg_return * stock['weight']
            
            risk_free_rate = 0.04
            sharpe_ratio = (total_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Display results
            result += "📊 OVERALL PORTFOLIO RISK\n"
            result += f"   Portfolio Value: ${total_value:,.2f}\n"
            result += f"   Number of Holdings: {len(portfolio_data)}\n"
            result += f"   Portfolio Beta: {portfolio_beta:.2f}\n"
            result += f"   Portfolio Volatility: {portfolio_volatility * 100:.2f}%\n"
            result += f"   Portfolio Sharpe Ratio: {sharpe_ratio:.2f}\n\n"
            
            # Risk rating
            result += "⚠️ RISK RATING\n"
            if portfolio_volatility > 0.30:
                risk_rating = "🔴 HIGH RISK - Very volatile portfolio"
            elif portfolio_volatility > 0.20:
                risk_rating = "🟡 MODERATE-HIGH RISK - Above average volatility"
            elif portfolio_volatility > 0.15:
                risk_rating = "🟢 MODERATE RISK - Average market volatility"
            else:
                risk_rating = "🟢 LOW RISK - Conservative portfolio"
            
            result += f"   {risk_rating}\n\n"
            
            # Individual position risks
            result += "📋 POSITION RISK BREAKDOWN\n"
            portfolio_data.sort(key=lambda x: x['volatility'], reverse=True)
            
            for stock in portfolio_data:
                result += f"\n   {stock['ticker']}\n"
                result += f"      Weight: {stock['weight'] * 100:.1f}% | Value: ${stock['value']:,.2f}\n"
                result += f"      Volatility: {stock['volatility'] * 100:.2f}% | Beta: {stock['beta']:.2f}\n"
            
            # Concentration risk
            result += "\n\n🎯 CONCENTRATION RISK\n"
            max_position = max(stock['weight'] for stock in portfolio_data)
            top_3_concentration = sum(sorted([s['weight'] for s in portfolio_data], reverse=True)[:3])
            
            result += f"   Largest Position: {max_position * 100:.1f}%\n"
            result += f"   Top 3 Concentration: {top_3_concentration * 100:.1f}%\n"
            
            if max_position > 0.30:
                conc_risk = "🔴 HIGH - Portfolio heavily concentrated"
            elif max_position > 0.20:
                conc_risk = "🟡 MODERATE - Some concentration present"
            else:
                conc_risk = "🟢 LOW - Well diversified"
            
            result += f"   Concentration Risk: {conc_risk}\n"
            
            # Recommendations
            result += "\n\n💡 RECOMMENDATIONS\n"
            if portfolio_volatility > 0.25:
                result += "   • Consider adding more defensive stocks to reduce volatility\n"
            if max_position > 0.25:
                result += "   • Reduce concentration in largest position\n"
            if portfolio_beta > 1.3:
                result += "   • Portfolio is more volatile than market - consider adding low-beta stocks\n"
            if len(portfolio_data) < 5:
                result += "   • Increase diversification with more holdings (aim for 10-20)\n"
            if sharpe_ratio < 0.5:
                result += "   • Risk-adjusted returns are low - review underperforming positions\n"
            
            if portfolio_volatility <= 0.20 and max_position <= 0.20 and len(portfolio_data) >= 10:
                result += "   ✅ Portfolio shows good diversification and risk management\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating portfolio risk: {e}"

    @mcp.tool()
    def calculate_var(ticker: str, confidence_level: float = 0.95, period: str = "1y", position_size: float = 10000) -> str:
        """
        Calculate Value at Risk (VaR) - maximum expected loss at a given confidence level.

        Args:
            ticker: The stock ticker symbol.
            confidence_level: Confidence level (default: 0.95 for 95%).
            period: Historical period for calculation (default: '1y').
            position_size: Position value in dollars (default: $10,000).

        Returns:
            VaR calculation and interpretation.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period=period)
            
            if len(hist) < 30:
                return f"Not enough data to calculate VaR for {ticker.upper()}."
            
            # Calculate daily returns
            returns = hist['Close'].pct_change().dropna()
            
            # Calculate VaR using historical method
            var_percentile = np.percentile(returns, (1 - confidence_level) * 100)
            var_dollar = position_size * abs(var_percentile)
            
            # Also calculate using parametric method (assumes normal distribution)
            mean_return = returns.mean()
            std_return = returns.std()
            z_score = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}.get(confidence_level, 1.65)
            parametric_var = position_size * (mean_return - z_score * std_return)
            
            result = f"⚠️ VALUE AT RISK (VaR) for {ticker.upper()}\n"
            result += "="*70 + "\n\n"
            
            result += "📊 VAR METRICS\n"
            result += f"   Position Size: ${position_size:,.2f}\n"
            result += f"   Confidence Level: {confidence_level * 100:.0f}%\n"
            result += f"   Time Horizon: 1 day\n\n"
            
            result += "📉 CALCULATIONS\n"
            result += f"   Historical VaR: ${var_dollar:,.2f}\n"
            result += f"   Parametric VaR: ${abs(parametric_var):,.2f}\n\n"
            
            result += "💡 INTERPRETATION\n"
            result += f"   With {confidence_level * 100:.0f}% confidence, you should not lose more than\n"
            result += f"   ${var_dollar:,.2f} in a single day on this ${position_size:,.2f} position.\n\n"
            
            result += f"   This means there's a {(1-confidence_level)*100:.0f}% chance of losing more than ${var_dollar:,.2f}\n"
            result += "   in a single day.\n\n"
            
            # Risk assessment
            var_percentage = (var_dollar / position_size) * 100
            if var_percentage > 5:
                risk_level = "🔴 HIGH RISK - Significant daily loss potential"
            elif var_percentage > 3:
                risk_level = "🟡 MODERATE RISK - Notable daily volatility"
            else:
                risk_level = "🟢 LOW RISK - Limited daily loss potential"
            
            result += f"   Daily VaR: {var_percentage:.2f}% of position\n"
            result += f"   {risk_level}\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating VaR: {e}"

    @mcp.tool()
    def calculate_drawdown(ticker: str, period: str = "5y") -> str:
        """
        Calculate maximum drawdown - largest peak-to-trough decline.
        Important for understanding worst-case scenarios.

        Args:
            ticker: The stock ticker symbol.
            period: Time period for analysis (default: '5y').

        Returns:
            Drawdown analysis including maximum drawdown.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period=period)
            
            if len(hist) < 30:
                return f"Not enough data to calculate drawdown for {ticker.upper()}."
            
            # Calculate cumulative returns
            prices = hist['Close']
            
            # Calculate running maximum
            running_max = prices.expanding().max()
            
            # Calculate drawdown
            drawdown = (prices - running_max) / running_max
            
            # Find maximum drawdown
            max_drawdown = drawdown.min()
            max_dd_date = drawdown.idxmin()
            
            # Find the peak before max drawdown
            max_dd_idx = prices.index.get_loc(max_dd_date)
            peak_price = running_max.iloc[max_dd_idx]
            trough_price = prices.iloc[max_dd_idx]
            
            # Current drawdown
            current_price = prices.iloc[-1]
            current_max = running_max.iloc[-1]
            current_drawdown = (current_price - current_max) / current_max
            
            result = f"📉 DRAWDOWN ANALYSIS for {ticker.upper()}\n"
            result += "="*70 + "\n\n"
            
            result += "📊 MAXIMUM DRAWDOWN\n"
            result += f"   Peak Price: ${peak_price:.2f}\n"
            result += f"   Trough Price: ${trough_price:.2f}\n"
            result += f"   Maximum Drawdown: {max_drawdown * 100:.2f}%\n"
            result += f"   Date of Trough: {max_dd_date.strftime('%Y-%m-%d')}\n\n"
            
            result += "📊 CURRENT STATUS\n"
            result += f"   Current Price: ${current_price:.2f}\n"
            result += f"   All-Time High: ${current_max:.2f}\n"
            result += f"   Current Drawdown: {current_drawdown * 100:.2f}%\n\n"
            
            if current_drawdown < -0.05:
                status = f"🔴 Currently {abs(current_drawdown * 100):.1f}% below all-time high"
            elif current_drawdown < -0.01:
                status = "🟡 Slightly below all-time high"
            else:
                status = "🟢 Near or at all-time high"
            
            result += f"   Status: {status}\n\n"
            
            result += "💡 INTERPRETATION\n"
            if abs(max_drawdown) > 0.50:
                risk = "🔴 VERY HIGH RISK - Severe historical drawdowns"
            elif abs(max_drawdown) > 0.30:
                risk = "🟡 HIGH RISK - Significant historical losses"
            elif abs(max_drawdown) > 0.20:
                risk = "🟢 MODERATE RISK - Typical market volatility"
            else:
                risk = "🟢 LOW RISK - Limited historical downside"
            
            result += f"   {risk}\n"
            result += f"\n   This stock has historically declined as much as {abs(max_drawdown * 100):.1f}%\n"
            result += "   from its peak. Be prepared for similar volatility.\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating drawdown: {e}"
