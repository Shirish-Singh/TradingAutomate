import pandas as pd
import matplotlib.pyplot as plt
import os

def detect_double_bottom(df, min_distance_between_lows=30, min_depth=0.1):
    """
    Detects the Double Bottom pattern in a given financial DataFrame.

    Args:
        df (pd.DataFrame): Financial data containing 'High', 'Low', 'Open', 'Close', 'Volume'.
        min_distance_between_lows (int): Minimum number of days between two lows to form a double bottom.
        min_depth (float): Minimum depth of the lows from the highs as a percentage to qualify.

    Returns:
        Tuple: Indices for the first low, second low, and breakout point or (None, None, None) if not found.
    """
    # Find local minimums in the 'Low' price
    lows = df['Low'].rolling(window=5, center=True).min()
    potential_lows = df['Low'] == lows

    # Filter potential lows with a significant depth from highs
    low_points = df[potential_lows]
    significant_lows = low_points[low_points['High'] - low_points['Low'] > low_points['High'] * min_depth]

    # Iterate to find pairs of lows that form a double bottom
    for i in range(len(significant_lows)):
        for j in range(i + min_distance_between_lows, len(significant_lows)):
            first_low = significant_lows.iloc[i]
            second_low = significant_lows.iloc[j]

            # Check if lows are approximately at the same level
            if abs(first_low['Low'] - second_low['Low']) < first_low['Low'] * min_depth:
                # Define resistance level (highest point between the two lows)
                resistance = df['High'][first_low.name:second_low.name].max()

                # Confirm breakout
                breakout_point = df[df.index > second_low.name]
                breakout = breakout_point[breakout_point['High'] > resistance]

                if not breakout.empty:
                    return first_low.name, second_low.name, breakout.index[0]

    return None, None, None


def plot_double_bottom(df, first_low, second_low, breakout_point, image_path='double_bottom_pattern.png'):
    """
    Plots the Double Bottom pattern and saves it as an image.

    Args:
        df (pd.DataFrame): Financial data.
        first_low, second_low, breakout_point (datetime): Indices for the first low, second low, and breakout point.
        image_path (str): The path to save the image.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    # Highlight the first and second lows
    plt.scatter(first_low, df.at[first_low, 'Low'], color='red', label='First Low')
    plt.scatter(second_low, df.at[second_low, 'Low'], color='red', label='Second Low')

    # Highlight the breakout point
    plt.scatter(breakout_point, df.at[breakout_point, 'Close'], color='green', label='Breakout Point')

    plt.title('Double Bottom Pattern')
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
    Invokes the detection and plotting of the Double Bottom pattern.

    Args:
        df (pd.DataFrame): Financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        first_low, second_low, breakout_point = detect_double_bottom(df)
        if first_low is not None and second_low is not None and breakout_point is not None:
            image_path = plot_double_bottom(df, first_low, second_low, breakout_point)
            return "Potential Double Bottom pattern detected.", image_path
        else:
            return "No Double Bottom pattern detected.", None
    except ValueError as e:
        return f"Error: {e}", None

# Example usage:
# result_message, image_path = invokeDoubleBottom(df)
