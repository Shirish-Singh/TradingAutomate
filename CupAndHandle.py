import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

# Assume 'df' is a DataFrame with 'Date', 'High', 'Low', 'Open', 'Close', 'Volume'
# Typically, you would load this data from a CSV file or financial API.

# Parameters for the cup and handle
min_cup_length = 50  # Minimum number of days for the cup
max_handle_length = 25  # Maximum number of days for the handle
min_depth = 0.1  # Minimum depth of the cup as a percentage of the price

def detect_cup_and_handle(df):

    # Define the rolling window size for the cup
    cup_window = 120  # This is arbitrary and would need to be tuned for your dataset


    potential_cup_mask = df['Low'].rolling(window=cup_window, center=True).min() == df['Low']

    # Adjusted logic for handles and breakouts using the mask
    close_rolled = df['Close'].rolling(window=20).mean()
    volume_rolled = df['Volume'].rolling(window=5).mean()

    # Handles are detected where the price dips slightly after the cup
    handles = (df['Low'] < close_rolled) & potential_cup_mask

    # Breakouts are detected by a close price greater than the rolling mean and a spike in volume
    breakout_volume = df['Volume'] > volume_rolled * 1.5
    breakouts = (df['Close'] > close_rolled) & breakout_volume & handles.shift(-1)

    if handles.any() and breakouts.any():
        # Find the first handle and the first breakout
        handle_start = handles.idxmax()
        breakout_point = breakouts.idxmax()

        # Assume cup start is 'cup_window' periods before the handle
        cup_start = handle_start - cup_window

        return cup_start, handle_start, breakout_point
    else:
        return None, None, None


def plot_cup_and_handle(df, cup_start, cup_end, handle_start, handle_end, breakout_point):
    plt.figure(figsize=(15, 7))
    plt.plot(df['Date'], df['Close'], label='Close Price')

    # Highlight the cup and handle pattern
    plt.plot([cup_start, cup_end], [df.loc[cup_start, 'Close'], df.loc[cup_end, 'Close']], color='green', label='Cup')
    plt.plot([handle_start, handle_end], [df.loc[handle_start, 'Close'], df.loc[handle_end, 'Close']], color='orange',
             label='Handle')

    # Mark the breakout point
    plt.scatter(breakout_point, df.loc[breakout_point, 'Close'], color='red', label='Breakout Point')

    plt.title('Cup and Handle Pattern')
    plt.legend()
    plt.show()


def invokeCandH(df):
    # This function would be used as follows:
    cup_start, handle_start, breakout_point = detect_cup_and_handle(df)
    # You would then pass these to the plotting function to visualize the pattern
    if cup_start and handle_start and breakout_point:
        print("Potential Cup and Handle pattern detected.")
        plot_cup_and_handle(df, cup_start, handle_start, breakout_point)
    else:
        print("No Cup and Handle Pattern found")

