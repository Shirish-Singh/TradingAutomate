import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from algos.fibonacci_calculator import FibonacciCalculator

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
            # For Series objects, align on index
            if isinstance(left, pd.Series) and isinstance(right, pd.Series):
                left_aligned, right_aligned = left.align(right, axis=0, copy=False)
                return left_aligned, right_aligned
            # For DataFrame objects, align on both axes
            elif isinstance(left, pd.DataFrame) and isinstance(right, pd.DataFrame):
                left_aligned, right_aligned = left.align(right, axis=None, copy=False)
                return left_aligned, right_aligned
            # For mixed types, convert to compatible types
            else:
                # If one is Series and one is DataFrame, convert Series to DataFrame
                if isinstance(left, pd.Series) and isinstance(right, pd.DataFrame):
                    left = pd.DataFrame(left)
                elif isinstance(left, pd.DataFrame) and isinstance(right, pd.Series):
                    right = pd.DataFrame(right)
                left_aligned, right_aligned = left.align(right, axis=None, copy=False)
                return left_aligned, right_aligned
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

def detect_falling_wedge(df, window_size=5, min_points=3):
    """
    Detects the Falling Wedge pattern in a given DataFrame.

    :param df: DataFrame containing financial data.
    :param window_size: The rolling window size to identify peaks and troughs.
    :param min_points: Minimum number of points required to confirm a pattern.
    :return: A tuple containing upper trendline points, lower trendline points, and the breakout point.
    """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None
        
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Make sure we have enough data
    if len(df_copy) < window_size * 3:
        return [], [], None
    
    # Find local maximums and minimums
    df_copy['rolling_max'] = df_copy['High'].rolling(window=window_size, center=True).max()
    df_copy['rolling_min'] = df_copy['Low'].rolling(window=window_size, center=True).min()
    
    # Handle NaNs in rolling max/min with interpolation
    df_copy['rolling_max'] = df_copy['rolling_max'].interpolate()
    df_copy['rolling_min'] = df_copy['rolling_min'].interpolate()
    
    # Handle any remaining NaNs by filling with corresponding values
    if df_copy['rolling_max'].isna().any():
        for idx in df_copy.index[df_copy['rolling_max'].isna()]:
            df_copy.loc[idx, 'rolling_max'] = df_copy.loc[idx, 'High']
    
    if df_copy['rolling_min'].isna().any():
        for idx in df_copy.index[df_copy['rolling_min'].isna()]:
            df_copy.loc[idx, 'rolling_min'] = df_copy.loc[idx, 'Low']
    
    # Final safety check - if there are still NaNs, use the mean
    if df_copy['rolling_max'].isna().any():
        mean_high = df_copy['High'].mean()
        for idx in df_copy.index[df_copy['rolling_max'].isna()]:
            df_copy.loc[idx, 'rolling_max'] = mean_high
            
    if df_copy['rolling_min'].isna().any():
        mean_low = df_copy['Low'].mean()
        for idx in df_copy.index[df_copy['rolling_min'].isna()]:
            df_copy.loc[idx, 'rolling_min'] = mean_low
    
    # Create boolean masks for peaks and troughs using a safer approach
    # Convert to numpy arrays to avoid pandas alignment issues
    high_values = df_copy['High'].values
    low_values = df_copy['Low'].values
    rolling_max_values = df_copy['rolling_max'].values
    rolling_min_values = df_copy['rolling_min'].values
    
    # Find peaks and troughs using numpy comparison with tolerance
    peak_indices = []
    trough_indices = []
    
    for i in range(len(df_copy)):
        if abs(high_values[i] - rolling_max_values[i]) < 1e-10:  # Use small tolerance for float comparison
            peak_indices.append(df_copy.index[i])
        if abs(low_values[i] - rolling_min_values[i]) < 1e-10:  # Use small tolerance for float comparison
            trough_indices.append(df_copy.index[i])
    
    # Filter to get actual peak and trough dataframes
    peaks = df_copy.loc[peak_indices] if peak_indices else df_copy.iloc[0:0]  # Empty DataFrame with same structure
    troughs = df_copy.loc[trough_indices] if trough_indices else df_copy.iloc[0:0]  # Empty DataFrame with same structure
    
    if len(peaks) < min_points or len(troughs) < min_points:
        return [], [], None
    
    # peak_indices and trough_indices are already defined above
    
    # Find upper and lower trendlines
    upper_trendline = []
    lower_trendline = []
    
    # Try to find at least min_points peaks that form a downward sloping line
    for i in range(len(peak_indices) - (min_points - 1)):
        potential_peaks = peak_indices[i:i+min_points]
        x_values = [df_copy.index.get_loc(idx) for idx in potential_peaks]
        y_values = [safe_float(df_copy.loc[idx, 'High']) for idx in potential_peaks]
        
        # Calculate slope of upper trendline
        slope_upper, intercept_upper = np.polyfit(x_values, y_values, 1)
        
        # For a falling wedge, the upper trendline should have a negative slope
        if safe_float(slope_upper) < 0:
            upper_trendline = potential_peaks
            break
    
    # If we couldn't find a valid upper trendline, return empty
    if not upper_trendline:
        return [], [], None
    
    # Try to find at least min_points troughs that form a downward sloping line
    for i in range(len(trough_indices) - (min_points - 1)):
        potential_troughs = trough_indices[i:i+min_points]
        x_values = [df_copy.index.get_loc(idx) for idx in potential_troughs]
        y_values = [safe_float(df_copy.loc[idx, 'Low']) for idx in potential_troughs]
        
        # Calculate slope of lower trendline
        slope_lower, intercept_lower = np.polyfit(x_values, y_values, 1)
        
        # For a falling wedge, the lower trendline should have a negative slope
        if safe_float(slope_lower) < 0:
            lower_trendline = potential_troughs
            break
    
    # If we couldn't find a valid lower trendline, return empty
    if not lower_trendline:
        return [], [], None
    
    # Calculate slopes of both trendlines to confirm converging pattern
    x_upper = [df_copy.index.get_loc(idx) for idx in upper_trendline]
    y_upper = [safe_float(df_copy.loc[idx, 'High']) for idx in upper_trendline]
    slope_upper, intercept_upper = np.polyfit(x_upper, y_upper, 1)
    
    x_lower = [df_copy.index.get_loc(idx) for idx in lower_trendline]
    y_lower = [safe_float(df_copy.loc[idx, 'Low']) for idx in lower_trendline]
    slope_lower, intercept_lower = np.polyfit(x_lower, y_lower, 1)
    
    # For a falling wedge, the upper trendline should have a steeper slope than the lower trendline
    if safe_float(slope_upper) >= safe_float(slope_lower):
        return [], [], None
    
    # Look for breakout after the pattern formation
    last_point = max(upper_trendline[-1], lower_trendline[-1])
    try:
        after_pattern = df_copy.loc[last_point:].iloc[1:]  # Start from the next point
    except Exception:
        # If we can't slice properly, return with no breakout point
        return upper_trendline, lower_trendline, None
    
    breakout_point = None
    
    # Check for breakout above the upper trendline
    for idx, row in after_pattern.iterrows():
        x_pos = df_copy.index.get_loc(idx)
        
        # Calculate the projected upper trendline value at this point
        if x_pos >= 0:
            projected_upper_trendline = safe_float(slope_upper) * x_pos + safe_float(intercept_upper)
            current_close = safe_float(row['Close'])
            
            # Check if price breaks above the upper trendline
            if current_close > projected_upper_trendline:
                breakout_point = idx
                break
    
    return upper_trendline, lower_trendline, breakout_point

def calculate_dynamic_fibonacci_targets(df, upper_trendline, lower_trendline, breakout_index):
    """
    Calculates Fibonacci retracement and extension levels dynamically based on the range between the peak and trough.

    :param df: DataFrame containing financial data.
    :param upper_trendline: List of indices for the upper trendline points.
    :param lower_trendline: List of indices for the lower trendline points.
    :param breakout_index: The index of the breakout point.
    :return: A dictionary containing potential Fibonacci retracement and extension levels.
    """
    try:
        # Create a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Get the peak and trough prices
        peak_price = safe_float(df_copy['High'].loc[upper_trendline[0]])
        trough_price = safe_float(df_copy['Low'].loc[lower_trendline[0]])
        breakout_price = safe_float(df_copy['High'].loc[breakout_index])
        
        # Calculate the price range
        price_range = peak_price - trough_price
        
        # Calculate Fibonacci levels
        fib_targets = {
            'Fibonacci 0.236 Target': safe_float(trough_price + price_range * 0.236),
            'Fibonacci 0.382 Target': safe_float(trough_price + price_range * 0.382),
            'Fibonacci 0.5 Target': safe_float(trough_price + price_range * 0.5),
            'Fibonacci 0.618 Target': safe_float(trough_price + price_range * 0.618),
            'Fibonacci 0.786 Target': safe_float(trough_price + price_range * 0.786),
            'Fibonacci 1.0 Target': peak_price,
            # Extension levels
            'Fibonacci 1.618 Target': safe_float(breakout_price + price_range * 1.618)
        }
        
        return fib_targets
    except Exception as e:
        print(f"Error calculating Fibonacci targets: {e}")
        return {}

def plot_falling_wedge(df, upper_trendline, lower_trendline, breakout_point, fib_targets=None, image_path='falling_wedge_pattern.png'):
    """
    Plots the Falling Wedge pattern and saves the plot as an image.

    :param df: DataFrame containing financial data.
    :param upper_trendline: List of indices for the upper trendline points.
    :param lower_trendline: List of indices for the lower trendline points.
    :param breakout_point: The breakout point index.
    :param fib_targets: Optional dictionary of Fibonacci target levels.
    :param image_path: File path to save the plot image.
    :return: The file path where the image is saved.
    """
    try:
        # Create a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        plt.figure(figsize=(12, 6))
        
        # Plot price data
        plt.plot(df_copy.index, df_copy['Close'], label='Close Price')
        
        # Plot upper trendline
        if upper_trendline:
            # Highlight the upper trendline points
            plt.scatter([idx for idx in upper_trendline], [df_copy.loc[idx, 'High'] for idx in upper_trendline], 
                        color='red', s=50)
            
            # Calculate the best fit line for upper trendline
            x_upper = [df_copy.index.get_loc(idx) for idx in upper_trendline]
            y_upper = [safe_float(df_copy.loc[idx, 'High']) for idx in upper_trendline]
            slope_upper, intercept_upper = np.polyfit(x_upper, y_upper, 1)
            
            # Plot the extended upper trendline
            x_range = range(df_copy.index.get_loc(upper_trendline[0]), df_copy.index.get_loc(df_copy.index[-1]) + 1)
            y_fit_upper = [safe_float(slope_upper) * x + safe_float(intercept_upper) for x in x_range]
            
            # Convert x_range back to datetime indices
            x_datetime = [df_copy.index[x] for x in x_range]
            plt.plot(x_datetime, y_fit_upper, 'r--', linewidth=1.5, label='Upper Trendline')
        
        # Plot lower trendline
        if lower_trendline:
            # Highlight the lower trendline points
            plt.scatter([idx for idx in lower_trendline], [df_copy.loc[idx, 'Low'] for idx in lower_trendline], 
                        color='blue', s=50)
            
            # Calculate the best fit line for lower trendline
            x_lower = [df_copy.index.get_loc(idx) for idx in lower_trendline]
            y_lower = [safe_float(df_copy.loc[idx, 'Low']) for idx in lower_trendline]
            slope_lower, intercept_lower = np.polyfit(x_lower, y_lower, 1)
            
            # Plot the extended lower trendline
            x_range = range(df_copy.index.get_loc(lower_trendline[0]), df_copy.index.get_loc(df_copy.index[-1]) + 1)
            y_fit_lower = [safe_float(slope_lower) * x + safe_float(intercept_lower) for x in x_range]
            
            # Convert x_range back to datetime indices
            x_datetime = [df_copy.index[x] for x in x_range]
            plt.plot(x_datetime, y_fit_lower, 'b--', linewidth=1.5, label='Lower Trendline')
        
        # Highlight breakout point if available
        if breakout_point is not None:
            breakout_high = safe_float(df_copy.loc[breakout_point, 'High'])
            plt.scatter(breakout_point, breakout_high, color='green', s=100, label='Breakout Point')
        
        # Plot Fibonacci levels if available
        if fib_targets:
            for level_name, level_value in fib_targets.items():
                plt.axhline(y=safe_float(level_value), color='purple', linestyle=':', label=level_name)
        
        plt.title('Falling Wedge Pattern')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plt.savefig(image_path)
        plt.close()
        
        return image_path
    except Exception as e:
        print(f"Error plotting Falling Wedge pattern: {e}")
        return None

def invokeFallingWedge(df):
    """
    Invokes the detection of the Falling Wedge pattern and returns the result.

    :param df: DataFrame containing financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 20:  # Minimum data needed for pattern detection
            return "Insufficient data for Falling Wedge pattern detection.", None
        
        # Detect the Falling Wedge pattern
        upper_trendline, lower_trendline, breakout_point = detect_falling_wedge(df_copy)
        
        if upper_trendline and lower_trendline:
            # Calculate Fibonacci targets if breakout point is available
            fib_targets = None
            if breakout_point is not None:
                fib_targets = calculate_dynamic_fibonacci_targets(df_copy, upper_trendline, lower_trendline, breakout_point)
            
            # Generate the plot
            image_path = plot_falling_wedge(df_copy, upper_trendline, lower_trendline, breakout_point, fib_targets)
            
            if image_path:
                # Calculate pattern metrics
                pattern_duration = len(df_copy.loc[min(upper_trendline[0], lower_trendline[0]):max(upper_trendline[-1], lower_trendline[-1])])
                
                # Calculate slopes for analysis
                x_upper = [df_copy.index.get_loc(idx) for idx in upper_trendline]
                y_upper = [df_copy.loc[idx, 'High'] for idx in upper_trendline]
                slope_upper, _ = np.polyfit(x_upper, y_upper, 1)
                
                x_lower = [df_copy.index.get_loc(idx) for idx in lower_trendline]
                y_lower = [df_copy.loc[idx, 'Low'] for idx in lower_trendline]
                slope_lower, _ = np.polyfit(x_lower, y_lower, 1)
                
                # Prepare analysis message
                message = "Falling Wedge pattern detected!\n\n"
                message += f"Pattern Duration: {pattern_duration} periods\n"
                
                if breakout_point is not None:
                    breakout_price = safe_float(df_copy.loc[breakout_point, 'High'])
                    current_price = safe_float(df_copy['Close'].iloc[-1])
                    message += f"Breakout Price: {breakout_price:.2f}\n"
                    message += f"Current Price: {current_price:.2f}\n"
                    message += "Status: Breakout confirmed. Bullish signal active."
                    
                    # Add Fibonacci target information
                    if fib_targets:
                        message += "\n\nPotential Fibonacci Targets:\n"
                        for level_name, level_value in fib_targets.items():
                            message += f"{level_name}: {level_value:.2f}\n"
                else:
                    current_price = safe_float(df_copy['Close'].iloc[-1])
                    message += f"Current Price: {current_price:.2f}\n"
                    message += "Status: Pattern forming. Watch for potential breakout."
                
                return message, image_path
            else:
                return "Error generating Falling Wedge pattern visualization.", None
        else:
            return "No Falling Wedge pattern detected in the given timeframe.", None
    except Exception as e:
        return f"Error during Falling Wedge detection: {e}", None