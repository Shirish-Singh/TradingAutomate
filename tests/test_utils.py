import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os

def generate_test_data(pattern_type="double_bottom", length=100, volatility=0.02):
    """
    Generate synthetic test data for pattern testing.
    
    Args:
        pattern_type (str): Type of pattern to generate data for
        length (int): Length of the data series
        volatility (float): Volatility factor for price movements
        
    Returns:
        pd.DataFrame: DataFrame with OHLC data
    """
    np.random.seed(42)  # For reproducibility
    
    # Base price and date range
    base_price = 100.0
    end_date = datetime.now()
    start_date = end_date - timedelta(days=length)
    date_range = pd.date_range(start=start_date, end=end_date, periods=length)
    
    # Generate random price movements
    price_changes = np.random.normal(0, volatility, length)
    
    # Create base prices
    closes = [base_price]
    for change in price_changes:
        closes.append(closes[-1] * (1 + change))
    closes = closes[1:]  # Remove the initial seed
    
    # Create a dataframe with OHLC data
    df = pd.DataFrame(index=date_range)
    df['Close'] = closes
    
    # Generate Open, High, Low based on Close
    df['Open'] = df['Close'].shift(1)
    df.loc[df.index[0], 'Open'] = df['Close'].iloc[0] * (1 - np.random.uniform(0, volatility))
    
    df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + np.random.uniform(0, volatility, len(df)))
    df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - np.random.uniform(0, volatility, len(df)))
    
    # Modify the data based on the pattern type
    if pattern_type == "double_bottom":
        # Create a double bottom pattern
        bottom1_idx = int(length * 0.3)
        bottom2_idx = int(length * 0.7)
        
        # Create first bottom
        df.iloc[bottom1_idx-3:bottom1_idx+4, df.columns.get_loc('Low')] *= 0.9
        
        # Create second bottom
        df.iloc[bottom2_idx-3:bottom2_idx+4, df.columns.get_loc('Low')] *= 0.9
        
    elif pattern_type == "double_top":
        # Create a double top pattern
        top1_idx = int(length * 0.3)
        top2_idx = int(length * 0.7)
        
        # Create first top
        df.iloc[top1_idx-3:top1_idx+4, df.columns.get_loc('High')] *= 1.1
        
        # Create second top
        df.iloc[top2_idx-3:top2_idx+4, df.columns.get_loc('High')] *= 1.1
        
    elif pattern_type == "head_and_shoulders":
        # Create head and shoulders pattern
        left_shoulder_idx = int(length * 0.25)
        head_idx = int(length * 0.5)
        right_shoulder_idx = int(length * 0.75)
        
        # Create left shoulder
        df.iloc[left_shoulder_idx-3:left_shoulder_idx+4, df.columns.get_loc('High')] *= 1.1
        
        # Create head (higher than shoulders)
        df.iloc[head_idx-3:head_idx+4, df.columns.get_loc('High')] *= 1.15
        
        # Create right shoulder
        df.iloc[right_shoulder_idx-3:right_shoulder_idx+4, df.columns.get_loc('High')] *= 1.1
        
    elif pattern_type == "cup_and_handle":
        # Create cup and handle pattern
        cup_start = int(length * 0.2)
        cup_bottom = int(length * 0.5)
        cup_end = int(length * 0.8)
        handle_end = int(length * 0.9)
        
        # Create cup (U shape)
        for i in range(cup_start, cup_bottom):
            factor = 1 - 0.1 * (i - cup_start) / (cup_bottom - cup_start)
            df.iloc[i, df.columns.get_loc('Low')] *= factor
            df.iloc[i, df.columns.get_loc('Close')] *= factor
        
        for i in range(cup_bottom, cup_end):
            factor = 1 - 0.1 * (cup_end - i) / (cup_end - cup_bottom)
            df.iloc[i, df.columns.get_loc('Low')] *= factor
            df.iloc[i, df.columns.get_loc('Close')] *= factor
        
        # Create handle (small dip)
        for i in range(cup_end, handle_end):
            factor = 1 - 0.05 * (i - cup_end) / (handle_end - cup_end)
            df.iloc[i, df.columns.get_loc('Low')] *= factor
            df.iloc[i, df.columns.get_loc('Close')] *= factor
    
    elif pattern_type == "rising_wedge":
        # Create rising wedge pattern
        for i in range(length):
            # Upper trendline (rising but less steep)
            upper_factor = 1 + 0.1 * (i / length)
            # Lower trendline (rising more steep)
            lower_factor = 1 + 0.15 * (i / length)
            
            df.iloc[i, df.columns.get_loc('High')] *= upper_factor
            df.iloc[i, df.columns.get_loc('Low')] *= lower_factor
    
    elif pattern_type == "falling_wedge":
        # Create falling wedge pattern
        for i in range(length):
            # Upper trendline (falling more steep)
            upper_factor = 1 - 0.15 * (i / length)
            # Lower trendline (falling but less steep)
            lower_factor = 1 - 0.1 * (i / length)
            
            df.iloc[i, df.columns.get_loc('High')] *= upper_factor
            df.iloc[i, df.columns.get_loc('Low')] *= lower_factor
    
    # Ensure data integrity
    df['Volume'] = np.random.randint(1000, 100000, size=len(df))
    df = df.fillna(method='ffill')
    
    return df

def fetch_test_data(ticker="AAPL", period="1y", interval="1d"):
    """
    Fetch real market data for testing.
    
    Args:
        ticker (str): Ticker symbol
        period (str): Period to fetch (e.g., '1y', '6mo')
        interval (str): Data interval (e.g., '1d', '1h')
        
    Returns:
        pd.DataFrame: DataFrame with OHLC data
    """
    try:
        data = yf.download(ticker, period=period, interval=interval)
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        # Return synthetic data as fallback
        return generate_test_data()

def run_pattern_test(pattern_function, data=None, pattern_type="double_bottom", save_dir=None):
    """
    Test a pattern detection function with either real or synthetic data.
    
    Args:
        pattern_function: The pattern detection function to test
        data (pd.DataFrame, optional): Data to use for testing, if None will generate synthetic data
        pattern_type (str): Type of pattern for synthetic data generation
        save_dir (str, optional): Directory to save test results
        
    Returns:
        tuple: Result message and image path from the pattern function
    """
    if data is None:
        data = generate_test_data(pattern_type=pattern_type)
    
    # Create save directory if specified
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    # Run the pattern detection function
    try:
        result = pattern_function(data)
        return result
    except Exception as e:
        print(f"Error testing {pattern_type}: {e}")
        return f"Error during {pattern_type} test: {e}", None

def align_dataframes_before_operation(left, right):
    """
    Align two dataframes or series before performing operations between them.
    
    Args:
        left: Left DataFrame or Series
        right: Right DataFrame or Series
        
    Returns:
        tuple: Aligned left and right objects
    """
    if isinstance(left, pd.DataFrame) and isinstance(right, pd.DataFrame):
        return left.align(right, axis=1, copy=False)
    elif isinstance(left, pd.Series) and isinstance(right, pd.Series):
        return left.align(right, copy=False)
    elif isinstance(left, pd.DataFrame) and isinstance(right, pd.Series):
        # Align Series with DataFrame
        right = right.reindex(left.index)
        return left, right
    elif isinstance(left, pd.Series) and isinstance(right, pd.DataFrame):
        # Align Series with DataFrame
        left = left.reindex(right.index)
        return left, right
    else:
        # Return as is if not DataFrames or Series
        return left, right

def plot_test_results(test_results, save_path=None):
    """
    Plot test results for all patterns.
    
    Args:
        test_results (dict): Dictionary of test results
        save_path (str, optional): Path to save the plot
    """
    fig, axes = plt.subplots(len(test_results), 1, figsize=(12, 4 * len(test_results)))
    
    if len(test_results) == 1:
        axes = [axes]
    
    for i, (pattern_name, (message, image_path)) in enumerate(test_results.items()):
        axes[i].set_title(f"{pattern_name}: {'Success' if 'detected' in message and 'Error' not in message else 'Failed'}")
        axes[i].text(0.1, 0.5, message[:100] + "..." if len(message) > 100 else message, 
                    transform=axes[i].transAxes)
        axes[i].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()
