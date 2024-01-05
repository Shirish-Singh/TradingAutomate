import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

def detect_double_top(df, window_size=20, threshold=0.05):
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

# Example usage
# first_top, second_top, support_level, breakdown_point = detect_double_top(df)


def plot_double_top(df, first_top, second_top, support_level, breakdown_point):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    # Highlight the first and second tops
    plt.scatter(first_top, df.at[first_top, 'High'], color='red', label='First Top')
    plt.scatter(second_top, df.at[second_top, 'High'], color='red', label='Second Top')

    # Plot the support level
    plt.axhline(y=support_level, color='blue', linestyle='--', label='Support Level')

    # Highlight the breakdown point
    plt.scatter(breakdown_point, df.at[breakdown_point, 'Low'], color='green', label='Breakdown Point')

    plt.title('Double Top Pattern')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
# plot_double_top(df, first_top, second_top, support_level, breakdown_point)


# Example usage
# first_top, second_top, support_level, breakdown_point = detect_double_top(df)
# plot_double_top(df, first_top, second_top, support_level, breakdown_point)
def invokeDoubleTop(df):
    # Detect the Double Top pattern
    first_top, second_top, support_level, breakdown_point = detect_double_top(df)

    # If a pattern is detected, plot it
    if first_top is not None and second_top is not None and support_level is not None and breakdown_point is not None:
        print("Potential Double Top pattern detected.")
        plot_double_top(df, first_top, second_top, support_level, breakdown_point)
    else:
        print("No Double Top pattern detected.")

# Example usage
# invokeDoubleTop(df)
