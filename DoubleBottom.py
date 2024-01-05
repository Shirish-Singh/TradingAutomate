import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

# Assume 'df' is a DataFrame with 'Date', 'High', 'Low', 'Open', 'Close', 'Volume'
# Typically, you would load this data from a CSV file or financial API.

def detect_double_bottom(df, min_distance_between_lows=30, min_depth=0.1):
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

# Example usage
# first_low_date, second_low_date, breakout_date = detect_double_bottom(df)


def plot_double_bottom(df, first_low, second_low, breakout_point):
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
    plt.show()

# Example usage
# plot_double_bottom(df, first_low_date, second_low_date, breakout_date)

# Using the function
# first_low, second_low, breakout_point = detect_double_bottom(df)
# plot_double_bottom(df, first_low, second_low, breakout_point)

def invokeDoubleBottom(df):
    # Detect the double bottom pattern
    first_low, second_low, breakout_point = detect_double_bottom(df)

    # If a pattern is detected, plot it
    if first_low is not None and second_low is not None and breakout_point is not None:
        print("Potential Double bottom pattern detected.")
        plot_double_bottom(df, first_low, second_low, breakout_point)
    else:
        print("No double bottom pattern detected.")

# Example usage
# invokeDoubleBottom(df)
