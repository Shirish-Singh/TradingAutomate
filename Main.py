import yfinance as yf
from datetime import datetime
from TradingPDF import TradingReportPDF  # Import the PDF report class
from algos.AnalyzeData import analyze_data
from algos import MA_AND_RSI as ma, RisingWedge as rw, CupAndHandle as cAndH, DoubleTop as dt, HeadAndShoulder as hands, \
    AscendingPattern as ap, DoubleBottom as db
import logging
import os
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_data(ticker, start_date, end_date, interval):
    """
    Fetches historical data for a given ticker symbol from Yahoo Finance.

    :param ticker: The ticker symbol to fetch the data for (e.g., 'BTC-USD').
    :param start_date: The start date for the data in 'YYYY-MM-DD' format.
    :param end_date: The end date for the data in 'YYYY-MM-DD' format.
    :param interval: The interval for the data (e.g., '1m', '15m', '1h', '1d', '1mo').
    :return: A DataFrame containing the historical data for the specified ticker and interval.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        if data.empty:
            logging.error("No data found for the given ticker and date range.")
            raise ValueError("No data found for the given ticker and date range.")
        return data
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        raise


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


def main():
    print("Trading Tool V1.1")

    # Ask the user for the ticker symbol
    ticker = input("Enter the ticker symbol (e.g., BTC-USD, press Enter for default 'BTC-USD'): ") or 'BTC-USD'

    # Ask the user for the start date
    start_date = input("Enter the start date (YYYY-MM-DD, press Enter for default '2023-10-01'): ") or '2023-10-01'

    # Ask the user for the end date
    end_date = input("Enter the end date (YYYY-MM-DD, press Enter for default today's date): ") or datetime.now().strftime('%Y-%m-%d')

    # Ask the user for the interval
    interval = input("Enter the interval (e.g., 1d, 1wk, 15min, press Enter for default '1d'): ") or '1d'

    # Fetch data based on user input
    try:
        data = fetch_data(ticker, start_date, end_date, interval)
    except ValueError as e:
        logging.error("Aborting due to data fetch error.")
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

    # Perform general data analysis
    signal, confidence, explanation = analyze_data(data)

    # Add analysis results to the PDF (splitting out each result)
    pdf.add_title("Data Analysis Results - DYOR")
    # Combine signal, confidence, and explanation into a single paragraph
    pdf.add_paragraph(f"Signal: {signal}\n"
                      f"Confidence Level: {confidence:.2f}%\n"
                      f"Explanation: {explanation}")
    # Process different trading patterns
    patterns = [
        ("Moving Average and RSI Strategy", ma.invokeMARSI),
        ("Cup and Handle", cAndH.invokeCandH),
        ("Double Bottom", db.invokeDoubleBottom),
        ("Ascending Triangle", ap.invokeAscendingTriangle),
        ("Head and Shoulders", hands.invokeHeadAndShoulders),
        ("Double Top", dt.invokeDoubleTop),
        ("Rising Wedge", rw.invokeRisingWedge)
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
    main()
