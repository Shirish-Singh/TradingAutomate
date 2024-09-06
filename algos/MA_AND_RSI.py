import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator


def invokeMARSI(df):
    """
    Invokes the Moving Average and RSI strategy, returning a buy/sell/hold decision.

    Args:
        df (pd.DataFrame): Financial data containing 'Close' prices.

    Returns:
        Tuple: A message with the final decision and None (no image generated).
    """
    try:
        # Calculate Moving Averages
        df['SMA50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
        df['SMA200'] = SMAIndicator(df['Close'], window=200).sma_indicator()

        # Calculate RSI
        df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()

        # Generate Buy/Sell signals based on Moving Average Crossover
        df['Signal'] = np.where((df['SMA50'] > df['SMA200']), 'Buy', 'Sell')

        # Check for RSI Divergence and modify the signals accordingly
        df['RSI_Divergence'] = np.where(
            (df['RSI'] < 30) & (df['Close'] > df['Close'].shift(1)), 'Bullish Divergence',
            np.where((df['RSI'] > 70) & (df['Close'] < df['Close'].shift(1)), 'Bearish Divergence', 'None')
        )

        # Adjust signals based on RSI Divergence
        df['Final_Signal'] = np.where(
            (df['Signal'] == 'Buy') & (df['RSI_Divergence'] == 'Bullish Divergence'), 'Strong Buy',
            np.where((df['Signal'] == 'Sell') & (df['RSI_Divergence'] == 'Bearish Divergence'), 'Strong Sell',
                     df['Signal'])
        )

        # Log insights
        for index, row in df.iterrows():
            print(
                f"Date: {index}, Close: {row['Close']}, SMA50: {row['SMA50']}, SMA200: {row['SMA200']}, RSI: {row['RSI']}, Signal: {row['Final_Signal']}")

        # Determine overall buy/sell decision
        if df['Final_Signal'].iloc[-1] == 'Strong Buy':
            decision = "Buy"
        elif df['Final_Signal'].iloc[-1] == 'Strong Sell':
            decision = "Sell"
        else:
            decision = "Hold"

        print(f"Final Decision based on latest data: {decision}")

        # Return a message and None for image path (since no image is generated)
        return f"Final Decision based on latest data: {decision}", None
    except Exception as e:
        return f"Error during MA and RSI strategy execution: {e}", None

# Example usage:
# df = pd.DataFrame(...)  # Assume df is your DataFrame with historical price data
# result_message, image_path = invokeMARSI(df)
