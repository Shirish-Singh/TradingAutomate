import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import talib

# Download historical data for BTC-USD
btc_data = yf.download('BTC-USD', start='2020-01-01', end='2024-01-05')

# Calculate Simple Moving Averages (SMA) for 20 and 50 periods
btc_data['SMA20'] = talib.SMA(btc_data['Close'], timeperiod=20)
btc_data['SMA50'] = talib.SMA(btc_data['Close'], timeperiod=50)

# Calculate the Relative Strength Index (RSI)
btc_data['RSI'] = talib.RSI(btc_data['Close'], timeperiod=14)

# Calculate Moving Average Convergence Divergence (MACD)
btc_data['MACD'], btc_data['MACD_signal'], _ = talib.MACD(btc_data['Close'],
                                                           fastperiod=12,
                                                           slowperiod=26,
                                                           signalperiod=9)

# Plot the closing price along with the SMAs, RSI, and MACD
plt.figure(figsize=(14, 10))

# Plot Price and SMAs
plt.subplot(311)
plt.title('BTC-USD Price and Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.plot(btc_data['Close'], label='Close Price', color='blue')
plt.plot(btc_data['SMA20'], label='20-period SMA', color='red', linestyle='--')
plt.plot(btc_data['SMA50'], label='50-period SMA', color='green', linestyle='--')
plt.legend()

# Plot RSI
# Placing RSI in the same plot for simplicity, but usually it should be in a separate subplot
plt.subplot(312)
plt.title('Relative Strength Index')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.plot(btc_data['RSI'], label='RSI', color='purple')
plt.axhline(70, color='red', linestyle='--')
plt.axhline(30, color='green', linestyle='--')
plt.legend()

# Plot MACD
plt.subplot(313)
plt.title('Moving Average Convergence Divergence (MACD)')
plt.xlabel('Date')
plt.ylabel('MACD')
plt.plot(btc_data['MACD'], label='MACD', color='black')
plt.plot(btc_data['MACD_signal'], label='Signal Line', color='orange', linestyle='--')
plt.legend()

plt.tight_layout()
plt.show()

# Output the latest part of the data including the indicators
btc_data.tail()
