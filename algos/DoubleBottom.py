import pandas as pd
import matplotlib.pyplot as plt
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


def detect_double_bottom(df, min_distance_between_lows=5, min_depth=0.03):

    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None
        
    """
    Detects the Double Bottom pattern in a given financial DataFrame.

    Args:
        df (pd.DataFrame): Financial data containing 'High', 'Low', 'Open', 'Close', 'Volume'.
        min_distance_between_lows (int): Minimum number of days between two lows to form a double bottom.
        min_depth (float): Minimum depth of the lows from the highs as a percentage to qualify.

    Returns:
        Tuple: Indices for the first low, second low, and breakout point or (None, None, None) if not found.
    """
    # Make a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Make sure we have enough data
    if len(df_copy) < min_distance_between_lows * 2:
        return None, None, None
    
    # Find local minimums in the 'Low' price using a smaller window for more sensitivity
    window_size = 3
    df_copy['rolling_min'] = df_copy['Low'].rolling(window=window_size, center=True).min()
    
    # Create a boolean mask for potential lows
    # Ensure alignment before comparison
    left, right = ensure_aligned(df_copy['Low'], df_copy['rolling_min'])
    low_mask = left == right
    potential_lows = df_copy[low_mask]
    
    # If we don't have enough potential lows, return None
    if len(potential_lows) < 2:
        return None, None, None
    
    # Get the indices of potential lows
    low_indices = potential_lows.index.tolist()
    
    # Iterate through pairs of lows to find double bottom pattern
    for i in range(len(low_indices) - 1):
        for j in range(i + 1, len(low_indices)):
            first_low_idx = low_indices[i]
            second_low_idx = low_indices[j]
            
            # Check if lows are far enough apart
            if df_copy.index.get_loc(second_low_idx) - df_copy.index.get_loc(first_low_idx) < min_distance_between_lows:
                continue
            
            # Safely access DataFrame with alignment
            try:
                try:
                    first_low_price = safe_float(df_copy.loc[first_low_idx, 'Low'])
                except:
                    first_low_price = safe_float(df_copy['Low'].iloc[first_low_idx])
            except:
                first_low_price = safe_float(df_copy.loc[first_low_idx]['Low'])
            # Safely access DataFrame with alignment
            try:
                try:
                    second_low_price = safe_float(df_copy.loc[second_low_idx, 'Low'])
                except:
                    second_low_price = safe_float(df_copy['Low'].iloc[second_low_idx])
            except:
                second_low_price = safe_float(df_copy.loc[second_low_idx]['Low'])
            
            # Check if lows are approximately at the same level (within min_depth %)
            if abs(first_low_price - second_low_price) / first_low_price > min_depth:
                continue
            
            # Find the highest point (resistance) between the two lows
            between_lows = df_copy.loc[first_low_idx:second_low_idx]
            if between_lows.empty:
                continue
                
            resistance_price = safe_float(safe_float(between_lows['High'].max()))
            resistance_idx = between_lows['High'].idxmax()
            
            # Look for a breakout after the second low
            after_second_low = df_copy.loc[second_low_idx:]
            
            if len(after_second_low) > 0:
                # Create a boolean mask for breakout points
                breakout_mask = after_second_low['Close'] > resistance_price
                breakout = after_second_low[breakout_mask]
                
                if not breakout.empty:
                    breakout_idx = breakout.index[0]
                    return first_low_idx, second_low_idx, breakout_idx
    
    return None, None, None

def plot_double_bottom_with_fibonacci(df, first_low, second_low, breakout_point, fib_targets, image_path='double_bottom_with_fibonacci.png'):
    """
    Plots the Double Bottom pattern with Fibonacci levels and saves it as an image.

    Args:
        df (pd.DataFrame): Financial data.
        first_low, second_low, breakout_point (datetime): Indices for the first low, second low, and breakout point.
        fib_targets (dict): Fibonacci retracement and extension levels.
        image_path (str): The path to save the image.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    # Highlight the first and second lows
    plt.scatter(first_low, df.at[first_low, 'Low'], color='red', label='First Low')
    plt.scatter(second_low, df.at[second_low, 'Low'], color='red', label='Second Low')

    # Highlight the breakout point
    plt.scatter(breakout_point, df.at[breakout_point, 'Close'], color='green', label='Breakout Point')

    # Plot Fibonacci targets
    for target_name, target_price in fib_targets.items():
        plt.axhline(y=target_price, color='blue', linestyle='--', label=f'{target_name}: {target_price:.2f}')

    plt.title('Double Bottom Pattern with Fibonacci Targets')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    plt.savefig(image_path)
    plt.close()

    return image_path

def invokeDoubleBottom(df):
    """
    Invokes the detection of the Double Bottom pattern and calculates dynamic Fibonacci targets.

    Args:
        df (pd.DataFrame): Financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        # Make a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        # Check if we have enough data
        if len(df_copy) < 10:  # Minimum data needed for pattern detection
            return "Insufficient data for Double Bottom pattern detection.", None
        
        # Detect the Double Bottom pattern
        first_low, second_low, breakout_point = detect_double_bottom(df_copy)
        
        if first_low is not None and second_low is not None and breakout_point is not None:
            # Create FibonacciCalculator instance
            fib_calculator = FibonacciCalculator(df_copy)

            # Calculate dynamic Fibonacci levels
            fib_targets = fib_calculator.calculate_all_fibonacci_levels(first_low, second_low, breakout_point)

            # Plot the double bottom pattern along with Fibonacci targets
            image_path = plot_double_bottom_with_fibonacci(df_copy, first_low, second_low, breakout_point, fib_targets)
            return f"Potential Double Bottom pattern detected with dynamic Fibonacci targets: {fib_targets}", image_path
        else:
            return "No Double Bottom pattern detected.", None
    except Exception as e:
        return f"Error in Double Bottom pattern detection: {e}", None
