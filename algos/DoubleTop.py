import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import os

def detect_double_top(df, window_size=20, threshold=0.05):
    """
    Detects the Double Top pattern in a given DataFrame.

    :param df: DataFrame containing 'High' and 'Low' prices.
    :param window_size: Rolling window size for detecting tops.
    :param threshold: Threshold for determining if two tops are close in price.
    :return: Indices of the first top, second top, support level, and breakdown point.
    """
    # Find local maximums
    highs = df['High'].rolling(window=window_size, center=True).max() == df['High']
    potential_highs = df[highs]

    # Iterate through potential highs to find double tops
    for i in range(len(potential_highs)-1):
        for j in range(i+1, len(potential_highs)):
            first_top = potential_highs.iloc[i]
            second_top = potential_highs.iloc[j]

            # Check if tops are within threshold of each other
            if abs(first_top['High'] - second_top['High']) < first_top['High'] * threshold:
                # Identify the support level (lowest point between two tops)
                support_level = df['Low'][first_top.name:second_top.name].min()

                # Confirm breakdown
                breakdown = df[df.index > second_top.name]
                if not breakdown[breakdown['Low'] < support_level].empty:
                    breakdown_point = breakdown[breakdown['Low'] < support_level].index[0]
                    return first_top.name, second_top.name, support_level, breakdown_point

    return None, None, None, None

def plot_double_top(df, first_top, second_top, support_level, breakdown_point, image_path='double_top_pattern.png'):
    """
    Plots the Double Top pattern and saves it as an image.

    :param df: DataFrame containing financial data.
    :param first_top: Index of the first top.
    :param second_top: Index of the second top.
    :param support_level: Price level of support between the tops.
    :param breakdown_point: Index where the breakdown occurs.
    :param image_path: File path to save the image.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    # Highlight the first and second tops
    plt.scatter(first_top, df.at[first_top, 'High'], color='red', label='First Top')
    plt.scatter(second_top, df.at[second_top, 'High'], color='red', label='Second Top')

    # Plot the support level
    plt.axhline(y=support_level, color='blue', linestyle='--', label='Support Level')

    # Highlight the breakdown point
    plt.scatter(breakdown_point, df.at[breakdown_point, 'Low'], color='green', label='Breakdown Point')

    plt.title('Double Top Pattern: Bearish Signal')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    plt.savefig(image_path)
    plt.close()

    return image_path

def invokeDoubleTop(df):
    """
    Invokes the detection of the Double Top pattern and returns the result.

    :param df: DataFrame containing financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        # Detect the Double Top pattern
        first_top, second_top, support_level, breakdown_point = detect_double_top(df)

        # If a pattern is detected, plot and save it
        if first_top is not None and second_top is not None and support_level is not None and breakdown_point is not None:
            print("Potential Double Top pattern detected.")
            image_path = plot_double_top(df, first_top, second_top, support_level, breakdown_point)
            return "Potential Double Top pattern detected.", image_path
        else:
            print("No Double Top pattern detected.")
            return "No Double Top pattern detected.", None
    except Exception as e:
        print(f"Error during Double Top detection: {e}")
        return f"Error during Double Top detection: {e}", None

# Example usage:
# result_message, image_path = invokeDoubleTop(df)
