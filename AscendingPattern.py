import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

def detect_ascending_triangle(df):
    # Parameters for the ascending triangle
    min_triangle_length = 20  # Minimum length for the triangle pattern

    # Find potential resistance levels - flat price areas
    resistance = df['High'].rolling(window=5).max()

    # Find ascending trendline - increasing lows
    higher_lows = df['Low'] > df['Low'].rolling(window=5).min()

    # Check for breakout above resistance
    breakout = df['High'] > resistance

    for i in range(len(df) - min_triangle_length):
        if higher_lows.iloc[i:i + min_triangle_length].all() and breakout.iloc[i + min_triangle_length]:
            return i, i + min_triangle_length, i + min_triangle_length

    return None, None, None

def plot_ascending_triangle(df, start, end, breakout_point):
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
    plt.show()

# Example usage
# start, end, breakout_point = detect_ascending_triangle(df)
# if start is not None and end is not None and breakout_point is not None:
#     plot_ascending_triangle(df, start, end, breakout_point)
def invokeAscendingTriangle(df):
    # Detect the ascending triangle pattern
    start, end, breakout_point = detect_ascending_triangle(df)

    # If a pattern is detected, plot it
    if start is not None and end is not None and breakout_point is not None:
        print("Potential ascending triangle pattern detected.")
        plot_ascending_triangle(df, start, end, breakout_point)
    else:
        print("No ascending triangle pattern detected.")

# Example usage
# invokeAscendingTriangle(df)
