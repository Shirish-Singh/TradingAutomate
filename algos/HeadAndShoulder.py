import pandas as pd
import matplotlib.pyplot as plt
import os

def detect_head_and_shoulders(df, window_size=20):
    """
    Detects the Head and Shoulders pattern in a given financial DataFrame.

    Args:
        df (pd.DataFrame): Financial data containing 'High', 'Low', 'Open', 'Close'.
        window_size (int): Rolling window size for finding peaks and troughs.

    Returns:
        Tuple: Indices for left shoulder, head, right shoulder, neckline (as a tuple), and breakdown point
               or (None, None, None, None, None) if not found.
    """
    # Find peaks and troughs using rolling windows
    peaks = df['High'].rolling(window=window_size, center=True).max() == df['High']
    troughs = df['Low'].rolling(window=window_size, center=True).min() == df['Low']

    # Logic to identify head and shoulders structure
    for i in range(len(df) - 3 * window_size):
        if peaks.iloc[i] and peaks.iloc[i + 2 * window_size] and peaks.iloc[i + 4 * window_size]:
            left_shoulder = i
            head = i + 2 * window_size
            right_shoulder = i + 4 * window_size

            # Identify the neckline
            left_neckline = df['Low'][i + window_size]
            right_neckline = df['Low'][i + 3 * window_size]

            # Check for breakdown
            breakdown = df['Low'][right_shoulder:] < min(left_neckline, right_neckline)
            if breakdown.any():
                breakdown_point = breakdown.idxmax()
                return left_shoulder, head, right_shoulder, (left_neckline, right_neckline), breakdown_point

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
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    # Highlight the left shoulder, head, and right shoulder
    plt.scatter(left_shoulder, df.at[left_shoulder, 'High'], color='blue', label='Left Shoulder')
    plt.scatter(head, df.at[head, 'High'], color='red', label='Head')
    plt.scatter(right_shoulder, df.at[right_shoulder, 'High'], color='blue', label='Right Shoulder')

    # Plot the neckline
    plt.plot([left_shoulder, right_shoulder], [neckline[0], neckline[1]], color='green', label='Neckline')

    # Highlight the breakdown point
    plt.scatter(breakdown_point, df.at[breakdown_point, 'Low'], color='purple', label='Breakdown Point')

    plt.title('Head and Shoulders Pattern: Bearish Signal')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    plt.savefig(image_path)
    plt.close()

    return image_path


def invokeHeadAndShoulders(df):
    """
    Invokes the detection and plotting of the Head and Shoulders pattern.

    Args:
        df (pd.DataFrame): Financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        left_shoulder, head, right_shoulder, neckline, breakdown_point = detect_head_and_shoulders(df)

        if left_shoulder is not None and head is not None and right_shoulder is not None and neckline is not None and breakdown_point is not None:
            image_path = plot_head_and_shoulders(df, left_shoulder, head, right_shoulder, neckline, breakdown_point)
            return "Potential Head and Shoulders pattern detected.", image_path
        else:
            return "No Head and Shoulders pattern detected.", None
    except Exception as e:
        return f"Error during Head and Shoulders detection: {e}", None

# Example usage:
# result_message, image_path = invokeHeadAndShoulders(df)
