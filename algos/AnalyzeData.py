import numpy as np
import talib

def analyze_data(data):
    """
    Analyzes the financial data by calculating indicators (SMA, RSI, MACD) and generating a buy/sell/hold signal.

    Args:
        data (pd.DataFrame): DataFrame containing 'Close' prices.

    Returns:
        Tuple: A string signal ('Buy', 'Sell', 'Hold'), a confidence level (float), and an explanation (string).
    """
    try:
        # Calculate indicators (SMA, RSI, MACD)
        data['SMA20'] = talib.SMA(data['Close'], timeperiod=20)
        data['SMA50'] = talib.SMA(data['Close'], timeperiod=50)
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
        data['MACD'], data['MACD_signal'], _ = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

        # Get the latest indicator values
        last_sma20 = data['SMA20'].iloc[-1]
        last_sma50 = data['SMA50'].iloc[-1]
        last_close = data['Close'].iloc[-1]
        last_rsi = data['RSI'].iloc[-1]
        last_macd = data['MACD'].iloc[-1]
        last_macdsignal = data['MACD_signal'].iloc[-1]

        # Initialize signal counters
        buy_signals = 0
        sell_signals = 0

        # Check SMA for buy or sell signals
        if np.isnan(last_sma20) or np.isnan(last_sma50):
            sma_signal = 'Unknown'
        elif last_close > last_sma20 > last_sma50:
            buy_signals += 1
            sma_signal = 'Bullish'
        elif last_close < last_sma20 < last_sma50:
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
