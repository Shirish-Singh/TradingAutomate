import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np

def detect_rising_wedge(df, window_size=20, angle_threshold=0.03):
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

# Example usage
# trendline_points, breakdown_point = detect_rising_wedge(df)


import matplotlib.pyplot as plt

def plot_rising_wedge(df, trendline_points, breakdown_point):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price')

    # Plot the rising wedge pattern
    for peak_index, trough_index in trendline_points:
        trendline = df.loc[peak_index:trough_index]
        plt.plot(trendline.index, trendline['Low'], color='red', linestyle='--', label='Trendline')

    # Highlight the breakdown point
    plt.scatter(breakdown_point, df['Low'].loc[breakdown_point], color='green', label='Breakdown Point')

    plt.title('Rising Wedge Pattern')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
# plot_rising_wedge(df, trendline_points, breakdown_point)
def invokeRisingWedge(df):
    # Detect the Rising Wedge pattern
    trendline_points, breakdown_point = detect_rising_wedge(df)

    # If a pattern is detected, plot it
    if trendline_points and breakdown_point:
        print("Potential Rising Wedge pattern detected.")
        plot_rising_wedge(df, trendline_points, breakdown_point)
    else:
        print("No Rising Wedge pattern detected.")

# Example usage
# invokeRisingWedge(df)

# Example usage
# lower_trendline, breakdown_point = detect_rising_wedge(df)
# plot_rising_wedge(df, lower_trendline, breakdown_point)
