import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from .fibonacci_calculator import FibonacciCalculator

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

def detect_cup_and_handle(df):
    """
    Detects Cup and Handle pattern in the given financial data.
    
    The Cup and Handle pattern consists of:
    1. A rounded bottom formation (the cup)
    2. A small downward drift (the handle)
    3. A breakout above the cup's rim
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        
    Returns:
        tuple: (bool, dict) - Whether pattern was detected and pattern details
    """
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Need at least 60 periods for a proper cup and handle
    if len(df_copy) < 60:
        return False, {}
    
    # Parameters for cup and handle detection
    cup_min_periods = 30  # Minimum periods for cup formation
    handle_min_periods = 5  # Minimum periods for handle formation
    handle_max_periods = 15  # Maximum periods for handle formation
    cup_depth_threshold = 0.15  # Cup should have a significant depth (15% from high)
    handle_depth_threshold = 0.15  # Handle shouldn't retrace more than 15% of cup height
    handle_max_depth = 0.5  # Handle shouldn't retrace more than 50% of cup depth
    
    # Calculate rolling max for potential cup rim detection
    df_copy['rolling_max_30'] = df_copy['High'].rolling(window=30).max()
    
    pattern_found = False
    pattern_data = {}
    
    # Iterate through potential cup formations
    for i in range(30, len(df_copy) - handle_max_periods):
        # Check for potential cup formation
        left_rim_idx = i - cup_min_periods
        if left_rim_idx < 0:
            continue
            
        # Find potential left rim (local high)
        left_section = df_copy.iloc[max(0, left_rim_idx-10):left_rim_idx+10]
        if left_section.empty:
            continue
            
        left_rim_offset = left_section['High'].idxmax()
        if hasattr(left_rim_offset, 'iloc'):
            left_rim_offset = left_rim_offset.iloc[0]
        left_rim_price = safe_float(df_copy.loc[left_rim_offset, 'High'])
        
        # Find cup bottom (lowest point between left rim and current position)
        cup_section = df_copy.loc[left_rim_offset:df_copy.index[i]]
        if cup_section.empty:
            continue
            
        cup_bottom_offset = cup_section['Low'].idxmin()
        if hasattr(cup_bottom_offset, 'iloc'):
            cup_bottom_offset = cup_bottom_offset.iloc[0]
        cup_bottom_price = safe_float(df_copy.loc[cup_bottom_offset, 'Low'])
        
        # Calculate cup depth
        cup_depth = left_rim_price - cup_bottom_price
        cup_depth_pct = cup_depth / left_rim_price
        
        # Check if cup is deep enough
        if cup_depth_pct < cup_depth_threshold:
            continue
        
        # Current position is potential right rim
        right_rim_price = safe_float(df_copy.loc[df_copy.index[i], 'High'])
        
        # Check if right rim is near the level of left rim
        if abs(right_rim_price - left_rim_price) / left_rim_price > 0.05:
            continue
        
        # Look for handle formation after right rim
        handle_section = df_copy.iloc[i:i+handle_max_periods]
        if handle_section.empty or len(handle_section) < handle_min_periods:
            continue
            
        # Find handle bottom
        handle_bottom_offset = handle_section['Low'].idxmin()
        if hasattr(handle_bottom_offset, 'iloc'):
            handle_bottom_offset = handle_bottom_offset.iloc[0]
        handle_bottom_price = safe_float(df_copy.loc[handle_bottom_offset, 'Low'])
        
        # Calculate handle depth
        handle_depth = right_rim_price - handle_bottom_price
        handle_depth_pct = handle_depth / right_rim_price
        
        # Check if handle has appropriate depth (not too shallow, not too deep)
        if handle_depth_pct < 0.03 or handle_depth / cup_depth > handle_max_depth:
            continue
        
        # Check if handle doesn't retrace too much of the cup
        if handle_bottom_price < cup_bottom_price + cup_depth * 0.5:
            continue
        
        # Look for breakout after handle
        handle_end_idx = handle_section.index[-1]
        breakout_section = df_copy.loc[handle_bottom_offset:].iloc[1:]
        
        if breakout_section.empty:
            continue
        
        # Find breakout point (close above right rim)
        breakout_idx = None
        for j in range(len(breakout_section)):
            if safe_float(breakout_section.iloc[j]['Close'] if j < len(breakout_section) else 0.0) > right_rim_price:
                breakout_idx = breakout_section.index[j]
                break
        
        # If no breakout found, continue to next potential pattern
        if breakout_idx is None:
            continue
        
        # Pattern found
        pattern_found = True
        pattern_data = {
            'left_rim_idx': left_rim_offset,
            'left_rim_price': left_rim_price,
            'cup_bottom_idx': cup_bottom_offset,
            'cup_bottom_price': cup_bottom_price,
            'right_rim_idx': df_copy.index[i],
            'right_rim_price': right_rim_price,
            'handle_bottom_idx': handle_bottom_offset,
            'handle_bottom_price': handle_bottom_price,
            'breakout_idx': breakout_idx,
            'breakout_price': safe_float(df_copy.loc[breakout_idx]['Close'] if breakout_idx in df_copy.index else 0.0),
            'cup_depth': cup_depth,
            'handle_depth': handle_depth,
            'cup_periods': len(cup_section),
            'handle_periods': len(handle_section)
        }
        break
    
    return pattern_found, pattern_data

def plot_cup_and_handle(df, pattern_data, image_path='cup_and_handle.png'):
    """
    Plots the Cup and Handle pattern with the detected points.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        pattern_data (dict): Dictionary with pattern details.
        image_path (str): Path to save the plot image.
        
    Returns:
        str: Path to the saved image.
    """
    try:
        # Create a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Extract pattern points
        left_rim_idx = pattern_data['left_rim_idx']
        cup_bottom_idx = pattern_data['cup_bottom_idx']
        right_rim_idx = pattern_data['right_rim_idx']
        handle_bottom_idx = pattern_data['handle_bottom_idx']
        breakout_idx = pattern_data['breakout_idx']
        
        # Calculate target price (measured move equal to cup depth)
        cup_depth = pattern_data['cup_depth']
        breakout_price = pattern_data['breakout_price']
        target_price = breakout_price + cup_depth
        
        # Create plot
        plt.figure(figsize=(14, 7))
        
        # Plot price data
        plt.plot(df_copy.index, df_copy['Close'], label='Close Price', color='blue', linewidth=1)
        
        # Highlight the pattern points
        plt.scatter(left_rim_idx, df_copy.loc[left_rim_idx, 'High'], color='red', s=100, label='Left Rim')
        plt.scatter(cup_bottom_idx, df_copy.loc[cup_bottom_idx, 'Low'], color='green', s=100, label='Cup Bottom')
        plt.scatter(right_rim_idx, df_copy.loc[right_rim_idx, 'High'], color='red', s=100, label='Right Rim')
        plt.scatter(handle_bottom_idx, df_copy.loc[handle_bottom_idx, 'Low'], color='purple', s=100, label='Handle Bottom')
        plt.scatter(breakout_idx, df_copy.loc[breakout_idx]['Close'] if breakout_idx in df_copy.index else 0.0, color='orange', s=100, label='Breakout')
        
        # Draw cup and handle shape
        cup_handle_x = [left_rim_idx, cup_bottom_idx, right_rim_idx, handle_bottom_idx, breakout_idx]
        cup_handle_y = [
            df_copy.loc[left_rim_idx, 'High'], 
            df_copy.loc[cup_bottom_idx, 'Low'], 
            df_copy.loc[right_rim_idx, 'High'], 
            df_copy.loc[handle_bottom_idx, 'Low'], 
            df_copy.loc[breakout_idx]['Close'] if breakout_idx in df_copy.index else 0.0
        ]
        plt.plot(cup_handle_x, cup_handle_y, 'r--', linewidth=1.5, label='Cup and Handle Pattern')
        
        # Draw target line
        target_idx = df_copy.index[-1]  # Use last available data point for target line
        plt.axhline(y=target_price, color='green', linestyle='--', linewidth=1.5, label=f'Target: {target_price:.2f}')
        
        # Add annotations
        plt.annotate('Left Rim', (left_rim_idx, df_copy.loc[left_rim_idx, 'High']), 
                    textcoords="offset points", xytext=(0,10), ha='center')
        plt.annotate('Cup Bottom', (cup_bottom_idx, df_copy.loc[cup_bottom_idx, 'Low']), 
                    textcoords="offset points", xytext=(0,-15), ha='center')
        plt.annotate('Right Rim', (right_rim_idx, df_copy.loc[right_rim_idx, 'High']), 
                    textcoords="offset points", xytext=(0,10), ha='center')
        plt.annotate('Handle Bottom', (handle_bottom_idx, df_copy.loc[handle_bottom_idx, 'Low']), 
                    textcoords="offset points", xytext=(0,-15), ha='center')
        plt.annotate('Breakout', (breakout_idx, df_copy.loc[breakout_idx]['Close'] if breakout_idx in df_copy.index else 0.0), 
                    textcoords="offset points", xytext=(5,5), ha='left')
        plt.annotate(f'Target: {target_price:.2f}', (target_idx, target_price), 
                    textcoords="offset points", xytext=(5,0), ha='left')
        
        # Add title and labels
        plt.title('Cup and Handle Pattern: Bullish Continuation Signal', fontsize=15)
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
        print(f"Error plotting Cup and Handle pattern: {e}")
        return None

def invokeCupAndHandle(df):
    """
    Detects and analyzes Cup and Handle pattern in the given financial data.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        
    Returns:
        tuple: (str, str) - Analysis message and path to the generated image (if any).
    """
    try:
        # Create a copy to avoid modifying the original dataframe
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 60:
            return "Insufficient data for Cup and Handle pattern detection. Need at least 60 data points.", None
        
        # Detect Cup and Handle pattern
        pattern_found, pattern_data = detect_cup_and_handle(df_copy)
        
        if not pattern_found:
            return "No Cup and Handle pattern detected in the given timeframe.", None
        
        # Generate the plot
        image_path = plot_cup_and_handle(df_copy, pattern_data)
        
        # Calculate pattern metrics
        cup_depth = pattern_data['cup_depth']
        cup_periods = pattern_data['cup_periods']
        handle_periods = pattern_data['handle_periods']
        breakout_price = pattern_data['breakout_price']
        target_price = breakout_price + cup_depth
        current_price = safe_float(df_copy['Close'].iloc[-1])
        potential_gain = ((target_price / current_price) - 1) * 100
        
        # Prepare analysis message
        message = "Cup and Handle pattern detected!\n\n"
        message += f"Cup Duration: {cup_periods} periods\n"
        message += f"Handle Duration: {handle_periods} periods\n"
        message += f"Cup Depth: {cup_depth:.2f}\n"
        message += f"Breakout Price: {breakout_price:.2f}\n"
        message += f"Current Price: {current_price:.2f}\n"
        message += f"Target Price: {target_price:.2f} (Potential gain: {potential_gain:.2f}%)\n\n"
        
        # Add status based on current price vs breakout price
        if safe_float(current_price) < safe_float(pattern_data['breakout_price']):
            message += "Status: Pattern forming. Awaiting breakout confirmation."
        else:
            message += "Status: Breakout confirmed. Bullish signal active."
        
        return message, image_path
        
    except Exception as e:
        return f"Error analyzing Cup and Handle pattern: {e}", None

# Example usage:
# result_message, image_path = invokeCupAndHandle(df)
