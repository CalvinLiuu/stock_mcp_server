"""
Sector analysis functions for analyzing market sectors and industries.
"""
import yfinance as yf
from typing import List, Optional
from mcp.server.fastmcp import FastMCP


def register_sector_tools(mcp: FastMCP):
    """Register sector analysis tools with the MCP server."""
    
    @mcp.tool()
    def analyze_sector(sector_name: str) -> str:
        """
        Analyze a specific market sector by examining representative stocks.

        Args:
            sector_name: Name of the sector (e.g., 'Technology', 'Healthcare', 'Financial Services', 'Energy', 'Consumer Cyclical', 'Utilities').

        Returns:
            Comprehensive sector analysis with performance metrics.
        """
        try:
            # Representative stocks for each sector
            sector_stocks = {
                'technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC', 'CSCO', 'ORCL', 'ADBE'],
                'healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'LLY', 'MRK', 'BMY', 'AMGN'],
                'financial services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'USB'],
                'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
                'consumer cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'CMG'],
                'consumer defensive': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'PM', 'MO', 'CL', 'MDLZ', 'KMB'],
                'utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'PEG', 'XEL', 'ED'],
                'industrials': ['UPS', 'HON', 'UNP', 'BA', 'CAT', 'GE', 'MMM', 'LMT', 'RTX', 'DE'],
                'real estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'SPG', 'O', 'WELL', 'DLR', 'AVB'],
                'materials': ['LIN', 'APD', 'SHW', 'ECL', 'DD', 'NEM', 'FCX', 'NUE', 'VMC', 'MLM'],
                'communication services': ['GOOGL', 'META', 'DIS', 'NFLX', 'CMCSA', 'T', 'VZ', 'TMUS', 'EA', 'TTWO']
            }
            
            sector_key = sector_name.lower()
            if sector_key not in sector_stocks:
                available = ', '.join([s.title() for s in sector_stocks.keys()])
                return f"Sector '{sector_name}' not recognized. Available sectors: {available}"
            
            tickers = sector_stocks[sector_key]
            
            result = f"📊 SECTOR ANALYSIS: {sector_name.upper()}\n"
            result += "="*70 + "\n\n"
            
            sector_data = []
            total_market_cap = 0
            
            for ticker in tickers[:10]:  # Analyze top 10 stocks
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    hist = stock.history(period="3mo")
                    
                    if not hist.empty:
                        current_price = info.get('regularMarketPrice', 0)
                        market_cap = info.get('marketCap', 0)
                        pe_ratio = info.get('trailingPE', 0)
                        
                        # Calculate 3-month return
                        start_price = hist['Close'].iloc[0]
                        end_price = hist['Close'].iloc[-1]
                        three_month_return = ((end_price - start_price) / start_price) * 100
                        
                        sector_data.append({
                            'ticker': ticker,
                            'name': info.get('shortName', ticker),
                            'price': current_price,
                            'market_cap': market_cap,
                            'pe_ratio': pe_ratio,
                            '3mo_return': three_month_return,
                            'volume': info.get('volume', 0)
                        })
                        
                        total_market_cap += market_cap
                except:
                    continue
            
            if not sector_data:
                return f"Could not retrieve data for {sector_name} sector."
            
            # Calculate sector averages
            avg_return = sum(s['3mo_return'] for s in sector_data) / len(sector_data)
            avg_pe = sum(s['pe_ratio'] for s in sector_data if s['pe_ratio']) / len([s for s in sector_data if s['pe_ratio']])
            
            result += "📈 SECTOR OVERVIEW\n"
            result += f"   Total Market Cap: ${total_market_cap:,.0f}\n"
            result += f"   Average 3-Month Return: {avg_return:+.2f}%\n"
            result += f"   Average P/E Ratio: {avg_pe:.2f}\n"
            result += f"   Stocks Analyzed: {len(sector_data)}\n\n"
            
            # Sort by performance
            sector_data.sort(key=lambda x: x['3mo_return'], reverse=True)
            
            result += "🏆 TOP PERFORMERS (3-Month Return)\n"
            for stock in sector_data[:5]:
                result += f"   {stock['ticker']}: {stock['3mo_return']:+.2f}% | ${stock['price']:.2f}\n"
            
            result += "\n📉 BOTTOM PERFORMERS (3-Month Return)\n"
            for stock in sector_data[-3:]:
                result += f"   {stock['ticker']}: {stock['3mo_return']:+.2f}% | ${stock['price']:.2f}\n"
            
            result += "\n💰 LARGEST BY MARKET CAP\n"
            sector_data.sort(key=lambda x: x['market_cap'], reverse=True)
            for stock in sector_data[:5]:
                result += f"   {stock['ticker']}: ${stock['market_cap']:,.0f}\n"
            
            # Sector health indicator
            result += "\n🎯 SECTOR HEALTH\n"
            positive_returns = len([s for s in sector_data if s['3mo_return'] > 0])
            health_pct = (positive_returns / len(sector_data)) * 100
            
            if health_pct >= 70:
                health = "🟢 STRONG - Most stocks performing well"
            elif health_pct >= 40:
                health = "🟡 MIXED - Sector showing varied performance"
            else:
                health = "🔴 WEAK - Majority of stocks underperforming"
            
            result += f"   {health}\n"
            result += f"   {positive_returns}/{len(sector_data)} stocks with positive returns\n"
            
            return result
        
        except Exception as e:
            return f"Error analyzing sector: {e}"

    @mcp.tool()
    def compare_sectors() -> str:
        """
        Compare performance across major market sectors.

        Returns:
            Comparative analysis of all major sectors.
        """
        try:
            # Use sector ETFs for quick comparison
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV',
                'Financials': 'XLF',
                'Energy': 'XLE',
                'Consumer Discretionary': 'XLY',
                'Consumer Staples': 'XLP',
                'Utilities': 'XLU',
                'Industrials': 'XLI',
                'Real Estate': 'XLRE',
                'Materials': 'XLB',
                'Communication Services': 'XLC'
            }
            
            result = "📊 SECTOR COMPARISON (via Sector ETFs)\n"
            result += "="*70 + "\n\n"
            
            sector_performance = []
            
            for sector, etf in sector_etfs.items():
                try:
                    stock = yf.Ticker(etf)
                    hist = stock.history(period="1y")
                    
                    if not hist.empty:
                        # Calculate returns
                        current_price = hist['Close'].iloc[-1]
                        
                        # 1-month return
                        one_month_ago = hist['Close'].iloc[-22] if len(hist) >= 22 else hist['Close'].iloc[0]
                        one_month_return = ((current_price - one_month_ago) / one_month_ago) * 100
                        
                        # 3-month return
                        three_month_ago = hist['Close'].iloc[-66] if len(hist) >= 66 else hist['Close'].iloc[0]
                        three_month_return = ((current_price - three_month_ago) / three_month_ago) * 100
                        
                        # 1-year return
                        one_year_ago = hist['Close'].iloc[0]
                        one_year_return = ((current_price - one_year_ago) / one_year_ago) * 100
                        
                        sector_performance.append({
                            'sector': sector,
                            'etf': etf,
                            '1mo': one_month_return,
                            '3mo': three_month_return,
                            '1yr': one_year_return
                        })
                except:
                    continue
            
            if not sector_performance:
                return "Could not retrieve sector comparison data."
            
            # Sort by 3-month performance
            sector_performance.sort(key=lambda x: x['3mo'], reverse=True)
            
            result += "📈 PERFORMANCE RANKINGS (3-Month)\n\n"
            for i, sector in enumerate(sector_performance, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                result += f"{emoji} {i}. {sector['sector']} ({sector['etf']})\n"
                result += f"      1M: {sector['1mo']:+.2f}% | 3M: {sector['3mo']:+.2f}% | 1Y: {sector['1yr']:+.2f}%\n\n"
            
            # Best and worst performers
            result += "="*70 + "\n"
            best = sector_performance[0]
            worst = sector_performance[-1]
            result += f"🏆 Best 3M: {best['sector']} ({best['3mo']:+.2f}%)\n"
            result += f"📉 Worst 3M: {worst['sector']} ({worst['3mo']:+.2f}%)\n"
            
            return result
        
        except Exception as e:
            return f"Error comparing sectors: {e}"

    @mcp.tool()
    def get_sector_leaders(sector_name: str, metric: str = "return") -> str:
        """
        Get the top performing stocks in a specific sector.

        Args:
            sector_name: Name of the sector to analyze.
            metric: Metric to rank by - 'return' (3-month return), 'market_cap', 'volume', or 'dividend_yield'.

        Returns:
            Ranked list of sector leaders by chosen metric.
        """
        try:
            # Representative stocks for each sector
            sector_stocks = {
                'technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC', 'CSCO', 'ORCL', 'ADBE', 'CRM', 'AVGO', 'TXN', 'QCOM', 'NOW'],
                'healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'LLY', 'MRK', 'BMY', 'AMGN', 'DHR', 'CVS', 'MDT', 'GILD', 'CI'],
                'financial services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'USB', 'PNC', 'TFC', 'COF', 'BK', 'SPG'],
                'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL', 'KMI', 'WMB', 'HES', 'DVN', 'BKR'],
                'consumer cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'CMG', 'F', 'GM', 'MAR', 'BKNG', 'YUM']
            }
            
            sector_key = sector_name.lower()
            if sector_key not in sector_stocks:
                available = ', '.join([s.title() for s in sector_stocks.keys()])
                return f"Sector '{sector_name}' not recognized. Available sectors: {available}"
            
            tickers = sector_stocks[sector_key]
            
            result = f"🏆 {sector_name.upper()} SECTOR LEADERS (by {metric})\n"
            result += "="*70 + "\n\n"
            
            stocks_data = []
            
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    hist = stock.history(period="3mo")
                    
                    if not hist.empty:
                        # Calculate 3-month return
                        three_month_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        
                        stocks_data.append({
                            'ticker': ticker,
                            'name': info.get('shortName', ticker),
                            'return': three_month_return,
                            'market_cap': info.get('marketCap', 0),
                            'volume': info.get('averageVolume', 0),
                            'dividend_yield': info.get('dividendYield', 0) * 100,
                            'price': info.get('regularMarketPrice', 0),
                            'pe_ratio': info.get('trailingPE', 0)
                        })
                except:
                    continue
            
            if not stocks_data:
                return f"Could not retrieve data for {sector_name} sector."
            
            # Sort by chosen metric
            sort_key = {
                'return': 'return',
                'market_cap': 'market_cap',
                'volume': 'volume',
                'dividend_yield': 'dividend_yield'
            }.get(metric, 'return')
            
            stocks_data.sort(key=lambda x: x[sort_key], reverse=True)
            
            # Display top 10
            for i, stock in enumerate(stocks_data[:10], 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:2d}."
                result += f"{emoji} {stock['ticker']} - {stock['name']}\n"
                result += f"    Price: ${stock['price']:.2f} | P/E: {stock['pe_ratio']:.2f}\n"
                
                if metric == 'return':
                    result += f"    3-Month Return: {stock['return']:+.2f}%\n"
                elif metric == 'market_cap':
                    result += f"    Market Cap: ${stock['market_cap']:,.0f}\n"
                elif metric == 'volume':
                    result += f"    Avg Volume: {stock['volume']:,.0f}\n"
                elif metric == 'dividend_yield':
                    result += f"    Dividend Yield: {stock['dividend_yield']:.2f}%\n"
                
                result += "\n"
            
            return result
        
        except Exception as e:
            return f"Error getting sector leaders: {e}"

    @mcp.tool()
    def analyze_portfolio_sector_allocation() -> str:
        """
        Analyze the sector allocation of your portfolio holdings.

        Returns:
            Breakdown of portfolio by sector with diversification metrics.
        """
        try:
            from utils import load_portfolio
            
            portfolio = load_portfolio()
            
            if not portfolio["holdings"]:
                return "Your portfolio is empty. Add holdings to see sector allocation."
            
            result = "🎯 PORTFOLIO SECTOR ALLOCATION\n"
            result += "="*70 + "\n\n"
            
            sector_allocation = {}
            total_value = 0
            
            for ticker, holding in portfolio["holdings"].items():
                shares = holding["shares"]
                
                stock = yf.Ticker(ticker)
                info = stock.info
                
                current_price = info.get('regularMarketPrice', 0)
                sector = info.get('sector', 'Unknown')
                
                position_value = shares * current_price
                total_value += position_value
                
                if sector in sector_allocation:
                    sector_allocation[sector]['value'] += position_value
                    sector_allocation[sector]['stocks'].append(ticker)
                else:
                    sector_allocation[sector] = {
                        'value': position_value,
                        'stocks': [ticker]
                    }
            
            # Calculate percentages and sort
            sector_list = []
            for sector, data in sector_allocation.items():
                percentage = (data['value'] / total_value * 100) if total_value > 0 else 0
                sector_list.append({
                    'sector': sector,
                    'value': data['value'],
                    'percentage': percentage,
                    'stocks': data['stocks'],
                    'count': len(data['stocks'])
                })
            
            sector_list.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Display allocation
            result += "📊 ALLOCATION BY SECTOR\n\n"
            for sector_data in sector_list:
                bar_length = int(sector_data['percentage'] / 2)  # Scale to 50 chars max
                bar = '█' * bar_length
                
                result += f"{sector_data['sector']}\n"
                result += f"   {bar} {sector_data['percentage']:.1f}%\n"
                result += f"   Value: ${sector_data['value']:,.2f} | Stocks: {', '.join(sector_data['stocks'])}\n\n"
            
            # Diversification analysis
            result += "="*70 + "\n"
            result += "📈 DIVERSIFICATION ANALYSIS\n\n"
            
            num_sectors = len(sector_allocation)
            result += f"   Sectors Represented: {num_sectors}\n"
            
            top_sector_pct = sector_list[0]['percentage']
            if top_sector_pct > 50:
                div_rating = "🔴 LOW - Highly concentrated in one sector"
            elif top_sector_pct > 35:
                div_rating = "🟡 MODERATE - Good diversification, slight concentration"
            else:
                div_rating = "🟢 HIGH - Well diversified across sectors"
            
            result += f"   Diversification: {div_rating}\n"
            result += f"   Largest Allocation: {sector_list[0]['sector']} ({top_sector_pct:.1f}%)\n"
            
            return result
        
        except Exception as e:
            return f"Error analyzing sector allocation: {e}"