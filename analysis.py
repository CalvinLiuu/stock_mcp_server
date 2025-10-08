"""
Technical analysis functions for stock market analysis.
"""
import yfinance as yf
from typing import List
from mcp.server.fastmcp import FastMCP


def register_analysis_tools(mcp: FastMCP):
    """Register technical analysis tools with the MCP server."""
    
    @mcp.tool()
    def analyze_buy_opportunity(ticker: str) -> str:
        """
        Analyzes a stock for a potential buy opportunity using a simple moving average (SMA) crossover.
        A buy signal is indicated when the short-term SMA crosses above the long-term SMA.

        Args:
            ticker: The stock ticker symbol to analyze (e.g., 'NVDA').

        Returns:
            A string with the analysis conclusion: 'Potential Buy Signal', 'Hold or Sell Signal', or 'Not Enough Data'.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")  # Get 6 months of data for analysis
            if len(hist) < 50:
                return f"Not enough historical data for {ticker.upper()} to perform analysis."

            # Calculate short-term (20-day) and long-term (50-day) SMAs
            hist['SMA20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA50'] = hist['Close'].rolling(window=50).mean()

            # Get the most recent values
            last_sma20 = hist['SMA20'].iloc[-1]
            last_sma50 = hist['SMA50'].iloc[-1]
            
            # Check for the crossover signal in the last few days
            prev_sma20 = hist['SMA20'].iloc[-2]
            prev_sma50 = hist['SMA50'].iloc[-2]

            # A buy signal is when the short-term SMA crosses *above* the long-term SMA
            if last_sma20 > last_sma50 and prev_sma20 <= prev_sma50:
                return f"Analysis for {ticker.upper()}: Potential Buy Signal. The 20-day SMA just crossed above the 50-day SMA."
            elif last_sma20 > last_sma50:
                return f"Analysis for {ticker.upper()}: Hold or Potential Buy. The short-term trend (20-day SMA) is currently above the long-term trend (50-day SMA)."
            else:
                return f"Analysis for {ticker.upper()}: Hold or Sell Signal. The short-term trend is below the long-term trend."

        except Exception as e:
            return f"An error occurred during analysis: {e}"

    @mcp.tool()
    def calculate_rsi(ticker: str, period: int = 14, timeframe: str = "3mo") -> str:
        """
        Calculate the Relative Strength Index (RSI) for a stock.
        RSI values above 70 indicate overbought, below 30 indicate oversold.

        Args:
            ticker: The stock ticker symbol.
            period: RSI period (default: 14 days).
            timeframe: Data timeframe (default: '3mo').

        Returns:
            Current RSI value and interpretation.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period=timeframe)
            
            if len(hist) < period + 1:
                return f"Not enough data to calculate RSI for {ticker.upper()}."
            
            # Calculate price changes
            delta = hist['Close'].diff()
            
            # Separate gains and losses
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Calculate RS and RSI
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            prev_rsi = rsi.iloc[-2]
            
            # Interpretation
            if current_rsi > 70:
                signal = "⚠️ OVERBOUGHT - Consider selling or waiting"
            elif current_rsi < 30:
                signal = "🎯 OVERSOLD - Potential buy opportunity"
            else:
                signal = "✅ NEUTRAL - Normal trading range"
            
            trend = "📈 Rising" if current_rsi > prev_rsi else "📉 Falling"
            
            result = f"📊 RSI Analysis for {ticker.upper()}\n"
            result += "="*50 + "\n"
            result += f"Current RSI ({period}-day): {current_rsi:.2f}\n"
            result += f"Trend: {trend}\n"
            result += f"Signal: {signal}\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating RSI: {e}"

    @mcp.tool()
    def calculate_macd(ticker: str, timeframe: str = "6mo") -> str:
        """
        Calculate MACD (Moving Average Convergence Divergence) for trend analysis.
        MACD crossing above signal line indicates bullish, below indicates bearish.

        Args:
            ticker: The stock ticker symbol.
            timeframe: Data timeframe (default: '6mo').

        Returns:
            MACD values and trading signal.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period=timeframe)
            
            if len(hist) < 26:
                return f"Not enough data to calculate MACD for {ticker.upper()}."
            
            # Calculate MACD
            exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            current_histogram = histogram.iloc[-1]
            prev_histogram = histogram.iloc[-2]
            
            # Determine signal
            if current_macd > current_signal and prev_histogram < 0:
                trading_signal = "🟢 BULLISH CROSSOVER - Potential buy signal"
            elif current_macd < current_signal and prev_histogram > 0:
                trading_signal = "🔴 BEARISH CROSSOVER - Potential sell signal"
            elif current_macd > current_signal:
                trading_signal = "📈 BULLISH - Upward momentum"
            else:
                trading_signal = "📉 BEARISH - Downward momentum"
            
            result = f"📊 MACD Analysis for {ticker.upper()}\n"
            result += "="*50 + "\n"
            result += f"MACD Line: {current_macd:.2f}\n"
            result += f"Signal Line: {current_signal:.2f}\n"
            result += f"Histogram: {current_histogram:.2f}\n"
            result += f"Signal: {trading_signal}\n"
            
            return result
        
        except Exception as e:
            return f"Error calculating MACD: {e}"

    @mcp.tool()
    def analyze_trends(ticker: str, timeframe: str = "1y") -> str:
        """
        Comprehensive trend analysis combining multiple indicators.

        Args:
            ticker: The stock ticker symbol.
            timeframe: Data timeframe (default: '1y').

        Returns:
            Multi-indicator trend analysis with overall recommendation.
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period=timeframe)
            
            if len(hist) < 50:
                return f"Not enough data for trend analysis of {ticker.upper()}."
            
            # Calculate various metrics
            current_price = hist['Close'].iloc[-1]
            
            # Moving Averages
            sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            sma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            sma200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None
            
            # Price vs MAs
            price_vs_sma20 = ((current_price - sma20) / sma20) * 100
            price_vs_sma50 = ((current_price - sma50) / sma50) * 100
            
            # Volume trend
            avg_volume = hist['Volume'].mean()
            recent_volume = hist['Volume'].tail(5).mean()
            volume_trend = "High" if recent_volume > avg_volume * 1.2 else "Normal" if recent_volume > avg_volume * 0.8 else "Low"
            
            # Volatility
            returns = hist['Close'].pct_change()
            volatility = returns.std() * 100
            
            # Overall trend
            signals = []
            if current_price > sma20:
                signals.append(1)
            else:
                signals.append(-1)
            
            if current_price > sma50:
                signals.append(1)
            else:
                signals.append(-1)
            
            if sma20 > sma50:
                signals.append(1)
            else:
                signals.append(-1)
            
            avg_signal = sum(signals) / len(signals)
            
            if avg_signal > 0.3:
                overall = "🟢 BULLISH - Strong upward trend"
            elif avg_signal < -0.3:
                overall = "🔴 BEARISH - Strong downward trend"
            else:
                overall = "🟡 NEUTRAL - Mixed signals"
            
            result = f"📊 COMPREHENSIVE TREND ANALYSIS for {ticker.upper()}\n"
            result += "="*70 + "\n\n"
            
            result += f"💰 Current Price: ${current_price:.2f}\n\n"
            
            result += "📈 MOVING AVERAGES\n"
            result += f"   20-day SMA: ${sma20:.2f} ({price_vs_sma20:+.2f}%)\n"
            result += f"   50-day SMA: ${sma50:.2f} ({price_vs_sma50:+.2f}%)\n"
            if sma200:
                price_vs_sma200 = ((current_price - sma200) / sma200) * 100
                result += f"   200-day SMA: ${sma200:.2f} ({price_vs_sma200:+.2f}%)\n"
            result += "\n"
            
            result += "📊 MARKET ACTIVITY\n"
            result += f"   Volume Trend: {volume_trend}\n"
            result += f"   Volatility: {volatility:.2f}%\n\n"
            
            result += f"🎯 OVERALL SIGNAL: {overall}\n"
            
            return result
        
        except Exception as e:
            return f"Error analyzing trends: {e}"

    @mcp.tool()
    def compare_stocks(tickers: List[str]) -> str:
        """
        Compare multiple stocks side by side with key metrics.

        Args:
            tickers: List of stock ticker symbols to compare (e.g., ['AAPL', 'MSFT', 'GOOGL']).

        Returns:
            Comparison table with key metrics for all stocks.
        """
        try:
            if len(tickers) < 2:
                return "Please provide at least 2 tickers to compare."
            
            result = "📊 STOCK COMPARISON\n"
            result += "="*100 + "\n\n"
            
            comparison_data = []
            
            for ticker in tickers:
                ticker = ticker.upper().strip()
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="3mo")
                
                if not hist.empty:
                    # Calculate returns
                    three_month_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    
                    comparison_data.append({
                        'ticker': ticker,
                        'price': info.get('regularMarketPrice', 0),
                        'market_cap': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', 'N/A'),
                        '3mo_return': three_month_return,
                        'volume': info.get('volume', 0),
                        'div_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
                    })
            
            # Display comparison
            for data in comparison_data:
                result += f"🏢 {data['ticker']}\n"
                result += f"   Price: ${data['price']:.2f}\n"
                result += f"   Market Cap: ${data['market_cap']:,.0f}\n"
                result += f"   P/E Ratio: {data['pe_ratio']}\n"
                result += f"   3-Month Return: {data['3mo_return']:+.2f}%\n"
                result += f"   Volume: {data['volume']:,}\n"
                result += f"   Dividend Yield: {data['div_yield']:.2f}%\n\n"
            
            # Find best performers
            if comparison_data:
                best_return = max(comparison_data, key=lambda x: x['3mo_return'])
                result += f"🏆 Best 3-Month Return: {best_return['ticker']} ({best_return['3mo_return']:+.2f}%)\n"
            
            return result
        
        except Exception as e:
            return f"Error comparing stocks: {e}"
