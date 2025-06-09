import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

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
        return float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        if value.empty:
            return 0.0
        return float(value.iloc[0, 0])
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

def detect_double_top(df, min_distance=10, max_price_diff_pct=0.03):
    """
    Detects Double Top pattern in the given financial data.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        min_distance (int): Minimum number of periods between tops.
        max_price_diff_pct (float): Maximum percentage difference between the two tops.
        
    Returns:
        tuple: (first_top_idx, second_top_idx, breakdown_idx) or (None, None, None) if not found.
    """
    # Need at least 20 periods for a proper double top
    if len(df) < 20:
        return None, None, None
    
    # Create a copy to avoid modifying the original dataframe
    df_copy = df.copy()
    
    # Find local maxima (peaks) using rolling window
    window = 5
    df_copy['is_peak'] = False
    
    # A point is a peak if it's the highest in a window of size 'window'
    for i in range(window, len(df_copy) - window):
        current_high = safe_float(df_copy['High'].iloc[i])
        window_max = safe_float(df_copy['High'].iloc[i-window:i+window+1].max())
        if current_high == window_max:
            df_copy.loc[df_copy.index[i], 'is_peak'] = True
    
    # Get all peaks using boolean indexing
    peak_mask = df_copy['is_peak'] == True
    peaks = df_copy[peak_mask]
    
    if len(peaks) < 2:
        return None, None, None
    
    # Check all pairs of peaks for double top pattern
    for i in range(len(peaks) - 1):
        for j in range(i + 1, len(peaks)):
            first_peak_idx = peaks.index[i]
            second_peak_idx = peaks.index[j]
            
            # Check if peaks are far enough apart
            peak_distance = df_copy.index.get_loc(second_peak_idx) - df_copy.index.get_loc(first_peak_idx)
            if peak_distance < min_distance:
                continue
            
            # Check if peaks are at similar price levels
            first_peak_price = safe_float(df_copy.loc[first_peak_idx, 'High'])
            second_peak_price = safe_float(df_copy.loc[second_peak_idx, 'High'])
            price_diff_pct = abs(first_peak_price - second_peak_price) / first_peak_price
            
            if price_diff_pct > max_price_diff_pct:
                continue
            
            # Find the lowest point (neckline/support) between the two peaks
            between_peaks = df_copy.loc[first_peak_idx:second_peak_idx]
            if between_peaks.empty:
                continue
                
            neckline_price = safe_float(between_peaks['Low'].min())
            
            # Look for breakdown after the second peak
            after_second_peak = df_copy.loc[second_peak_idx:]
            if len(after_second_peak) < 3:
                continue
                
            # Find breakdown point (close below neckline) using boolean mask
            breakdown_mask = after_second_peak['Close'] < neckline_price
            breakdown = after_second_peak[breakdown_mask]
            if len(breakdown) == 0:
                continue
                
            breakdown_idx = breakdown.index[0]
            
            # Pattern found
            return first_peak_idx, second_peak_idx, breakdown_idx
    
    return None, None, None

def plot_double_top(df, first_top_idx, second_top_idx, breakdown_idx, image_path='double_top_pattern.png'):
    """
    Plots the Double Top pattern with the detected points.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        first_top_idx: Index of the first top.
        second_top_idx: Index of the second top.
        breakdown_idx: Index of the breakdown point.
        image_path (str): Path to save the plot image.
        
    Returns:
        str: Path to the saved image.
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Calculate neckline/support level
        between_tops = df_copy.loc[first_top_idx:second_top_idx]
        if between_tops.empty:
            # Handle the case where between_tops is empty
            neckline_price = safe_float(df_copy.loc[first_top_idx:second_top_idx, 'Low'].min())
            neckline_idx = first_top_idx  # Fallback to first_top_idx if we can't find minimum
        else:
            neckline_price = safe_float(between_tops['Low'].min())
            neckline_idx = between_tops['Low'].idxmin()
        
        # Calculate pattern height and target
        first_top_high = safe_float(df_copy.loc[first_top_idx, 'High'])
        pattern_height = first_top_high - neckline_price
        target_price = neckline_price - pattern_height
        
        # Create plot
        plt.figure(figsize=(14, 7))
        
        # Plot price data
        plt.plot(df_copy.index, df_copy['Close'], label='Close Price', color='blue', linewidth=1)
        
        # Highlight the pattern
        plt.scatter(first_top_idx, df_copy.loc[first_top_idx, 'High'], color='red', s=100, label='First Top')
        plt.scatter(second_top_idx, df_copy.loc[second_top_idx, 'High'], color='red', s=100, label='Second Top')
        plt.scatter(neckline_idx, neckline_price, color='blue', s=80, label='Neckline')
        plt.scatter(breakdown_idx, df_copy.loc[breakdown_idx, 'Close'], color='green', s=100, label='Breakdown')
        
        # Plot neckline/support
        plt.axhline(y=neckline_price, color='blue', linestyle='--', linewidth=1.5, label='Support/Neckline')
        
        # Plot target - safely calculate target_idx
        breakdown_loc = df_copy.index.get_loc(breakdown_idx)
        target_loc = min(breakdown_loc + 10, len(df_copy) - 1)
        target_idx = df_copy.index[target_loc]
        
        breakdown_close = safe_float(df_copy.loc[breakdown_idx, 'Close'])
        plt.plot([breakdown_idx, target_idx], [breakdown_close, target_price], 
                'g--', linewidth=1.5, label='Price Target')
        plt.annotate(f'Target: {target_price:.2f}', (target_idx, target_price), 
                    textcoords="offset points", xytext=(5,0), ha='left')
        
        # Add annotations
        first_top_high = safe_float(df_copy.loc[first_top_idx, 'High'])
        second_top_high = safe_float(df_copy.loc[second_top_idx, 'High'])
        breakdown_close = safe_float(df_copy.loc[breakdown_idx, 'Close'])
        
        plt.annotate('First Top', (first_top_idx, first_top_high), 
                    textcoords="offset points", xytext=(0,10), ha='center')
        plt.annotate('Second Top', (second_top_idx, second_top_high), 
                    textcoords="offset points", xytext=(0,10), ha='center')
        plt.annotate('Breakdown', (breakdown_idx, breakdown_close), 
                    textcoords="offset points", xytext=(0,-15), ha='center')
        
        # Add title and labels
        plt.title('Double Top Pattern: Bearish Reversal Signal', fontsize=15)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(image_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return image_path
    except Exception as e:
        print(f"Error plotting Double Top pattern: {e}")
        return None

def invokeDoubleTop(df):
    """
    Detects and analyzes Double Top pattern in the given financial data.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        
    Returns:
        tuple: (str, str) - Analysis message and path to the generated image (if any).
    """
    try:
        # Create a copy to avoid modifying the original dataframe
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 20:
            return "Insufficient data for Double Top pattern detection. Need at least 20 data points.", None
        
        # Detect Double Top pattern
        first_top_idx, second_top_idx, breakdown_idx = detect_double_top(df_copy)
        
        if first_top_idx is None or second_top_idx is None or breakdown_idx is None:
            return "No Double Top pattern detected in the given timeframe.", None
        
        # Calculate neckline/support level
        between_tops = df_copy.loc[first_top_idx:second_top_idx]
        if between_tops.empty:
            return "Error: Empty data between tops.", None
            
        neckline_price = safe_float(between_tops['Low'].min())
        
        # Generate the plot
        image_path = plot_double_top(df_copy, first_top_idx, second_top_idx, breakdown_idx)
        
        # Calculate pattern metrics
        first_top_price = safe_float(df_copy.loc[first_top_idx, 'High'])
        second_top_price = safe_float(df_copy.loc[second_top_idx, 'High'])
        breakdown_price = safe_float(df_copy.loc[breakdown_idx, 'Close'])
        pattern_height = first_top_price - neckline_price
        target_price = neckline_price - pattern_height
        current_price = safe_float(df_copy['Close'].iloc[-1])
        potential_drop = ((target_price / current_price) - 1) * 100
        
        # Prepare analysis message
        message = "Double Top pattern detected!\n\n"
        message += f"First Top: {first_top_price:.2f}\n"
        message += f"Second Top: {second_top_price:.2f}\n"
        message += f"Neckline/Support: {neckline_price:.2f}\n"
        message += f"Breakdown Price: {breakdown_price:.2f}\n"
        message += f"Pattern Height: {pattern_height:.2f}\n"
        message += f"Current Price: {current_price:.2f}\n"
        message += f"Target Price: {target_price:.2f} (Potential drop: {potential_drop:.2f}%)\n\n"
        
        # Use explicit comparison for current price vs neckline
        if current_price < neckline_price:
            message += "Status: Breakdown confirmed. Bearish signal active."
        else:
            message += "Status: Awaiting breakdown below neckline/support."
        
        return message, image_path
        
    except Exception as e:
        return f"Error analyzing Double Top pattern: {e}", None

# Example usage:
# result_message, image_path = invokeDoubleTop(df)
