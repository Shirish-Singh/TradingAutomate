import pandas as pd
import matplotlib.pyplot as plt
import os

def detect_ascending_triangle(df, min_triangle_length=20):
    """
    Detects the Ascending Triangle pattern in a given financial DataFrame.

    Args:
        df (pd.DataFrame): Financial data containing 'High', 'Low', 'Open', 'Close'.
        min_triangle_length (int): Minimum length for the ascending triangle pattern.

    Returns:
        Tuple: Start index, end index, and breakout point or (None, None, None) if not found.
    """
    # Find potential resistance levels - flat price areas
    resistance = df['High'].rolling(window=5).max()

    # Find ascending trendline - increasing lows
    higher_lows = df['Low'] > df['Low'].rolling(window=5).min()

    # Check for breakout above resistance
    breakout = df['High'] > resistance

    # Iterate to detect ascending triangle pattern
    for i in range(len(df) - min_triangle_length):
        if higher_lows.iloc[i:i + min_triangle_length].all() and breakout.iloc[i + min_triangle_length]:
            return i, i + min_triangle_length, i + min_triangle_length

    return None, None, None


def plot_ascending_triangle(df, start, end, breakout_point, image_path='ascending_triangle_pattern.png'):
    """
    Plots the Ascending Triangle pattern and saves it as an image.

    Args:
        df (pd.DataFrame): Financial data.
        start, end, breakout_point (int): Indices for the start, end, and breakout point.
        image_path (str): The path to save the image.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    # Highlight the ascending triangle pattern
    plt.scatter(df.index[start], df['Low'][start], color='green', label='Triangle Start')
    plt.scatter(df.index[end], df['Low'][end], color='orange', label='Triangle End')
    plt.scatter(df.index[breakout_point], df['High'][breakout_point], color='red', label='Breakout Point')

    plt.title('Ascending Triangle Pattern')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    plt.savefig(image_path)
    plt.close()

    return image_path


def invokeAscendingTriangle(df):
    """
    Invokes the detection and plotting of the Ascending Triangle pattern.

    Args:
        df (pd.DataFrame): Financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        start, end, breakout_point = detect_ascending_triangle(df)

        if start is not None and end is not None and breakout_point is not None:
            image_path = plot_ascending_triangle(df, start, end, breakout_point)
            return "Potential Ascending Triangle pattern detected.", image_path
        else:
            return "No Ascending Triangle pattern detected.", None
    except Exception as e:
        return f"Error: {e}", None

# Example usage:
# result_message, image_path = invokeAscendingTriangle(df)
