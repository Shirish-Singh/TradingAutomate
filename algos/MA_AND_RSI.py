import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


def invokeMARSI(df):
    """
    Advanced Moving Average and RSI strategy for high-value trades, with risk management and signal confirmation.

    Args:
        df (pd.DataFrame): Financial data containing 'Close' prices.

    Returns:
        Tuple: A message with the final decision and None (no image generated).
    """
    try:
        # Calculate Moving Averages (50-day and 200-day)
        df['SMA50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
        df['SMA200'] = SMAIndicator(df['Close'], window=200).sma_indicator()

        # Calculate RSI (Relative Strength Index)
        df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()

        # Calculate Bollinger Bands (to assess volatility)
        bb = BollingerBands(df['Close'], window=20, window_dev=2)
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_lower'] = bb.bollinger_lband()

        # Calculate ADX (Average Directional Index) for trend strength
        adx = ADXIndicator(df['High'], df['Low'], df['Close'], window=14)
        df['ADX'] = adx.adx()

        # Generate Buy/Sell signals based on Moving Average Crossover
        df['Signal'] = np.where((df['SMA50'] > df['SMA200']), 'Buy', 'Sell')

        # RSI Divergence Check
        df['RSI_Divergence'] = np.where(
            (df['RSI'] < 30) & (df['Close'] > df['Close'].shift(1)), 'Bullish Divergence',
            np.where((df['RSI'] > 70) & (df['Close'] < df['Close'].shift(1)), 'Bearish Divergence', 'None')
        )

        # Combine RSI, ADX, and Bollinger Bands for stronger signals
        df['Final_Signal'] = np.where(
            (df['Signal'] == 'Buy') & (df['RSI_Divergence'] == 'Bullish Divergence') & (df['ADX'] > 25), 'Strong Buy',
            np.where((df['Signal'] == 'Sell') & (df['RSI_Divergence'] == 'Bearish Divergence') & (df['ADX'] > 25), 'Strong Sell',
                     df['Signal'])
        )

        # Incorporate Bollinger Bands to manage volatility risk (optional filter)
        df['Final_Signal'] = np.where(
            (df['Final_Signal'] == 'Strong Buy') & (df['Close'] < df['BB_lower']), 'Buy with Low Volatility',
            np.where((df['Final_Signal'] == 'Strong Sell') & (df['Close'] > df['BB_upper']), 'Sell with High Volatility',
                     df['Final_Signal'])
        )

        # Log insights (can be removed for performance in production)
        # for index, row in df.iterrows():
        #     print(
        #         f"Date: {index}, Close: {row['Close']}, SMA50: {row['SMA50']}, SMA200: {row['SMA200']}, "
        #         f"RSI: {row['RSI']}, ADX: {row['ADX']}, Signal: {row['Final_Signal']}"
        #     )

        # Final decision: only buy or sell if the ADX confirms strong trend, else hold
        last_signal = df['Final_Signal'].iloc[-1]
        if 'Strong Buy' in last_signal or 'Buy with Low Volatility' in last_signal:
            decision = "Buy"
        elif 'Strong Sell' in last_signal or 'Sell with High Volatility' in last_signal:
            decision = "Sell"
        else:
            decision = "Hold"

        print(f"Final Decision based on latest data: {decision}")

        return f"Final Decision: {decision}", None

    except Exception as e:
        return f"Error during MA and RSI strategy execution: {e}", None
