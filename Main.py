from AnalyzeData import analyze_data
import yfinance as yf
from datetime import datetime

import CupAndHandle as cAndH
import DoubleBottom as doubleBottom
import AscendingPattern as ap

import HeadAndShoulder as hands
import DoubleTop as dt
import RisingWedge as rw
def fetch_data(ticker, start_date, end_date, interval):
    """
    Fetches historical data for a given ticker symbol from Yahoo Finance.

    :param ticker: The ticker symbol to fetch the data for (e.g., 'BTC-USD').
    :param start_date: The start date for the data in 'YYYY-MM-DD' format.
    :param end_date: The end date for the data in 'YYYY-MM-DD' format.
    :param interval: The interval for the data (e.g., '1m', '15m', '1h', '1d', '1mo').
    :return: A DataFrame containing the historical data for the specified ticker and interval.
    """
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    return data

# Example usage:
# btc_data_15m = fetch_data('BTC-USD', '2023-12-01', '2024-01-01', '15m') DONT USE THIS WITHOUT MA ETC CONFIGURATION
# btc_data_1h = fetch_data('BTC-USD', '2023-12-01', '2024-01-01', '1h') DONT USE THIS WITHOUT MA ETC CONFIGURATION
# btc_data_1d = fetch_data('BTC-USD', '2020-01-01', '2024-01-01', '1d')
# btc_data_1mo = fetch_data('BTC-USD', '2019-01-01', '2024-01-01', '1mo')

# Note: The '1m' interval data is usually available for the past 7 days. For intervals like '15m' and '1h',
# you might need to adjust the start_date closer to the end_date due to data availability.



print("Welcome To Trading Predictions..")

# Ask the user for the ticker symbol
ticker = input("Enter the ticker symbol (e.g., BTC-USD, press Enter for default 'BTC-USD'): ")
if not ticker:
    ticker = 'BTC-USD'

# Ask the user for the start date
start_date = input("Enter the start date (YYYY-MM-DD, press Enter for default '2023-10-01'): ")
if not start_date:
    start_date = '2023-10-01'

# Ask the user for the end date
end_date = input("Enter the end date (YYYY-MM-DD, press Enter for default today's date): ")
if not end_date:
    end_date = datetime.now().strftime('%Y-%m-%d')

# Ask the user for the interval
interval = input("Enter the interval (e.g., 1d, 1wk, 15min, press Enter for default '1d'): ")
if not interval:
    interval = '1d'
# Fetch data based on user input
data = fetch_data(ticker, start_date, end_date, interval)

result = analyze_data(data)

#Bullish
cAndH.invokeCandH(data)
doubleBottom.invokeDoubleBottom(data)
ap.invokeAscendingTriangle(data)

#Bearish
hands.invokeHeadAndShoulders(data)
dt.invokeDoubleTop(data)
rw.invokeRisingWedge(data)
print(result)