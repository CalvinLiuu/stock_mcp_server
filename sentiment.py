"""
Market sentiment analysis and tracking.
Aggregates multiple market indicators to provide bearish/bullish signals.
"""
import yfinance as yf
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from utils import load_sentiment_history, save_sentiment_history


def calculate_vix_signal() -> Tuple[float, str, float]:
    """Calculate VIX-based sentiment signal."""
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")
        if hist.empty:
            return 0, "N/A", 0
        
        current_vix = hist['Close'].iloc[-1]
        
        # Scoring: VIX < 12 = very bullish (+10), VIX > 30 = very bearish (-10)
        if current_vix < 12:
            score = 10
            signal = "🟢 VERY BULLISH (Complacency)"
        elif current_vix < 15:
            score = 5
            signal = "🟢 BULLISH (Low Fear)"
        elif current_vix < 20:
            score = 0
            signal = "🟡 NEUTRAL (Normal)"
        elif current_vix < 25:
            score = -5
            signal = "🟠 BEARISH (Elevated)"
        elif current_vix < 30:
            score = -8
            signal = "🔴 BEARISH (High Fear)"
        else:
            score = -10
            signal = "🔴 VERY BEARISH (Panic)"
        
        return score, signal, current_vix
    except Exception as e:
        return 0, f"Error: {e}", 0


def calculate_index_trend_signal(ticker: str, sma_period: int = 200) -> Tuple[float, str, float, float]:
    """Calculate trend signal based on price vs moving average."""
    try:
        index = yf.Ticker(ticker)
        hist = index.history(period="1y")
        if len(hist) < sma_period:
            return 0, "N/A", 0, 0
        
        current_price = hist['Close'].iloc[-1]
        sma = hist['Close'].rolling(window=sma_period).mean().iloc[-1]
        diff_pct = ((current_price - sma) / sma) * 100
        
        # Scoring: >+5% = bullish, <-5% = bearish
        if diff_pct > 8:
            score = 10
            signal = "🟢 STRONG UPTREND"
        elif diff_pct > 3:
            score = 5
            signal = "🟢 UPTREND"
        elif diff_pct > -3:
            score = 0
            signal = "🟡 NEUTRAL"
        elif diff_pct > -8:
            score = -5
            signal = "🔴 DOWNTREND"
        else:
            score = -10
            signal = "🔴 STRONG DOWNTREND"
        
        return score, signal, diff_pct, current_price
    except Exception as e:
        return 0, f"Error: {e}", 0, 0


def calculate_put_call_ratio_signal() -> Tuple[float, str, float]:
    """Estimate put/call ratio from index behavior."""
    try:
        # We'll use VIX behavior as a proxy since direct P/C ratio isn't in yfinance
        # High VIX correlates with high put buying
        vix = yf.Ticker("^VIX")
        spy = yf.Ticker("SPY")
        
        vix_hist = vix.history(period="1mo")
        spy_hist = spy.history(period="1mo")
        
        if vix_hist.empty or spy_hist.empty:
            return 0, "N/A", 0
        
        # Calculate volatility and recent trend
        current_vix = vix_hist['Close'].iloc[-1]
        avg_vix = vix_hist['Close'].mean()
        
        # Proxy P/C ratio: higher VIX relative to average = more puts
        pc_proxy = current_vix / avg_vix
        
        if pc_proxy < 0.8:
            score = 8
            signal = "🟢 BULLISH (Low hedging)"
        elif pc_proxy < 1.0:
            score = 3
            signal = "🟢 SLIGHTLY BULLISH"
        elif pc_proxy < 1.2:
            score = 0
            signal = "🟡 NEUTRAL"
        elif pc_proxy < 1.4:
            score = -5
            signal = "🔴 BEARISH (High hedging)"
        else:
            score = -8
            signal = "🔴 VERY BEARISH (Heavy hedging)"
        
        return score, signal, pc_proxy
    except Exception as e:
        return 0, f"Error: {e}", 0


def calculate_sector_rotation_signal() -> Tuple[float, str, str]:
    """Detect sector rotation patterns (defensive vs growth)."""
    try:
        # Defensive: XLP (Staples), XLU (Utilities), XLV (Healthcare)
        # Growth: XLK (Tech), XLY (Consumer Discretionary)
        
        defensive_tickers = ['XLP', 'XLU', 'XLV']
        growth_tickers = ['XLK', 'XLY', 'QQQ']
        
        defensive_performance = []
        growth_performance = []
        
        # Calculate 1-month performance with more data
        for ticker in defensive_tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2mo")
                if not hist.empty and len(hist) > 10:
                    # Use last 20 trading days
                    perf = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100
                    defensive_performance.append(perf)
            except:
                continue
        
        for ticker in growth_tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2mo")
                if not hist.empty and len(hist) > 10:
                    # Use last 20 trading days
                    perf = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]) * 100
                    growth_performance.append(perf)
            except:
                continue
        
        if not defensive_performance or not growth_performance:
            return 0, "N/A", "Insufficient data"
        
        avg_defensive = sum(defensive_performance) / len(defensive_performance)
        avg_growth = sum(growth_performance) / len(growth_performance)
        
        rotation = avg_growth - avg_defensive
        
        if rotation > 3:
            score = 8
            signal = "🟢 BULLISH (Growth leading)"
            detail = f"Growth +{avg_growth:.1f}% vs Defensive +{avg_defensive:.1f}%"
        elif rotation > 1:
            score = 3
            signal = "🟢 SLIGHTLY BULLISH"
            detail = f"Growth +{avg_growth:.1f}% vs Defensive +{avg_defensive:.1f}%"
        elif rotation > -1:
            score = 0
            signal = "🟡 NEUTRAL (Mixed)"
            detail = f"Growth {avg_growth:+.1f}% vs Defensive {avg_defensive:+.1f}%"
        elif rotation > -3:
            score = -5
            signal = "🔴 BEARISH (Defensive leading)"
            detail = f"Defensive {avg_defensive:+.1f}% vs Growth {avg_growth:+.1f}%"
        else:
            score = -8
            signal = "🔴 VERY BEARISH (Flight to safety)"
            detail = f"Defensive {avg_defensive:+.1f}% vs Growth {avg_growth:+.1f}%"
        
        return score, signal, detail
    except Exception as e:
        return 0, f"Error: {e}", str(e)


def calculate_market_breadth_signal() -> Tuple[float, str, float]:
    """Analyze market breadth across major sectors."""
    try:
        # Major sector ETFs
        sectors = ['XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'XLP', 'XLI', 'XLU', 'XLB']
        
        positive_sectors = 0
        total_sectors = 0
        
        for ticker in sectors:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2mo")
                if not hist.empty and len(hist) > 20:
                    total_sectors += 1
                    # Check if sector is up over past 20 trading days
                    start_price = hist['Close'].iloc[-20]
                    end_price = hist['Close'].iloc[-1]
                    perf = end_price - start_price
                    if perf > 0:
                        positive_sectors += 1
            except:
                continue
        
        if total_sectors == 0:
            return 0, "N/A", 0
        
        breadth_pct = (positive_sectors / total_sectors) * 100
        
        if breadth_pct >= 80:
            score = 10
            signal = "🟢 EXCELLENT (Strong participation)"
        elif breadth_pct >= 60:
            score = 5
            signal = "🟢 GOOD (Healthy participation)"
        elif breadth_pct >= 40:
            score = 0
            signal = "🟡 NEUTRAL (Mixed)"
        elif breadth_pct >= 25:
            score = -5
            signal = "🔴 POOR (Weak participation)"
        else:
            score = -10
            signal = "🔴 VERY POOR (Narrow market)"
        
        return score, signal, breadth_pct
    except Exception as e:
        return 0, f"Error: {e}", 0


def calculate_volume_trend_signal() -> Tuple[float, str, str]:
    """Analyze volume patterns (high volume on up vs down days)."""
    try:
        spy = yf.Ticker("SPY")
        hist = spy.history(period="1mo")
        
        if hist.empty or len(hist) < 10:
            return 0, "N/A", "Insufficient data"
        
        # Calculate average volume on up days vs down days
        up_days = hist[hist['Close'] > hist['Open']]
        down_days = hist[hist['Close'] < hist['Open']]
        
        if len(up_days) == 0 or len(down_days) == 0:
            return 0, "🟡 NEUTRAL", "Mixed signals"
        
        avg_up_volume = up_days['Volume'].mean()
        avg_down_volume = down_days['Volume'].mean()
        
        volume_ratio = avg_up_volume / avg_down_volume
        
        if volume_ratio > 1.3:
            score = 8
            signal = "🟢 BULLISH (Buying pressure)"
            detail = f"Up-day volume {volume_ratio:.1f}x down-day"
        elif volume_ratio > 1.1:
            score = 3
            signal = "🟢 SLIGHTLY BULLISH"
            detail = f"Up-day volume {volume_ratio:.1f}x down-day"
        elif volume_ratio > 0.9:
            score = 0
            signal = "🟡 NEUTRAL"
            detail = f"Volume ratio: {volume_ratio:.1f}"
        elif volume_ratio > 0.7:
            score = -5
            signal = "🔴 BEARISH (Selling pressure)"
            detail = f"Down-day volume {1/volume_ratio:.1f}x up-day"
        else:
            score = -8
            signal = "🔴 VERY BEARISH (Heavy selling)"
            detail = f"Down-day volume {1/volume_ratio:.1f}x up-day"
        
        return score, signal, detail
    except Exception as e:
        return 0, f"Error: {e}", str(e)


def calculate_ai_tech_signal() -> Tuple[float, str, str]:
    """Analyze AI/Tech sector strength relative to broader market."""
    try:
        qqq = yf.Ticker("QQQ")
        spy = yf.Ticker("SPY")
        
        qqq_hist = qqq.history(period="3mo")
        spy_hist = spy.history(period="3mo")
        
        if qqq_hist.empty or spy_hist.empty:
            return 0, "N/A", "Insufficient data"
        
        # Calculate 3-month performance
        qqq_perf = ((qqq_hist['Close'].iloc[-1] - qqq_hist['Close'].iloc[0]) / qqq_hist['Close'].iloc[0]) * 100
        spy_perf = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[0]) / spy_hist['Close'].iloc[0]) * 100
        
        outperformance = qqq_perf - spy_perf
        
        # Check AI bellwethers
        ai_stocks = ['NVDA', 'MSFT', 'GOOGL', 'META']
        ai_performance = []
        
        for ticker in ai_stocks:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            if not hist.empty and len(hist) > 5:
                perf = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                ai_performance.append(perf)
        
        avg_ai = sum(ai_performance) / len(ai_performance) if ai_performance else 0
        
        if outperformance > 5 and avg_ai > 5:
            score = 10
            signal = "🟢 VERY BULLISH (AI/Tech leading)"
            detail = f"QQQ outperforming by {outperformance:.1f}%, AI stocks +{avg_ai:.1f}%"
        elif outperformance > 2:
            score = 5
            signal = "🟢 BULLISH (Tech strength)"
            detail = f"QQQ +{outperformance:.1f}% vs SPY"
        elif outperformance > -2:
            score = 0
            signal = "🟡 NEUTRAL"
            detail = f"QQQ {outperformance:+.1f}% vs SPY"
        elif outperformance > -5:
            score = -5
            signal = "🔴 BEARISH (Tech weakness)"
            detail = f"QQQ underperforming by {abs(outperformance):.1f}%"
        else:
            score = -10
            signal = "🔴 VERY BEARISH (Tech selling)"
            detail = f"QQQ underperforming by {abs(outperformance):.1f}%, AI stocks {avg_ai:+.1f}%"
        
        return score, signal, detail
    except Exception as e:
        return 0, f"Error: {e}", str(e)


def calculate_leverage_indicator() -> Tuple[float, str, str]:
    """Estimate leverage in the system based on volatility patterns."""
    try:
        spy = yf.Ticker("SPY")
        hist = spy.history(period="3mo")
        
        if hist.empty or len(hist) < 30:
            return 0, "N/A", "Insufficient data"
        
        # Calculate recent volatility vs historical
        returns = hist['Close'].pct_change()
        recent_vol = returns.tail(20).std() * 100
        historical_vol = returns.std() * 100
        
        vol_ratio = recent_vol / historical_vol
        
        # High volatility suggests deleveraging/stress
        if vol_ratio > 1.5:
            score = -10
            signal = "🔴 HIGH STRESS (Deleveraging)"
            detail = f"Volatility {vol_ratio:.1f}x normal"
        elif vol_ratio > 1.2:
            score = -5
            signal = "🔴 ELEVATED (Unwinding)"
            detail = f"Volatility {vol_ratio:.1f}x normal"
        elif vol_ratio > 0.8:
            score = 0
            signal = "🟡 NORMAL"
            detail = f"Volatility at {vol_ratio:.1f}x normal"
        elif vol_ratio > 0.6:
            score = 5
            signal = "🟢 LOW (Stable)"
            detail = f"Volatility {vol_ratio:.1f}x normal"
        else:
            score = 8
            signal = "🟢 VERY LOW (Complacent)"
            detail = f"Volatility {vol_ratio:.1f}x normal"
        
        return score, signal, detail
    except Exception as e:
        return 0, f"Error: {e}", str(e)


def aggregate_sentiment_score() -> Dict:
    """Aggregate all signals into overall sentiment score."""
    
    # Signal weights
    weights = {
        'vix': 2.0,
        'spy_trend': 1.5,
        'qqq_trend': 1.5,
        'put_call': 1.5,
        'sector_rotation': 1.5,
        'breadth': 1.0,
        'volume': 1.0,
        'ai_tech': 1.5,
        'leverage': 1.0
    }
    
    # Calculate all signals
    signals = {}
    
    vix_score, vix_signal, vix_value = calculate_vix_signal()
    signals['vix'] = {'score': vix_score, 'signal': vix_signal, 'value': vix_value, 'weight': weights['vix']}
    
    spy_score, spy_signal, spy_diff, spy_price = calculate_index_trend_signal('SPY', 200)
    signals['spy_trend'] = {'score': spy_score, 'signal': spy_signal, 'value': f"{spy_diff:+.1f}% vs SMA200", 'weight': weights['spy_trend']}
    
    qqq_score, qqq_signal, qqq_diff, qqq_price = calculate_index_trend_signal('QQQ', 50)
    signals['qqq_trend'] = {'score': qqq_score, 'signal': qqq_signal, 'value': f"{qqq_diff:+.1f}% vs SMA50", 'weight': weights['qqq_trend']}
    
    pc_score, pc_signal, pc_value = calculate_put_call_ratio_signal()
    signals['put_call'] = {'score': pc_score, 'signal': pc_signal, 'value': f"{pc_value:.2f}", 'weight': weights['put_call']}
    
    sector_score, sector_signal, sector_detail = calculate_sector_rotation_signal()
    signals['sector_rotation'] = {'score': sector_score, 'signal': sector_signal, 'value': sector_detail, 'weight': weights['sector_rotation']}
    
    breadth_score, breadth_signal, breadth_pct = calculate_market_breadth_signal()
    signals['breadth'] = {'score': breadth_score, 'signal': breadth_signal, 'value': f"{breadth_pct:.0f}% sectors positive", 'weight': weights['breadth']}
    
    vol_score, vol_signal, vol_detail = calculate_volume_trend_signal()
    signals['volume'] = {'score': vol_score, 'signal': vol_signal, 'value': vol_detail, 'weight': weights['volume']}
    
    ai_score, ai_signal, ai_detail = calculate_ai_tech_signal()
    signals['ai_tech'] = {'score': ai_score, 'signal': ai_signal, 'value': ai_detail, 'weight': weights['ai_tech']}
    
    lev_score, lev_signal, lev_detail = calculate_leverage_indicator()
    signals['leverage'] = {'score': lev_score, 'signal': lev_signal, 'value': lev_detail, 'weight': weights['leverage']}
    
    # Calculate weighted score
    total_weighted_score = 0
    total_weight = 0
    
    for key, data in signals.items():
        weighted = data['score'] * data['weight']
        total_weighted_score += weighted
        total_weight += data['weight']
    
    # Normalize to -100 to +100 scale
    normalized_score = (total_weighted_score / total_weight) * 10
    
    # Classify sentiment
    if normalized_score < -60:
        classification = "🔴 EXTREMELY BEARISH"
        recommendation = "High risk environment. Consider: 40-50% cash, defensive sectors, hedges, reduce growth exposure."
    elif normalized_score < -20:
        classification = "🔴 BEARISH"
        recommendation = "Caution warranted. Consider: 20-30% cash, increase defensive allocation, selective hedges."
    elif normalized_score < 20:
        classification = "🟡 NEUTRAL"
        recommendation = "Mixed signals. Balanced approach: maintain diversification, selective opportunities."
    elif normalized_score < 60:
        classification = "🟢 BULLISH"
        recommendation = "Positive environment. Consider: full equity exposure, favor growth sectors, maintain stops."
    else:
        classification = "🟢 EXTREMELY BULLISH"
        recommendation = "Strong momentum. Full participation warranted, but watch for overheating signals."
    
    return {
        'score': normalized_score,
        'classification': classification,
        'recommendation': recommendation,
        'signals': signals,
        'timestamp': datetime.now().isoformat()
    }


def register_sentiment_tools(mcp: FastMCP):
    """Register market sentiment tools with the MCP server."""
    
    @mcp.tool()
    def get_market_sentiment() -> str:
        """
        Get current overall market sentiment based on multiple indicators.
        Returns aggregated sentiment score and interpretation.
        """
        try:
            result = aggregate_sentiment_score()
            
            output = "📊 MARKET SENTIMENT ANALYSIS\n"
            output += "="*70 + "\n\n"
            output += f"Overall Sentiment: {result['classification']}\n"
            output += f"Score: {result['score']:.1f}/100\n"
            output += f"Updated: {datetime.fromisoformat(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            output += f"💡 RECOMMENDATION:\n{result['recommendation']}\n\n"
            output += "Use get_detailed_sentiment_signals() for breakdown of all indicators.\n"
            
            # Save to history
            history = load_sentiment_history()
            if 'daily_scores' not in history:
                history['daily_scores'] = []
            
            # Add today's score
            today = datetime.now().date().isoformat()
            history['daily_scores'].append({
                'date': today,
                'score': result['score'],
                'classification': result['classification']
            })
            
            # Keep last 90 days
            if len(history['daily_scores']) > 90:
                history['daily_scores'] = history['daily_scores'][-90:]
            
            save_sentiment_history(history)
            
            return output
        
        except Exception as e:
            return f"Error calculating market sentiment: {e}"
    
    @mcp.tool()
    def get_detailed_sentiment_signals() -> str:
        """
        Get detailed breakdown of all sentiment signals.
        Returns each indicator's value, signal, and contribution to overall score.
        """
        try:
            result = aggregate_sentiment_score()
            
            output = "📊 DETAILED SENTIMENT SIGNAL BREAKDOWN\n"
            output += "="*70 + "\n\n"
            output += f"Overall Score: {result['score']:.1f}/100 - {result['classification']}\n\n"
            output += "Individual Signals:\n"
            output += "-"*70 + "\n\n"
            
            signal_names = {
                'vix': '📈 VIX Level',
                'spy_trend': '📊 SPY Trend',
                'qqq_trend': '📊 QQQ Trend',
                'put_call': '⚖️  Put/Call Proxy',
                'sector_rotation': '🔄 Sector Rotation',
                'breadth': '📏 Market Breadth',
                'volume': '📊 Volume Pattern',
                'ai_tech': '🤖 AI/Tech Signal',
                'leverage': '⚡ Leverage Indicator'
            }
            
            for key, name in signal_names.items():
                if key in result['signals']:
                    s = result['signals'][key]
                    weighted_score = s['score'] * s['weight']
                    output += f"{name}:\n"
                    output += f"   Value: {s['value']}\n"
                    output += f"   Signal: {s['signal']}\n"
                    output += f"   Score: {s['score']:.1f}/10 (Weight: {s['weight']}x) = {weighted_score:.1f}\n\n"
            
            output += "="*70 + "\n"
            output += f"💡 {result['recommendation']}\n"
            
            return output
        
        except Exception as e:
            return f"Error getting detailed signals: {e}"
    
    @mcp.tool()
    def get_vix_analysis() -> str:
        """
        Analyze VIX (volatility index) for fear/greed signals.
        VIX > 20 indicates elevated fear, < 12 indicates complacency.
        """
        try:
            score, signal, value = calculate_vix_signal()
            
            output = "📈 VIX VOLATILITY ANALYSIS\n"
            output += "="*50 + "\n\n"
            output += f"Current VIX: {value:.2f}\n"
            output += f"Signal: {signal}\n"
            output += f"Sentiment Score: {score}/10\n\n"
            output += "Interpretation:\n"
            output += "  • VIX < 12: Very low fear (complacency risk)\n"
            output += "  • VIX 12-20: Normal market conditions\n"
            output += "  • VIX 20-30: Elevated uncertainty\n"
            output += "  • VIX > 30: High fear/panic (potential opportunity)\n"
            
            return output
        
        except Exception as e:
            return f"Error analyzing VIX: {e}"
    
    @mcp.tool()
    def get_market_breadth() -> str:
        """
        Analyze market breadth indicators.
        Measures participation across sectors and indices.
        """
        try:
            score, signal, breadth_pct = calculate_market_breadth_signal()
            
            output = "📏 MARKET BREADTH ANALYSIS\n"
            output += "="*50 + "\n\n"
            output += f"Sectors Positive (1-month): {breadth_pct:.0f}%\n"
            output += f"Signal: {signal}\n"
            output += f"Sentiment Score: {score}/10\n\n"
            output += "Interpretation:\n"
            output += "  • >80%: Excellent participation (healthy rally)\n"
            output += "  • 60-80%: Good breadth\n"
            output += "  • 40-60%: Mixed market\n"
            output += "  • <40%: Narrow market (few leaders, risky)\n"
            
            return output
        
        except Exception as e:
            return f"Error analyzing market breadth: {e}"
    
    @mcp.tool()
    def get_sector_rotation_signal() -> str:
        """
        Detect sector rotation patterns (defensive vs growth).
        Rotation to defensives (XLP, XLU, XLV) indicates risk-off sentiment.
        """
        try:
            score, signal, detail = calculate_sector_rotation_signal()
            
            output = "🔄 SECTOR ROTATION ANALYSIS\n"
            output += "="*50 + "\n\n"
            output += f"Pattern: {detail}\n"
            output += f"Signal: {signal}\n"
            output += f"Sentiment Score: {score}/10\n\n"
            output += "Interpretation:\n"
            output += "  • Growth leading: Risk-on, bullish sentiment\n"
            output += "  • Defensive leading: Risk-off, bearish sentiment\n"
            output += "  • Mixed: Transition period or uncertainty\n"
            
            return output
        
        except Exception as e:
            return f"Error analyzing sector rotation: {e}"
    
    @mcp.tool()
    def get_ai_sector_signal() -> str:
        """
        Specific analysis of AI/tech sector strength.
        Tracks AI-heavy stocks vs broader market.
        """
        try:
            score, signal, detail = calculate_ai_tech_signal()
            
            output = "🤖 AI/TECH SECTOR SIGNAL\n"
            output += "="*50 + "\n\n"
            output += f"Analysis: {detail}\n"
            output += f"Signal: {signal}\n"
            output += f"Sentiment Score: {score}/10\n\n"
            output += "Interpretation:\n"
            output += "  • QQQ outperforming + AI stocks up: Strong tech/AI trend\n"
            output += "  • QQQ underperforming: Tech rotation/weakness\n"
            output += "  • Relevant for AI bubble concerns and tech leadership\n"
            
            return output
        
        except Exception as e:
            return f"Error analyzing AI sector: {e}"
    
    @mcp.tool()
    def track_sentiment_history(days: int = 30) -> str:
        """
        View historical sentiment scores to identify trends.
        Shows if sentiment is improving or deteriorating.
        
        Args:
            days: Number of days of history to show (default: 30).
        """
        try:
            history = load_sentiment_history()
            
            if 'daily_scores' not in history or not history['daily_scores']:
                return "No sentiment history available yet. Run get_market_sentiment() to start tracking."
            
            scores = history['daily_scores'][-days:]
            
            output = f"📈 SENTIMENT HISTORY (Last {len(scores)} days)\n"
            output += "="*70 + "\n\n"
            
            if len(scores) >= 2:
                current = scores[-1]['score']
                previous = scores[0]['score']
                change = current - previous
                
                if change > 10:
                    trend = "📈 IMPROVING (Becoming more bullish)"
                elif change > 3:
                    trend = "📈 Slightly improving"
                elif change > -3:
                    trend = "➡️  STABLE"
                elif change > -10:
                    trend = "📉 Slightly deteriorating"
                else:
                    trend = "📉 DETERIORATING (Becoming more bearish)"
                
                output += f"Trend: {trend}\n"
                output += f"Change: {change:+.1f} points over {len(scores)} days\n\n"
            
            output += "Recent History:\n"
            output += "-"*70 + "\n"
            
            # Show last 10 entries
            for entry in scores[-10:]:
                output += f"{entry['date']}: {entry['score']:6.1f} - {entry['classification']}\n"
            
            return output
        
        except Exception as e:
            return f"Error retrieving sentiment history: {e}"
    
    @mcp.tool()
    def analyze_leverage_indicators() -> str:
        """
        Analyze indicators of leverage in the market.
        Based on volatility patterns and market behavior.
        """
        try:
            score, signal, detail = calculate_leverage_indicator()
            
            output = "⚡ LEVERAGE INDICATOR ANALYSIS\n"
            output += "="*50 + "\n\n"
            output += f"Status: {detail}\n"
            output += f"Signal: {signal}\n"
            output += f"Sentiment Score: {score}/10\n\n"
            output += "Interpretation:\n"
            output += "  • High stress: Potential forced selling/deleveraging\n"
            output += "  • Elevated: Unwinding beginning, caution\n"
            output += "  • Normal: Stable leverage levels\n"
            output += "  • Low: Calm markets, low forced liquidation risk\n\n"
            output += "Note: Based on recent volatility vs historical patterns.\n"
            output += "Sudden spikes suggest leverage unwinding (bearish short-term).\n"
            
            return output
        
        except Exception as e:
            return f"Error analyzing leverage: {e}"

