import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from ta.trend import SMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

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

def calculate_indicators(df):
    """
    Calculate technical indicators for the MA and RSI strategy.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        
    Returns:
        pd.DataFrame: DataFrame with added indicators.
    """
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Check if we have enough data
    if len(df_copy) < 200:  # Need at least 200 data points for SMA200
        raise ValueError("Insufficient data for calculating indicators. Need at least 200 data points.")
    
    # Calculate SMA50, SMA200
    df_copy['SMA50'] = SMAIndicator(df_copy['Close'], window=50).sma_indicator()
    df_copy['SMA200'] = SMAIndicator(df_copy['Close'], window=200).sma_indicator()
    
    # Calculate RSI
    df_copy['RSI'] = RSIIndicator(df_copy['Close'], window=14).rsi()
    
    # Calculate Bollinger Bands
    bollinger = BollingerBands(df_copy['Close'], window=20, window_dev=2)
    df_copy['BB_upper'] = bollinger.bollinger_hband()
    df_copy['BB_middle'] = bollinger.bollinger_mavg()
    df_copy['BB_lower'] = bollinger.bollinger_lband()
    
    # Calculate ADX
    adx_indicator = ADXIndicator(df_copy['High'], df_copy['Low'], df_copy['Close'], window=14)
    df_copy['ADX'] = adx_indicator.adx()
    
    # Replace NaN values with 0 to avoid issues
    df_copy = df_copy.fillna(0)
    
    return df_copy


def plot_ma_rsi_strategy(df, image_path='ma_rsi_strategy.png'):
    """
    Plot the MA and RSI strategy with buy/sell signals.
    
    Args:
        df (pd.DataFrame): DataFrame with signals.
        image_path (str): Path to save the plot image.
        
    Returns:
        str: Path to the saved image.
    """
    plt.figure(figsize=(14, 10))
    
    # Plot price and moving averages
    plt.subplot(3, 1, 1)
    plt.plot(df.index, df['Close'], label='Close Price', linewidth=1.5)
    plt.plot(df.index, df['SMA50'], label='SMA50', linewidth=1)
    plt.plot(df.index, df['SMA200'], label='SMA200', linewidth=1)
    plt.plot(df.index, df['BB_upper'], 'r--', label='BB Upper', linewidth=0.8)
    plt.plot(df.index, df['BB_middle'], 'b--', label='BB Middle', linewidth=0.8)
    plt.plot(df.index, df['BB_lower'], 'g--', label='BB Lower', linewidth=0.8)
    
    # Plot buy/sell signals
    buy_signals = df[df['Final_Signal'] == 'Buy']
    sell_signals = df[df['Final_Signal'] == 'Sell']
    
    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', s=100, label='Buy Signal')
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', s=100, label='Sell Signal')
    
    plt.title('MA and RSI Strategy with Bollinger Bands', fontsize=14)
    plt.ylabel('Price', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Plot RSI
    plt.subplot(3, 1, 2)
    plt.plot(df.index, df['RSI'], label='RSI', color='purple', linewidth=1.5)
    plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
    plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
    plt.fill_between(df.index, 30, 70, color='gray', alpha=0.1)
    
    # Highlight RSI signals
    rsi_buy = df[df['RSI_Signal'] == 1]
    rsi_sell = df[df['RSI_Signal'] == -1]
    plt.scatter(rsi_buy.index, rsi_buy['RSI'], marker='^', color='g', s=50, label='RSI Buy')
    plt.scatter(rsi_sell.index, rsi_sell['RSI'], marker='v', color='r', s=50, label='RSI Sell')
    
    plt.title('Relative Strength Index (RSI)', fontsize=14)
    plt.ylabel('RSI', fontsize=12)
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Plot ADX
    plt.subplot(3, 1, 3)
    plt.plot(df.index, df['ADX'], label='ADX', color='blue', linewidth=1.5)
    plt.axhline(y=25, color='r', linestyle='--', label='Strong Trend (25)')
    plt.fill_between(df.index, 0, 25, color='gray', alpha=0.1)
    
    # Highlight ADX signals
    adx_strong = df[df['ADX_Signal'] == 1]
    plt.scatter(adx_strong.index, adx_strong['ADX'], marker='o', color='orange', s=30, label='Strong Trend')
    
    plt.title('Average Directional Index (ADX)', fontsize=14)
    plt.ylabel('ADX', fontsize=12)
    plt.ylim(0, max(100, df['ADX'].max() * 1.1))
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(image_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return image_path


def generate_signals(df):
    """
    Generate trading signals based on the calculated indicators.
    
    Args:
        df (pd.DataFrame): DataFrame with indicators.
        
    Returns:
        pd.DataFrame: DataFrame with added signals.
    """
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Initialize signal columns
    df_copy['MA_Signal'] = 0  # 1 for bullish, -1 for bearish
    df_copy['RSI_Signal'] = 0  # 1 for bullish, -1 for bearish
    df_copy['BB_Signal'] = 0  # 1 for bullish, -1 for bearish
    df_copy['ADX_Signal'] = 0  # 1 for strong trend
    df_copy['Final_Signal'] = 'Hold'  # 'Buy', 'Sell', or 'Hold'
    
    # Generate MA signals - more sophisticated with SMA50 and SMA200 crossover
    # Use explicit boolean comparisons to avoid ambiguous truth value errors
    ma_bullish_mask = (df_copy['Close'] > df_copy['SMA50']) & (df_copy['SMA50'] > df_copy['SMA200'])
    ma_bearish_mask = (df_copy['Close'] < df_copy['SMA50']) & (df_copy['SMA50'] < df_copy['SMA200'])
    
    # Apply signals using masks
    df_copy.loc[ma_bullish_mask, 'MA_Signal'] = 1  # Strong bullish
    df_copy.loc[ma_bearish_mask, 'MA_Signal'] = -1  # Strong bearish
    
    # Generate RSI signals with more nuanced ranges
    df_copy.loc[df_copy['RSI'] < 30, 'RSI_Signal'] = 1  # Oversold
    df_copy.loc[df_copy['RSI'] > 70, 'RSI_Signal'] = -1  # Overbought
    
    # RSI crossing up from oversold
    rsi_cross_up_mask = (df_copy['RSI'] >= 30) & (df_copy['RSI'] <= 40) & (df_copy['RSI'].shift(1) < 30)
    df_copy.loc[rsi_cross_up_mask, 'RSI_Signal'] = 1
    
    # RSI crossing down from overbought
    rsi_cross_down_mask = (df_copy['RSI'] <= 70) & (df_copy['RSI'] >= 60) & (df_copy['RSI'].shift(1) > 70)
    df_copy.loc[rsi_cross_down_mask, 'RSI_Signal'] = -1
    
    # Generate Bollinger Bands signals with confirmation
    # Price crossing below lower band
    bb_lower_cross_mask = (df_copy['Close'] < df_copy['BB_lower']) & (df_copy['Close'].shift(1) >= df_copy['BB_lower'].shift(1))
    df_copy.loc[bb_lower_cross_mask, 'BB_Signal'] = 1
    
    # Price crossing above upper band
    bb_upper_cross_mask = (df_copy['Close'] > df_copy['BB_upper']) & (df_copy['Close'].shift(1) <= df_copy['BB_upper'].shift(1))
    df_copy.loc[bb_upper_cross_mask, 'BB_Signal'] = -1
    
    # Price bouncing up from lower band
    bb_bounce_up_mask = (df_copy['Close'] > df_copy['BB_lower']) & (df_copy['Close'].shift(1) <= df_copy['BB_lower'].shift(1))
    df_copy.loc[bb_bounce_up_mask, 'BB_Signal'] = 1
    
    # Price bouncing down from upper band
    bb_bounce_down_mask = (df_copy['Close'] < df_copy['BB_upper']) & (df_copy['Close'].shift(1) >= df_copy['BB_upper'].shift(1))
    df_copy.loc[bb_bounce_down_mask, 'BB_Signal'] = -1
    
    # Generate ADX signals (ADX > 25 indicates a strong trend)
    df_copy.loc[df_copy['ADX'] > 25, 'ADX_Signal'] = 1
    
    # Generate final signals with more sophisticated logic
    for i in range(len(df_copy)):
        # Skip if we don't have enough data for signals
        if i < 5:
            continue
            
        # Buy signals - multiple conditions for stronger confirmation
        ma_signal = int(df_copy['MA_Signal'].iloc[i])
        rsi_signal = int(df_copy['RSI_Signal'].iloc[i])
        bb_signal = int(df_copy['BB_Signal'].iloc[i])
        adx_signal = int(df_copy['ADX_Signal'].iloc[i])
        
        if (ma_signal == 1 and (rsi_signal == 1 or bb_signal == 1) and adx_signal == 1):
            df_copy.loc[df_copy.index[i], 'Final_Signal'] = 'Buy'
            
        # Sell signals - multiple conditions for stronger confirmation
        elif (ma_signal == -1 and (rsi_signal == -1 or bb_signal == -1) and adx_signal == 1):
            df_copy.loc[df_copy.index[i], 'Final_Signal'] = 'Sell'
    
    return df_copy


def invokeMARSI(df):
    """
    Advanced Moving Average and RSI strategy for high-value trades, with risk management and signal confirmation.

    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        
    Returns:
        Tuple: A message with the final decision and an image path showing the analysis.
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 200:
            return "Insufficient data for MA_AND_RSI analysis. Need at least 200 data points.", None
        
        # Calculate technical indicators
        df_copy = calculate_indicators(df_copy)
        
        # Generate trading signals
        df_copy = generate_signals(df_copy)
        
        # Create visualization
        image_path = plot_ma_rsi_strategy(df_copy)
        
        # Get the final signal
        last_signal = str(df_copy['Final_Signal'].iloc[-1])
        
        # Prepare detailed analysis message
        last_close = safe_float(df_copy['Close'].iloc[-1])
        last_sma50 = safe_float(df_copy['SMA50'].iloc[-1])
        last_sma200 = safe_float(df_copy['SMA200'].iloc[-1])
        last_rsi = safe_float(df_copy['RSI'].iloc[-1])
        last_adx = safe_float(df_copy['ADX'].iloc[-1])
        
        # Determine RSI condition using explicit comparisons
        if last_rsi > 70:
            rsi_condition = "Overbought"
        elif last_rsi < 30:
            rsi_condition = "Oversold"
        else:
            rsi_condition = "Neutral"
            
        # Determine ADX condition using explicit comparison
        adx_condition = "Strong Trend" if last_adx > 25 else "Weak Trend"
        
        analysis_message = f"MA_AND_RSI Analysis:\n"
        analysis_message += f"Current Price: {last_close:.2f}\n"
        analysis_message += f"SMA50: {last_sma50:.2f}, SMA200: {last_sma200:.2f}\n"
        analysis_message += f"RSI: {last_rsi:.2f} ({rsi_condition})\n"
        analysis_message += f"ADX: {last_adx:.2f} ({adx_condition})\n"
        
        if last_signal == 'Buy':
            return f"BUY Signal: {analysis_message}", image_path
        elif last_signal == 'Sell':
            return f"SELL Signal: {analysis_message}", image_path
        else:
            return f"HOLD: No clear signal. {analysis_message}", image_path

    except Exception as e:
        return f"Error in MA_AND_RSI strategy: {e}", None
