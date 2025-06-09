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
        return safe_float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        if value.empty:
            return 0.0
        return safe_float(value.iloc[0, 0])
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
    import pandas as pd
    
    # Handle scalar values
    if not isinstance(left, (pd.Series, pd.DataFrame)) or not isinstance(right, (pd.Series, pd.DataFrame)):
        return left, right
        
    # Handle empty Series/DataFrames
    if (isinstance(left, pd.Series) and len(left) == 0) or (isinstance(left, pd.DataFrame) and left.empty):
        return 0.0, right
    if (isinstance(right, pd.Series) and len(right) == 0) or (isinstance(right, pd.DataFrame) and right.empty):
        return left, 0.0
    
    # Align Series/DataFrames
    if hasattr(left, 'align') and hasattr(right, 'align'):
        try:
            return left.align(right, axis=0, copy=False)
        except Exception as e:
            # If alignment fails, convert to scalar values as a fallback
            if isinstance(left, (pd.Series, pd.DataFrame)):
                left_val = left.iloc[0] if isinstance(left, pd.Series) else left.iloc[0, 0]
            else:
                left_val = left
                
            if isinstance(right, (pd.Series, pd.DataFrame)):
                right_val = right.iloc[0] if isinstance(right, pd.Series) else right.iloc[0, 0]
            else:
                right_val = right
                
            return left_val, right_val
    
    return left, right


def detect_ascending_triangle(df):
    """
    Detects Ascending Triangle pattern in the given financial data.
    
    An Ascending Triangle consists of:
    1. A horizontal resistance line (flat top)
    2. An upward sloping support line (rising bottoms)
    3. Converging trendlines
    4. Eventual breakout above resistance
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        
    Returns:
        tuple: (pattern_data, support_line, resistance_line, breakout_idx)
    """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        print(f"Missing required columns. Available columns: {df.columns.tolist()}")
        return None, None, None, None
        
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Need at least 30 periods for a proper ascending triangle
    if len(df_copy) < 30:
        return None, None, None, None
    
    # Parameters for ascending triangle detection
    min_touches = 3  # Minimum number of touches on resistance and support
    min_pattern_length = 15  # Minimum number of periods for pattern formation
    max_pattern_length = 60  # Maximum number of periods for pattern formation
    resistance_threshold = 0.02  # Maximum variance in resistance line (2%)
    
    pattern_found = False
    pattern_data = {}
    
    # Iterate through potential pattern formations
    for start_idx in range(len(df_copy) - min_pattern_length):
        end_idx = min(start_idx + max_pattern_length, len(df_copy) - 1)
        
        if end_idx - start_idx < min_pattern_length:
            continue
        
        # Get section of data for pattern detection
        section = df_copy.iloc[start_idx:end_idx+1]
        
        # Find potential resistance level (horizontal line)
        # Look for clustered highs
        highs = section['High'].values
        
        # Use histogram to find the most common high price range
        hist, bin_edges = np.histogram(highs, bins=20)
        most_common_bin = np.argmax(hist)
        resistance_zone_min = float(bin_edges[most_common_bin])
        resistance_zone_max = float(bin_edges[most_common_bin + 1])
        
        # Find highs that touch the resistance zone
        resistance_touches = []
        for i, high in enumerate(highs):
            high_value = float(high)
            if resistance_zone_min <= high_value <= resistance_zone_max:
                resistance_touches.append(i + start_idx)
        
        # Need minimum number of touches on resistance
        if len(resistance_touches) < min_touches:
            continue
        
        # Calculate average resistance level
        resistance_level = np.mean([safe_float(df_copy.iloc[i]['High'].iloc[0]) for i in resistance_touches])
        
        # Find potential support line (rising bottoms)
        # Identify local minima
        local_minima = []
        for i in range(1, len(section) - 1):
            current_low = safe_float(section['Low'].iloc[i].iloc[0])
            prev_low = safe_float(section['Low'].iloc[i-1].iloc[0])
            next_low = safe_float(section['Low'].iloc[i+1].iloc[0])
            if current_low < prev_low and current_low < next_low:
                local_minima.append(i + start_idx)
        
        # Need at least 2 minima to form a support line
        if len(local_minima) < 2:
            continue
        
        # Check if minima are rising (ascending)
        minima_prices = [safe_float(df_copy.iloc[i]['Low'].iloc[0]) for i in local_minima]
        minima_indices = np.array(local_minima)
        
        # Fit a line to the minima
        if len(minima_indices) >= 2:
            slope, intercept = np.polyfit(minima_indices, minima_prices, 1)
            
            # Support line should be ascending
            if float(slope) <= 0:
                continue
            
            # Calculate support line values
            support_line = float(slope) * np.arange(start_idx, end_idx+1) + float(intercept)
            
            # Check for convergence with resistance line
            convergence_idx = int((resistance_level - float(intercept)) / float(slope))
            
            # Convergence should be within a reasonable future point
            if convergence_idx < end_idx or convergence_idx > end_idx + 30:
                continue
            
            # Check for breakout
            breakout_idx = None
            for i in range(end_idx, min(end_idx + 20, len(df_copy) - 1)):
                current_close = safe_float(df_copy.iloc[i]['Close'].iloc[0])
                resistance_threshold = float(resistance_level * 1.01)  # 1% above resistance
                if current_close > resistance_threshold:
                    breakout_idx = i
                    break
            
            # If no breakout yet, check if pattern is still valid
            if breakout_idx is None:
                # Last price should be near resistance
                current_close = safe_float(df_copy.iloc[end_idx]['Close'].iloc[0])
                min_threshold = float(resistance_level * 0.95)
                if current_close < min_threshold:
                    continue
            
            # Pattern found
            pattern_found = True
            pattern_data = {
                'start_idx': start_idx,
                'end_idx': end_idx,
                'resistance_level': float(resistance_level),
                'resistance_touches': resistance_touches,
                'support_slope': float(slope),
                'support_intercept': float(intercept),
                'local_minima': local_minima,
                'convergence_idx': convergence_idx,
                'breakout_idx': breakout_idx
            }
            break
    
    return pattern_found, pattern_data


def plot_ascending_triangle(df, pattern_data, image_path='ascending_triangle.png'):
    """
    Plots the Ascending Triangle pattern with the detected points.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        pattern_data (dict): Dictionary with pattern details.
        image_path (str): Path to save the plot image.
        
    Returns:
        str: Path to the saved image.
    """
    if not pattern_data:
        return None
    
    # Extract pattern points
    start_idx = pattern_data['start_idx']
    end_idx = pattern_data['end_idx']
    resistance_level = pattern_data['resistance_level']
    resistance_touches = pattern_data['resistance_touches']
    support_slope = pattern_data['support_slope']
    support_intercept = pattern_data['support_intercept']
    local_minima = pattern_data['local_minima']
    breakout_idx = pattern_data['breakout_idx']
    
    # Create plot
    plt.figure(figsize=(14, 7))
    
    # Plot price data
    plt.plot(df.index, df['Close'], label='Close Price', color='blue', linewidth=1)
    
    # Highlight the pattern area
    plt.axvspan(df.index[start_idx], df.index[end_idx], alpha=0.1, color='gray')
    
    # Plot resistance line
    plt.axhline(y=resistance_level, color='r', linestyle='-', linewidth=2, 
                label='Resistance', alpha=0.7)
    
    # Plot support line
    x_values = np.arange(start_idx, min(pattern_data['convergence_idx'] + 10, len(df)))
    y_values = support_slope * x_values + support_intercept
    plt.plot(df.index[x_values], y_values, 'g-', linewidth=2, 
             label='Support', alpha=0.7)
    
    # Mark resistance touches
    for idx in resistance_touches:
        plt.plot(df.index[idx], df.iloc[idx]['High'], 'ro', markersize=6)
    
    # Mark support touches (local minima)
    for idx in local_minima:
        plt.plot(df.index[idx], df.iloc[idx]['Low'], 'go', markersize=6)
    
    # Mark breakout if it exists
    if breakout_idx is not None:
        plt.plot(df.index[breakout_idx], df.iloc[breakout_idx]['Close'], 'mo', 
                 markersize=10, label='Breakout')
        
        # Calculate target based on pattern height
        pattern_height = resistance_level - (support_slope * start_idx + support_intercept)
        target_price = resistance_level + pattern_height
        
        # Plot target
        target_idx = min(breakout_idx + (end_idx - start_idx) // 2, len(df) - 1)
        plt.plot([df.index[breakout_idx], df.index[target_idx]], 
                 [resistance_level, target_price], 'm--', linewidth=1.5, 
                 label='Price Target')
        plt.annotate(f'Target: {target_price:.2f}', 
                     (df.index[target_idx], target_price), 
                     textcoords="offset points", xytext=(5,0), ha='left')
        
        # Calculate Fibonacci extension levels
        fib_calc = FibonacciCalculator(df.copy())
        pattern_low = support_slope * start_idx + support_intercept
        # Ensure all parameters are valid floats
        try:
            breakout_close = safe_float(df.iloc[breakout_idx]['Close'])
            fib_levels = fib_calc.calculate_fibonacci_extensions(safe_float(pattern_low), safe_float(resistance_level), 
                                                  breakout_close)
            
            # Plot key Fibonacci extension levels
            for level, price in fib_levels.items():
                if level in [1.618, 2.618]:  # Only show key extension levels
                    plt.axhline(y=price, linestyle='--', alpha=0.5, color='purple', 
                               linewidth=1, label=f'Fib {level}')
                    plt.annotate(f'Fib {level}: {price:.2f}', 
                                 (df.index[-1], price), 
                                 textcoords="offset points", xytext=(5,0), ha='left')
        except Exception as e:
            print(f"Error calculating Fibonacci extensions: {e}")
            # Continue without Fibonacci levels if there's an error
    
    # Add title and labels
    plt.title('Ascending Triangle Pattern Detection', fontsize=15)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(image_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return image_path


def invokeAscendingTriangle(df):
    """
    Detects and analyzes Ascending Triangle pattern in the given financial data.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.
        
    Returns:
        tuple: (str, str) - Analysis message and path to the generated image (if any).
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 30:  # Minimum data needed for pattern detection
            return "Insufficient data for Ascending Triangle pattern detection.", None
        
        # Detect Ascending Triangle pattern
        pattern_found, pattern_data = detect_ascending_triangle(df_copy)
        
        if not pattern_found or len(pattern_data) == 0:
            return "No Ascending Triangle pattern detected in the given timeframe.", None
        
        # Generate the plot
        image_path = plot_ascending_triangle(df_copy, pattern_data)
        
        if image_path is None:
            return "Failed to generate Ascending Triangle pattern plot.", None
        
        # Calculate pattern metrics
        start_idx = pattern_data['start_idx']
        resistance_level = safe_float(pattern_data['resistance_level'])
        support_slope = safe_float(pattern_data['support_slope'])
        support_intercept = safe_float(pattern_data['support_intercept'])
        pattern_start_support = float(support_slope * start_idx + support_intercept)
        pattern_height = float(resistance_level - pattern_start_support)
        pattern_height_pct = float((pattern_height / pattern_start_support) * 100)
        
        # Calculate target price
        target_price = float(resistance_level + pattern_height)
        current_price = safe_float(df_copy['Close'].iloc[-1].iloc[0])
        potential_gain = float(((target_price / current_price) - 1) * 100)
        
        # Check if breakout has occurred
        breakout_status = "Breakout confirmed" if pattern_data['breakout_idx'] is not None else "Awaiting breakout"
        
        # Calculate Fibonacci targets if breakout occurred
        fib_message = ""
        if pattern_data['breakout_idx'] is not None:
            fib_calc = FibonacciCalculator(df.copy())
            breakout_price = safe_float(df_copy.iloc[pattern_data['breakout_idx']]['Close'])
            fib_levels = fib_calc.calculate_fibonacci_extensions(
                pattern_start_support,
                resistance_level,
                breakout_price
            )
            fib_message = "Fibonacci Extension Targets:\n"
            fib_message += f"1.618 Extension: {float(fib_levels[1.618]):.2f}\n"
            fib_message += f"2.618 Extension: {float(fib_levels[2.618]):.2f}\n\n"
        
        # Prepare analysis message
        message = "Ascending Triangle pattern detected!\n\n"
        message += f"Pattern Duration: {pattern_data['end_idx'] - pattern_data['start_idx']} periods\n"
        message += f"Resistance Level: {resistance_level:.2f}\n"
        message += f"Pattern Height: {pattern_height:.2f} ({pattern_height_pct:.2f}%)\n"
        message += f"Current Price: {current_price:.2f}\n"
        message += f"Status: {breakout_status}\n\n"
        
        if pattern_data['breakout_idx'] is not None:
            breakout_price = safe_float(df_copy.iloc[pattern_data['breakout_idx']]['Close'])
            message += f"Breakout Price: {breakout_price:.2f}\n"
            message += f"Measured Move Target: {target_price:.2f} (Potential gain: {potential_gain:.2f}%)\n\n"
            message += fib_message
            message += "Trading Strategy: Consider long positions with stop loss below the ascending support line."
        else:
            message += "Trading Strategy: Watch for breakout above resistance level. " \
                      "Potential entry on confirmed breakout with stop loss below the ascending support line."
        
        return message, image_path
        
    except Exception as e:
        return f"Error analyzing Ascending Triangle pattern: {e}", None
