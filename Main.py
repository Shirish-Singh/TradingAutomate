import yfinance as yf
from datetime import datetime
from TradingPDF import TradingReportPDF  # Import the PDF report class
from algos.AnalyzeData import analyze_data
from algos.fibonacci_calculator import FibonacciCalculator
from algos import MA_AND_RSI as ma, RisingWedge as rw, DoubleTop as dt, HeadAndShoulder as hands, DoubleBottom as db, FallingWedge as fw
from algos import CupAndHandle as ch, AscendingTriangle as at
import logging
import os
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_mock_data(ticker, start_date, end_date, interval):
    """
    Generate mock data for testing when the API fails.
    
    :param ticker: The ticker symbol
    :param start_date: Start date in 'YYYY-MM-DD' format
    :param end_date: End date in 'YYYY-MM-DD' format
    :param interval: Data interval
    :return: A DataFrame with mock stock data
    """
    import pandas as pd
    import numpy as np
    from pandas.tseries.offsets import Day, Hour, Minute
    
    # Parse dates
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # Determine frequency based on interval
    if interval == '1d':
        freq = Day()
        periods = (end - start).days + 1
    elif interval == '1h':
        freq = Hour()
        periods = (end - start).days * 24
    elif interval == '15m':
        freq = Minute(15)
        periods = (end - start).days * 24 * 4
    else:
        freq = Day()
        periods = (end - start).days + 1
    
    # Generate date range
    date_range = pd.date_range(start=start, periods=periods, freq=freq)
    
    # Set a base price based on ticker (just for variety)
    base_price = hash(ticker) % 1000 + 100  # Between 100 and 1099
    
    # Generate price data with some randomness but following a trend
    np.random.seed(42)  # For reproducibility
    price_changes = np.random.normal(0, 1, len(date_range)).cumsum() * 0.01
    prices = base_price * (1 + price_changes)
    
    # Generate volume data
    volumes = np.random.randint(1000000, 10000000, len(date_range))
    
    # Create DataFrame
    data = pd.DataFrame({
        'Open': prices * (1 - np.random.random(len(date_range)) * 0.01),
        'High': prices * (1 + np.random.random(len(date_range)) * 0.01),
        'Low': prices * (1 - np.random.random(len(date_range)) * 0.015),
        'Close': prices,
        'Adj Close': prices,
        'Volume': volumes
    }, index=date_range)
    
    return data

def fetch_data(ticker, start_date, end_date, interval):
    """
    Fetches historical data for a given ticker symbol from Yahoo Finance.
    Falls back to mock data if the API fails.

    :param ticker: The ticker symbol to fetch the data for (e.g., 'AAPL').
    :param start_date: The start date for the data in 'YYYY-MM-DD' format.
    :param end_date: The end date for the data in 'YYYY-MM-DD' format.
    :param interval: The interval for the data (e.g., '1m', '15m', '1h', '1d', '1mo').
    :return: A DataFrame containing the historical data for the specified ticker and interval.
    """
    try:
        # Try common stock tickers first
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        if data.empty:
            # If the original ticker fails, try some variations
            alternate_tickers = [f"{ticker}-USD", f"{ticker}.US"]
            for alt_ticker in alternate_tickers:
                logging.info(f"Trying alternate ticker: {alt_ticker}")
                data = yf.download(alt_ticker, start=start_date, end=end_date, interval=interval)
                if not data.empty:
                    logging.info(f"Successfully fetched data using alternate ticker: {alt_ticker}")
                    return data
            
            logging.warning("No data found via API. Using mock data for testing purposes.")
            return generate_mock_data(ticker, start_date, end_date, interval)
        return data
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        logging.warning("Using mock data for testing purposes due to API error.")
        return generate_mock_data(ticker, start_date, end_date, interval)


def process_pattern(pdf, pattern_name, pattern_function, data):
    """
    Process a trading pattern by invoking its detection and adding the result to the PDF.

    :param pdf: TradingReportPDF object.
    :param pattern_name: The name of the pattern (e.g., "Cup and Handle").
    :param pattern_function: The function that detects the pattern.
    :param data: The financial data DataFrame.
    """
    # Add header for the pattern
    pdf.add_title(pattern_name, level=2)

    # Run the pattern detection
    try:
        result_message, image_path = pattern_function(data)
        pdf.add_paragraph(result_message)
        if image_path:
            pdf.add_image(image_path)
    except Exception as e:
        logging.error(f"Error processing {pattern_name}: {e}")
        pdf.add_paragraph(f"Error processing {pattern_name}: {e}")

    # Add a line separator after each pattern result
    pdf.add_line()


def main(ticker='BTC-USD', start_date='2023-10-01', end_date=None, interval='1d'):
    print("Trading Tool V1.1")
    
    # Set default end date if not provided
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
        
    print(f"Using ticker: {ticker}, start date: {start_date}, end date: {end_date}, interval: {interval}")

    # Fetch data based on user input
    data = fetch_data(ticker, start_date, end_date, interval)
    
    if data is None or data.empty:
        logging.error("No data available for analysis. Aborting.")
        return

    # Create the PDF object
    pdf = TradingReportPDF()

    # Add a page to the PDF
    pdf.add_page()

    # Add a title and a paragraph to the report
    pdf.add_title("Introduction")
    pdf.add_paragraph("This report contains the results of various trading algorithms applied to market data.")

    # Add user input summary to the PDF
    pdf.add_title("User Inputs")

    pdf.add_paragraph(f"Ticker Symbol: {ticker}\n"
                      f"Start Date: {start_date}\n"
                      f"End Date: {end_date}\n"
                      f"Interval: {interval}\n"
                      f"Duration: { calculate_duration(start_date, end_date)}\n")
    # Process different trading patterns
    patterns = [
        ("Moving Average and RSI Strategy", ma.invokeMARSI),
        ("Double Bottom", db.invokeDoubleBottom),
        ("Head and Shoulders", hands.invokeHeadAndShoulders),
        ("Double Top", dt.invokeDoubleTop),
        ("Rising Wedge", rw.invokeRisingWedge),
        ("Falling Wedge", fw.invokeFallingWedge),
        ("Cup and Handle", ch.invokeCupAndHandle),
        ("Ascending Triangle", at.invokeAscendingTriangle)
    ]

    for pattern_name, pattern_function in patterns:
        logging.info(f"Processing pattern: {pattern_name}")
        try:
            process_pattern(pdf, pattern_name, pattern_function, data)
        except Exception as e:
            logging.error(f"Error processing {pattern_name}: {e}")
            pdf.add_paragraph(f"Error processing {pattern_name}: {e}")

    # Finalize the report
    report_name = f"Trading_Report_{ticker}_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf.finalize_report(report_name)
    logging.info(f"Trading report saved as {report_name}")

    # Delete all .png files after PDF generation
    delete_generated_images()

def delete_generated_images():
    """
    Deletes all .png files generated during the process.
    """
    png_files = glob.glob("*.png")  # Find all .png files in the current directory
    for file in png_files:
        try:
            os.remove(file)
            logging.info(f"Deleted image file: {file}")
        except Exception as e:
            logging.error(f"Error deleting file {file}: {e}")


def calculate_duration(start_date, end_date):
    """
    Calculates the duration between the start and end dates in a human-readable format (days, months, or years).
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    delta = end - start
    days = delta.days

    # Determine the duration in days, months, or years
    if days < 30:
        return f"{days} days"
    elif days < 365:
        months = days // 30
        return f"{months} months"
    else:
        years = days // 365
        return f"{years} years"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Tool for technical analysis')
    parser.add_argument('--ticker', type=str, default='BTC', help='Ticker symbol (e.g., AAPL, MSFT, GOOG)')
    parser.add_argument('--start_date', type=str, default='2025-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', type=str, default=None, help='End date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--interval', type=str, default='1d', help='Data interval (e.g., 1d, 1wk, 15min)')
    
    args = parser.parse_args()
    
    main(ticker=args.ticker, start_date=args.start_date, end_date=args.end_date, interval=args.interval)
