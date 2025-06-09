import numpy as np
import pandas as pd
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from ta.trend import MACD

def safe_float(value):
    """
    Safely convert a value to float, handling pandas Series objects.
    
    Args:
        value: Value to convert to float, could be a pandas Series, DataFrame, or scalar
        
    Returns:
        float: The converted float value
    """
    if isinstance(value, pd.Series):
        if len(value) == 0:
            return 0.0
        return safe_float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        if value.empty:
            return 0.0
        return safe_float(value.iloc[0, 0])
    return float(value)


def ensure_aligned(left, right):
    """
    Ensure two pandas Series or DataFrames are aligned before operations.
    
    Args:
        left: First pandas Series or DataFrame
        right: Second pandas Series or DataFrame
        
    Returns:
        tuple: (aligned_left, aligned_right)
    """
    if hasattr(left, 'align') and hasattr(right, 'align'):
        return left.align(right, axis=0, copy=False)
    return left, right

def analyze_data(data):
    """
    Analyzes the financial data by calculating indicators (SMA, RSI, MACD) and generating a buy/sell/hold signal.

    Args:
        data (pd.DataFrame): DataFrame containing 'Close' prices.

    Returns:
        Tuple: A string signal ('Buy', 'Sell', 'Hold'), a confidence level (float), and an explanation (string).
    """
    try:
        # Make a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Check if we have enough data
        if len(df) < 50:  # Need at least 50 data points for reliable indicators
            return "Insufficient data", 0, "Not enough historical data to perform reliable analysis."
        
        # Calculate indicators (SMA, RSI, MACD)
        df['SMA20'] = SMAIndicator(df['Close'], window=20).sma_indicator()
        df['SMA50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
        df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
        
        # Calculate MACD
        macd = MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()

        # Drop NaN values that might cause issues
        df = df.dropna()
        
        # If after dropping NaNs we don't have enough data, return early
        if len(df) < 5:
            return "Insufficient data after processing", 0, "Not enough valid data points after calculating indicators."

        # Get the latest indicator values
        last_sma20 = safe_float(df['SMA20'].iloc[-1])
        last_sma50 = safe_float(df['SMA50'].iloc[-1])
        last_close = safe_float(df['Close'].iloc[-1])
        last_rsi = safe_float(df['RSI'].iloc[-1])
        last_macd = safe_float(df['MACD'].iloc[-1])
        last_macdsignal = safe_float(df['MACD_signal'].iloc[-1])

        # Initialize signal counters
        buy_signals = 0
        sell_signals = 0

        # Check SMA for buy or sell signals
        if np.isnan(last_sma20) or np.isnan(last_sma50):
            sma_signal = 'Unknown'
        elif last_close > last_sma20 and last_sma20 > last_sma50:
            buy_signals += 1
            sma_signal = 'Bullish'
        elif last_close < last_sma20 and last_sma20 < last_sma50:
            sell_signals += 1
            sma_signal = 'Bearish'
        else:
            sma_signal = 'Neutral'

        # Check RSI for buy or sell signals
        if last_rsi > 70:
            sell_signals += 1
            rsi_signal = 'Overbought'
        elif last_rsi < 30:
            buy_signals += 1
            rsi_signal = 'Oversold'
        else:
            rsi_signal = 'Neutral'

        # Check MACD for buy or sell signals
        if last_macd > last_macdsignal:
            buy_signals += 1
            macd_signal = 'Above Signal'
        elif last_macd < last_macdsignal:
            sell_signals += 1
            macd_signal = 'Below Signal'
        else:
            macd_signal = 'Neutral'

        # Determine overall signal
        if buy_signals > sell_signals:
            signal = 'Buy'
        elif sell_signals > buy_signals:
            signal = 'Sell'
        else:
            signal = 'Hold'

        # Determine confidence level
        confidence = (abs(buy_signals - sell_signals) / 3) * 100  # 3 is the number of indicators

        # Provide explanation
        explanation = (f"SMA Trend: {sma_signal}, RSI Level: {rsi_signal}, "
                       f"MACD Status: {macd_signal}. Overall signal is {signal} "
                       f"with {confidence:.2f}% confidence based on the indicators.")

        return signal, confidence, explanation
    except Exception as e:
        return f"Error in data analysis: {e}", 0, "No explanation available due to error."
