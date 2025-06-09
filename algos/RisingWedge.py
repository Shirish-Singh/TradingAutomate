import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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


def detect_rising_wedge(df, window_size=5, min_points=3):

    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None
        
    """
    Detects the Rising Wedge pattern in a given DataFrame.

    :param df: DataFrame containing financial data.
    :param window_size: The rolling window size to identify peaks and troughs.
    :param min_points: Minimum number of points required to confirm a pattern.
    :return: A tuple containing upper trendline points, lower trendline points, and the breakdown point.
    """
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Make sure we have enough data
    if len(df_copy) < window_size * 3:
        return [], [], None
    
    # Find local maximums and minimums
    df_copy['rolling_max'] = df_copy['High'].rolling(window=window_size, center=True).max()
    df_copy['rolling_min'] = df_copy['Low'].rolling(window=window_size, center=True).min()
    
    # Identify peaks and troughs using boolean masks
    peak_mask = df_copy['High'] == df_copy['rolling_max']
    trough_mask = df_copy['Low'] == df_copy['rolling_min']
    
    peaks = df_copy[peak_mask]
    troughs = df_copy[trough_mask]
    
    if len(peaks) < min_points or len(troughs) < min_points:
        return [], [], None
    
    # Get peak and trough indices
    peak_indices = peaks.index.tolist()
    trough_indices = troughs.index.tolist()
    
    # Find upper and lower trendlines
    upper_trendline = []
    lower_trendline = []
    
    # Try to find at least min_points peaks that form an upward sloping line
    for i in range(len(peak_indices) - (min_points - 1)):
        potential_peaks = peak_indices[i:i+min_points]
        x_values = [df_copy.index.get_loc(idx) for idx in potential_peaks]
        y_values = [safe_float(df_copy.loc[idx, 'High']) for idx in potential_peaks]
        
        # Calculate slope of upper trendline
        slope_upper, intercept_upper = np.polyfit(x_values, y_values, 1)
        
        # For a rising wedge, the upper trendline should have a positive slope
        if safe_float(slope_upper) > 0:
            upper_trendline = potential_peaks
            break
    
    # If we couldn't find a valid upper trendline, return empty
    if not upper_trendline:
        return [], [], None
    
    # Try to find at least min_points troughs that form an upward sloping line
    for i in range(len(trough_indices) - (min_points - 1)):
        potential_troughs = trough_indices[i:i+min_points]
        x_values = [df_copy.index.get_loc(idx) for idx in potential_troughs]
        y_values = [safe_float(df_copy.loc[idx, 'Low']) for idx in potential_troughs]
        
        # Calculate slope of lower trendline
        slope_lower, intercept_lower = np.polyfit(x_values, y_values, 1)
        
        # For a rising wedge, the lower trendline should have a positive slope
        if safe_float(slope_lower) > 0:
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
    
    # For a rising wedge, the lower trendline should have a steeper slope than the upper trendline
    if safe_float(slope_lower) <= safe_float(slope_upper):
        return [], [], None
    
    # Look for breakdown after the pattern formation
    last_point = max(upper_trendline[-1], lower_trendline[-1])
    after_pattern = df_copy.loc[last_point:].iloc[1:]  # Start from the next point
    
    breakdown_point = None
    
    # Check for breakdown below the lower trendline
    for idx, row in after_pattern.iterrows():
        x_pos = df_copy.index.get_loc(idx)
        
        # Calculate the projected lower trendline value at this point
        if x_pos >= 0:
            projected_lower_trendline = safe_float(slope_lower) * x_pos + safe_float(intercept_lower)
            current_close = safe_float(row['Close'])
            
            # Check if price breaks below the lower trendline
            if current_close < projected_lower_trendline:
                breakdown_point = idx
                break
    
    return upper_trendline, lower_trendline, breakdown_point

def plot_rising_wedge(df, upper_trendline, lower_trendline, breakdown_point, image_path='rising_wedge_pattern.png'):
    """
    Plots the Rising Wedge pattern and saves the plot as an image.

    :param df: DataFrame containing financial data.
    :param upper_trendline: List of indices for the upper trendline points.
    :param lower_trendline: List of indices for the lower trendline points.
    :param breakdown_point: The breakdown point index.
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
        
        # Highlight breakdown point if available
        if breakdown_point is not None:
            breakdown_low = safe_float(df_copy.loc[breakdown_point, 'Low'])
            plt.scatter(breakdown_point, breakdown_low, color='green', s=100, label='Breakdown Point')
            
            # Calculate target (measured move equal to the height of the wedge at the breakdown)
            last_upper = upper_trendline[-1]
            last_lower = lower_trendline[-1]
            x_breakdown = df_copy.index.get_loc(breakdown_point)
            
            # Calculate the projected upper and lower trendline values at the breakdown point
            projected_upper = slope_upper * x_breakdown + intercept_upper
            projected_lower = slope_lower * x_breakdown + intercept_lower
            
            # Calculate the height of the wedge at the breakdown
            wedge_height = projected_upper - projected_lower
            
            # Target price is the breakdown price minus the wedge height
            target_price = breakdown_low - wedge_height
            
            # Plot the target line
            plt.axhline(y=target_price, color='green', linestyle='--', 
                      label=f'Target: {target_price:.2f}')
        
        plt.title('Rising Wedge Pattern')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plt.savefig(image_path)
        plt.close()
        
        return image_path
    except Exception as e:
        print(f"Error plotting Rising Wedge pattern: {e}")
        return None

def invokeRisingWedge(df):
    """
    Invokes the detection of the Rising Wedge pattern and returns the result.

    :param df: DataFrame containing financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 20:  # Minimum data needed for pattern detection
            return "Insufficient data for Rising Wedge pattern detection.", None
        
        # Detect the Rising Wedge pattern
        upper_trendline, lower_trendline, breakdown_point = detect_rising_wedge(df_copy)
        
        if upper_trendline and lower_trendline:
            # Generate the plot
            image_path = plot_rising_wedge(df_copy, upper_trendline, lower_trendline, breakdown_point)
            
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
                message = "Rising Wedge pattern detected!\n\n"
                message += f"Pattern Duration: {pattern_duration} periods\n"
                
                if breakdown_point is not None:
                    breakdown_price = safe_float(df_copy.loc[breakdown_point, 'Low'])
                    current_price = safe_float(df_copy['Close'].iloc[-1])
                    message += f"Breakdown Price: {breakdown_price:.2f}\n"
                    message += f"Current Price: {current_price:.2f}\n"
                    message += "Status: Breakdown confirmed. Bearish signal active."
                else:
                    current_price = safe_float(df_copy['Close'].iloc[-1])
                    message += f"Current Price: {current_price:.2f}\n"
                    message += "Status: Pattern forming. Watch for potential breakdown."
                
                return message, image_path
            else:
                return "Error generating Rising Wedge pattern visualization.", None
        else:
            return "No Rising Wedge pattern detected in the given timeframe.", None
    except Exception as e:
        return f"Error during Rising Wedge detection: {e}", None
