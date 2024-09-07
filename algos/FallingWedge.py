import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from algos.fibonacci_calculator import FibonacciCalculator


def detect_falling_wedge(df, window_size=20, angle_threshold=-0.03):
    """
    Detects the Falling Wedge pattern in a given DataFrame.

    :param df: DataFrame containing financial data.
    :param window_size: The rolling window size to identify peaks and troughs.
    :param angle_threshold: The maximum slope required to consider a falling trendline.
    :return: A list of trendline points (peak_index, trough_index) and the breakout point, if detected.
    """
    peaks = df['High'].rolling(window=window_size, center=True).max()
    troughs = df['Low'].rolling(window=window_size, center=True).min()

    # Identify peaks and troughs
    peak_indices = df.index[df['High'] == peaks]
    trough_indices = df.index[df['Low'] == troughs]

    # Initialize variables to store trendline points
    trendline_points = []

    # Find falling wedge patterns
    for peak_index in peak_indices:
        for trough_index in trough_indices:
            if peak_index < trough_index:
                # Calculate the trendline between the peak and trough
                trendline = df.loc[peak_index:trough_index]
                x_values = range(len(trendline))
                slope, intercept = np.polyfit(x_values, trendline['High'], 1)

                # Check if the trendline has a negative slope within a certain threshold
                if slope < angle_threshold:
                    trendline_points.append((peak_index, trough_index))
                    break

    # Find the breakout point (where price breaks above the trendline)
    breakout_point = None
    for peak_index, trough_index in trendline_points:
        if df['High'].loc[trough_index:].max() > df['High'].loc[peak_index]:
            breakout_point = df['High'].loc[trough_index:].idxmax()
            break

    return trendline_points, breakout_point


def calculate_dynamic_fibonacci_targets(df, peak_index, trough_index, breakout_index):
    """
    Calculates Fibonacci retracement and extension levels dynamically based on the range between the peak and trough.

    :param df: DataFrame containing financial data.
    :param peak_index: The index of the peak in the falling wedge pattern.
    :param trough_index: The index of the trough in the falling wedge pattern.
    :param breakout_index: The index of the breakout point.
    :return: A dictionary containing potential Fibonacci retracement and extension levels.
    """
    # Get the price values for the peak, trough, and breakout points
    peak_price = df['High'].loc[peak_index]
    trough_price = df['Low'].loc[trough_index]
    breakout_price = df['High'].loc[breakout_index]

    # Calculate the range between the peak and trough
    price_range = peak_price - trough_price

    # Fibonacci retracement levels
    fib_levels = {
        'Fibonacci 0.236 Target': trough_price + price_range * 0.236,
        'Fibonacci 0.382 Target': trough_price + price_range * 0.382,
        'Fibonacci 0.5 Target': trough_price + price_range * 0.5,
        'Fibonacci 0.618 Target': trough_price + price_range * 0.618,
        'Fibonacci 0.786 Target': trough_price + price_range * 0.786,
    }

    # Fibonacci extension level (1.618 as a common extension level in bull trends)
    fib_extension = {
        'Fibonacci 1.618 Target': breakout_price + price_range * 1.618
    }

    # Combine retracement and extension levels
    fib_targets = {**fib_levels, **fib_extension}

    return fib_targets


def plot_falling_wedge_with_dynamic_fibonacci(df, trendline_points, breakout_point, fib_targets,
                                              image_path='falling_wedge_with_dynamic_fibonacci.png'):
    """
    Plots the Falling Wedge pattern along with dynamically detected Fibonacci targets and saves the plot as an image.

    :param df: DataFrame containing financial data.
    :param trendline_points: List of trendline points (peak_index, trough_index).
    :param breakout_point: The breakout point.
    :param fib_targets: Dictionary of dynamically calculated Fibonacci retracement and extension targets.
    :param image_path: File path to save the plot image.
    :return: The file path where the image is saved.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price')

    # Plot the falling wedge pattern
    for peak_index, trough_index in trendline_points:
        trendline = df.loc[peak_index:trough_index]
        plt.plot(trendline.index, trendline['High'], color='blue', linestyle='--', label='Trendline')

    # Highlight the breakout point
    plt.scatter(breakout_point, df['High'].loc[breakout_point], color='green', label='Breakout Point')

    # Plot Fibonacci targets
    for target_name, target_price in fib_targets.items():
        plt.axhline(y=target_price, color='orange', linestyle='--', label=f'{target_name}: {target_price:.2f}')

    plt.title('Falling Wedge Pattern with Dynamic Fibonacci Targets')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    plt.savefig(image_path)
    plt.close()

    return image_path


def invokeFallingWedge(df):
    """
    Invokes the detection of the Falling Wedge pattern and calculates dynamic Fibonacci targets.

    :param df: DataFrame containing financial data.
    :return: Tuple containing a message, targets, and an image path if a pattern is detected, otherwise a message and None.
    """
    try:
        # Detect the Falling Wedge pattern
        trendline_points, breakout_point = detect_falling_wedge(df)

        # If a pattern is detected, calculate the dynamic Fibonacci targets and plot the pattern with the targets
        if trendline_points and breakout_point:
            # Get the peak and trough from the first trendline points
            peak_index, trough_index = trendline_points[0]

            # Calculate dynamic Fibonacci targets
            fib_targets = calculate_dynamic_fibonacci_targets(df, peak_index, trough_index, breakout_point)

            # Plot the falling wedge with Fibonacci targets and save it
            image_path = plot_falling_wedge_with_dynamic_fibonacci(df, trendline_points, breakout_point, fib_targets)
            return f"Potential Falling Wedge pattern detected with dynamic Fibonacci targets: {fib_targets}", image_path
        else:
            return "No Falling Wedge pattern detected.", None
    except Exception as e:
        return f"Error during Falling Wedge detection: {e}", None
