import yfinance as yf
import mplfinance as mpf

from AnalysisConfig import AnalysisConfig
from algos.HeadAndShoulder import detect_head_and_shoulders


def technicalAnalysis(config):
    # Download data
    data = yf.download(config.ticker, period=config.period, interval=config.interval)
    # Display the first few rows of the dataframe
    print(data.head())
    # Basic statistics
    print(data.describe())
    # Plotting
    mpf.plot(data, type='ohlc', mav=config.mav, volume=config.volume, style=config.style, savefig='plot.png')
    pattern_detected = detect_head_and_shoulders(data)
    if pattern_detected:
        print("Potential Head and Shoulders pattern detected.")
    else:
        print("No Head and Shoulders pattern detected.")

# Create a configuration object
config = AnalysisConfig(
    ticker='BTC-USD',
    period='1mo',  # Last month
    interval='1d',  # Daily data
    mav=(10, 20),
    volume=True
)

technicalAnalysis(config)

# Perform technical analysis
technicalAnalysis(config)
