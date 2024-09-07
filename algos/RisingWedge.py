import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def detect_rising_wedge(df, window_size=20, angle_threshold=0.03):
    """
    Detects the Rising Wedge pattern in a given DataFrame.

    :param df: DataFrame containing financial data.
    :param window_size: The rolling window size to identify peaks and troughs.
    :param angle_threshold: The minimum slope required to consider a rising trendline.
    :return: A list of trendline points (peak_index, trough_index) and the breakdown point, if detected.
    """
    peaks = df['High'].rolling(window=window_size, center=True).max()
    troughs = df['Low'].rolling(window=window_size, center=True).min()

    # Identify peaks and troughs
    peak_indices = df.index[df['High'] == peaks]
    trough_indices = df.index[df['Low'] == troughs]

    # Initialize variables to store trendline points
    trendline_points = []

    # Find rising wedge patterns
    for peak_index in peak_indices:
        for trough_index in trough_indices:
            if peak_index < trough_index:
                # Calculate the trendline between the peak and trough
                trendline = df.loc[peak_index:trough_index]
                x_values = range(len(trendline))
                slope, intercept = np.polyfit(x_values, trendline['Low'], 1)

                # Check if the trendline has a positive slope within a certain threshold
                if slope > angle_threshold:
                    trendline_points.append((peak_index, trough_index))
                    break

    # Find the breakdown point
    breakdown_point = None
    for peak_index, trough_index in trendline_points:
        if df['Low'].loc[trough_index:].min() < df['Low'].loc[peak_index]:
            breakdown_point = df['Low'].loc[trough_index:].idxmin()
            break

    return trendline_points, breakdown_point


def plot_rising_wedge(df, trendline_points, breakdown_point, image_path='rising_wedge_pattern.png'):
    """
    Plots the Rising Wedge pattern and saves the plot as an image.

    :param df: DataFrame containing financial data.
    :param trendline_points: List of trendline points (peak_index, trough_index).
    :param breakdown_point: The breakdown point.
    :param image_path: File path to save the plot image.
    :return: The file path where the image is saved.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price')

    # Plot the rising wedge pattern
    for peak_index, trough_index in trendline_points:
        trendline = df.loc[peak_index:trough_index]
        plt.plot(trendline.index, trendline['Low'], color='red', linestyle='--', label='Trendline')

    # Highlight the breakdown point
    plt.scatter(breakdown_point, df['Low'].loc[breakdown_point], color='green', label='Breakdown Point')

    plt.title('Rising Wedge Pattern: Bearish Signal')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    plt.savefig(image_path)
    plt.close()

    return image_path


def invokeRisingWedge(df):
    """
    Invokes the detection of the Rising Wedge pattern and returns the result.

    :param df: DataFrame containing financial data.
    :return: Tuple containing a message and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        # Detect the Rising Wedge pattern
        trendline_points, breakdown_point = detect_rising_wedge(df)

        # If a pattern is detected, plot and save it
        if trendline_points and breakdown_point:
            image_path = plot_rising_wedge(df, trendline_points, breakdown_point)
            return "Potential Rising Wedge pattern detected.", image_path
        else:
            return "No Rising Wedge pattern detected.", None
    except Exception as e:
        return f"Error during Rising Wedge detection: {e}", None
