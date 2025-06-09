import pandas as pd
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


def detect_head_and_shoulders(df, window_size=5):

    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None, None
        
    """
    Detects the Head and Shoulders pattern in a given financial DataFrame.

    Args:
        df (pd.DataFrame): Financial data containing 'High', 'Low', 'Open', 'Close'.
        window_size (int): Rolling window size for finding peaks and troughs.

    Returns:
        Tuple: Indices for left shoulder, head, right shoulder, neckline (as a tuple), and breakdown point
               or (None, None, None, None, None) if not found.
    """
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Check if we have enough data
    if len(df_copy) < window_size * 3:
        return None, None, None, None, None
    
    # Find local maximums (peaks) for potential shoulders and head
    df_copy['rolling_max'] = df_copy['High'].rolling(window=window_size, center=True).max()
    
    # Create a boolean mask for potential peaks
    # Ensure alignment before comparison
    left, right = ensure_aligned(df_copy['High'], df_copy['rolling_max'])
    peak_mask = left == right
    potential_peaks = df_copy[peak_mask]
    
    if len(potential_peaks) < 3:
        return None, None, None, None, None
    
    # Get the indices of potential peaks
    peak_indices = potential_peaks.index.tolist()
    
    # Try to find head and shoulders pattern among the peaks
    for i in range(len(peak_indices) - 2):
        left_shoulder_idx = peak_indices[i]
        head_idx = peak_indices[i + 1]
        right_shoulder_idx = peak_indices[i + 2]
        
        # Check if the peaks form a head and shoulders pattern
        # The head should be higher than both shoulders
        left_shoulder_price = safe_float(df_copy.loc[left_shoulder_idx, 'High'])
        head_price = safe_float(df_copy.loc[head_idx, 'High'])
        right_shoulder_price = safe_float(df_copy.loc[right_shoulder_idx, 'High'])
        
        # Explicit comparisons to avoid ambiguous truth value errors
        if (head_price > left_shoulder_price and 
            head_price > right_shoulder_price and
            abs(left_shoulder_price - right_shoulder_price) / left_shoulder_price < 0.1):
            
            # Find the troughs between the peaks for neckline
            left_section = df_copy.loc[left_shoulder_idx:head_idx]
            right_section = df_copy.loc[head_idx:right_shoulder_idx]
            
            if left_section.empty or right_section.empty:
                continue
                
            left_trough_idx = left_section['Low'].idxmin()
            right_trough_idx = right_section['Low'].idxmin()
            
            # Get the prices at the troughs
            left_trough_price = safe_float(df_copy.loc[left_trough_idx, 'Low'])
            right_trough_price = safe_float(df_copy.loc[right_trough_idx, 'Low'])
            
            # Calculate neckline (linear interpolation between troughs)
            neckline = (left_trough_price, right_trough_price)
            
            # Look for breakdown after the right shoulder
            breakdown_point = None
            after_right_shoulder = df_copy.loc[right_shoulder_idx:]
            
            # Skip if there's no data after the right shoulder
            if after_right_shoulder.empty:
                continue
                
            # Calculate the neckline at each point after the right shoulder
            for idx, row in after_right_shoulder.iterrows():
                # Calculate the position ratio between left and right trough
                if right_trough_idx == left_trough_idx:  # Avoid division by zero
                    continue
                    
                position_ratio = (idx - left_trough_idx) / (right_trough_idx - left_trough_idx)
                
                # Calculate the neckline price at this position
                neckline_price = left_trough_price + position_ratio * (right_trough_price - left_trough_price)
                
                # Check if price breaks below the neckline
                current_low = safe_float(row['Low'])
                if current_low < neckline_price:
                    breakdown_point = idx
                    break
            
            # If we found a complete pattern with breakdown
            if breakdown_point is not None:
                return left_shoulder_idx, head_idx, right_shoulder_idx, neckline, breakdown_point
    
    return None, None, None, None, None

def plot_head_and_shoulders(df, left_shoulder, head, right_shoulder, neckline, breakdown_point, image_path='head_and_shoulders_pattern.png'):
    """
    Plots the Head and Shoulders pattern and saves the plot as an image.

    Args:
        df (pd.DataFrame): Financial data.
        left_shoulder, head, right_shoulder (int): Indices for the left shoulder, head, and right shoulder.
        neckline (tuple): Neckline prices.
        breakdown_point (int): Index of the breakdown point.
        image_path (str): The path to save the image.
    """
    try:
        # Create a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        plt.figure(figsize=(12, 6))
        
        # Plot price data
        plt.plot(df_copy.index, df_copy['Close'], label='Close Price')
        
        # Highlight the pattern points
        left_shoulder_high = safe_float(df_copy.loc[left_shoulder, 'High'])
        head_high = safe_float(df_copy.loc[head, 'High'])
        right_shoulder_high = safe_float(df_copy.loc[right_shoulder, 'High'])
        breakdown_low = safe_float(df_copy.loc[breakdown_point, 'Low'])
        
        plt.scatter(left_shoulder, left_shoulder_high, color='red', s=100, label='Left Shoulder')
        plt.scatter(head, head_high, color='red', s=100, label='Head')
        plt.scatter(right_shoulder, right_shoulder_high, color='red', s=100, label='Right Shoulder')
        plt.scatter(breakdown_point, breakdown_low, color='green', s=100, label='Breakdown')
        
        # Draw neckline
        neckline_start = safe_float(neckline[0])
        neckline_end = safe_float(neckline[1])
        plt.plot([left_shoulder, right_shoulder], [neckline_start, neckline_end], 'b--', label='Neckline')
        
        # Extend neckline to the breakdown point
        position_ratio = (breakdown_point - left_shoulder) / (right_shoulder - left_shoulder) if right_shoulder != left_shoulder else 1
        neckline_at_breakdown = neckline_start + position_ratio * (neckline_end - neckline_start)
        plt.plot([right_shoulder, breakdown_point], [neckline_end, neckline_at_breakdown], 'b--')
        
        # Calculate and draw target (measured move equal to head height from neckline)
        head_height = head_high - neckline_start
        target_price = neckline_at_breakdown - head_height
        plt.axhline(y=target_price, color='green', linestyle='--', label=f'Target: {target_price:.2f}')
        
        plt.title('Head and Shoulders Pattern')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plt.savefig(image_path)
        plt.close()
        
        return image_path
    except Exception as e:
        print(f"Error plotting Head and Shoulders pattern: {e}")
        return None

def invokeHeadAndShoulders(df):
    """
    Invokes the detection and plotting of the Head and Shoulders pattern.

    Args:
        df (pd.DataFrame): Financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 15:  # Minimum data needed for pattern detection
            return "Insufficient data for Head and Shoulders pattern detection.", None
        
        # Detect the Head and Shoulders pattern
        left_shoulder, head, right_shoulder, neckline, breakdown_point = detect_head_and_shoulders(df_copy)
        
        if left_shoulder is not None and head is not None and right_shoulder is not None and neckline is not None and breakdown_point is not None:
            # Plot the pattern
            image_path = plot_head_and_shoulders(df_copy, left_shoulder, head, right_shoulder, neckline, breakdown_point)
            
            # Calculate pattern metrics for analysis
            if image_path:
                left_shoulder_price = safe_float(df_copy.loc[left_shoulder, 'High'])
                head_price = safe_float(df_copy.loc[head, 'High'])
                right_shoulder_price = safe_float(df_copy.loc[right_shoulder, 'High'])
                breakdown_price = safe_float(df_copy.loc[breakdown_point, 'Low'])
                current_price = safe_float(df_copy['Close'].iloc[-1])
                
                # Calculate pattern height and target
                neckline_at_breakdown = neckline[0] + (neckline[1] - neckline[0]) * (breakdown_point - left_shoulder) / (right_shoulder - left_shoulder) if right_shoulder != left_shoulder else neckline[0]
                pattern_height = head_price - neckline_at_breakdown
                target_price = neckline_at_breakdown - pattern_height
                potential_drop = ((target_price / current_price) - 1) * 100
                
                # Prepare analysis message
                message = "Head and Shoulders pattern detected!\n\n"
                message += f"Left Shoulder: {left_shoulder_price:.2f}\n"
                message += f"Head: {head_price:.2f}\n"
                message += f"Right Shoulder: {right_shoulder_price:.2f}\n"
                message += f"Breakdown Price: {breakdown_price:.2f}\n"
                message += f"Pattern Height: {pattern_height:.2f}\n"
                message += f"Current Price: {current_price:.2f}\n"
                message += f"Target Price: {target_price:.2f} (Potential drop: {potential_drop:.2f}%)\n\n"
                
                if current_price < breakdown_price:
                    message += "Status: Breakdown confirmed. Bearish signal active."
                else:
                    message += "Status: Awaiting confirmation of breakdown."
                
                return message, image_path
            else:
                return "Error generating Head and Shoulders pattern visualization.", None
        else:
            return "No Head and Shoulders pattern detected in the given timeframe.", None
    except Exception as e:
        return f"Error during Head and Shoulders detection: {e}", None

# Example usage:
# result_message, image_path = invokeHeadAndShoulders(df)
