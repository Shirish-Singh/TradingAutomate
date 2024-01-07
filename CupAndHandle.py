import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num


def detect_cup_and_handle(df, cup_window_ratio=0.2):
    """
    Detects the cup and handle pattern in a given financial DataFrame.

    Args:
        df (pd.DataFrame): Financial data containing 'Date', 'High', 'Low', 'Open', 'Close', 'Volume'.
        cup_window_ratio (float): Ratio of the dataset length to set the cup window size.

    Returns:
        Tuple: Indices for cup start, handle start, and breakout point or (None, None, None) if not found.
    """
    if not {'High', 'Low', 'Open', 'Close', 'Volume'}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'High', 'Low', 'Open', 'Close', 'Volume' columns")


    # Dynamically set the cup window based on the length of the dataset
    cup_window = max(int(len(df) * cup_window_ratio), 20)  # Ensure a minimum size

    potential_cup_mask = df['Low'].rolling(window=cup_window, center=True).min() == df['Low']

    close_rolled = df['Close'].rolling(window=20).mean()
    volume_rolled = df['Volume'].rolling(window=5).mean()

    handles = (df['Low'] < close_rolled) & potential_cup_mask
    breakout_volume = df['Volume'] > volume_rolled * 1.5
    breakouts = (df['Close'] > close_rolled) & breakout_volume & handles.shift(-1)

    if handles.any() and breakouts.any():
        handle_start = handles.idxmax()
        breakout_point = breakouts.idxmax()
        cup_start = handle_start - pd.Timedelta(days=cup_window)

        return cup_start, handle_start, breakout_point
    else:
        return None, None, None


def plot_cup_and_handle(df, cup_start, handle_start, breakout_point):
    """
    Plots the cup and handle pattern.

    Args:
        df (pd.DataFrame): Financial data.
        cup_start, handle_start, breakout_point (datetime): Indices for cup start, handle start, and breakout point.
    """
    plt.figure(figsize=(15, 7))
    plt.plot(df.index, df['Close'], label='Close Price')

    # Define cup_end and handle_end
    cup_end = handle_start
    handle_end = breakout_point

    # Plot the cup and handle
    plt.plot([cup_start, cup_end], [df.loc[cup_start, 'Close'], df.loc[cup_end, 'Close']], color='green', label='Cup')
    plt.plot([handle_start, handle_end], [df.loc[handle_start, 'Close'], df.loc[handle_end, 'Close']], color='orange',
             label='Handle')

    # Mark the breakout point
    plt.scatter(breakout_point, df.loc[breakout_point, 'Close'], color='red', label='Breakout Point')

    plt.title('Cup and Handle Pattern')
    plt.legend()
    plt.show()


def invokeCandH(df):
    """
    Invokes the detection and plotting of the Cup and Handle pattern.

    Args:
        df (pd.DataFrame): Financial data.
    """
    try:
        cup_start, handle_start, breakout_point = detect_cup_and_handle(df)
        if cup_start is not None and handle_start is not None and breakout_point is not None:
            print("Potential Cup and Handle pattern detected.")
            plot_cup_and_handle(df, cup_start, handle_start, breakout_point)
        else:
            print("No Cup and Handle Pattern found")
    except ValueError as e:
        print(f"Error: {e}")

# Example usage:
# df = pd.read_csv('your_data.csv')
# invokeCandH(df)
