import pandas as pd
import matplotlib.pyplot as plt
import os
from algos.fibonacci_calculator import FibonacciCalculator

def safe_float(value):
    if isinstance(value, pd.Series):
        if len(value) == 0:
            return 0.0
        return safe_float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        if value.empty:
            return 0.0
        return safe_float(value.iloc[0, 0])
    return float(value)

def ensure_aligned(left, right):
    if not isinstance(left, (pd.Series, pd.DataFrame)) or not isinstance(right, (pd.Series, pd.DataFrame)):
        return left, right
    if (isinstance(left, pd.Series) and len(left) == 0) or (isinstance(left, pd.DataFrame) and left.empty):
        return 0.0, right
    if (isinstance(right, pd.Series) and len(right) == 0) or (isinstance(right, pd.DataFrame) and right.empty):
        return left, 0.0

    try:
        if isinstance(left, pd.Series) and isinstance(right, pd.Series):
            if not left.index.equals(right.index):
                common_idx = left.index.intersection(right.index)
                if len(common_idx) > 0:
                    return left.loc[common_idx], right.loc[common_idx]
                return safe_float(left), safe_float(right)
            return left.align(right, axis=0, copy=False)
        if isinstance(left, pd.DataFrame) and isinstance(right, pd.DataFrame):
            if not left.index.equals(right.index):
                common_idx = left.index.intersection(right.index)
                if len(common_idx) > 0:
                    return left.loc[common_idx], right.loc[common_idx]
                return safe_float(left), safe_float(right)
            return left.align(right, axis=None, copy=False)
        if isinstance(left, pd.Series):
            left = pd.DataFrame(left)
        if isinstance(right, pd.Series):
            right = pd.DataFrame(right)
        if not left.index.equals(right.index):
            common_idx = left.index.intersection(right.index)
            if len(common_idx) > 0:
                return left.loc[common_idx], right.loc[common_idx]
            return safe_float(left), safe_float(right)
        return left.align(right, axis=None, copy=False)
    except Exception:
        return safe_float(left), safe_float(right)

def detect_double_bottom(df, min_distance_between_lows=5, min_depth=0.03):
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None

    df_copy = df.copy()
    if len(df_copy) < min_distance_between_lows * 2:
        return None, None, None

    window_size = 3
    df_copy['rolling_min'] = df_copy['Low'].rolling(window=window_size, center=True).min()

    try:
        left, right = ensure_aligned(df_copy['Low'], df_copy['rolling_min'])
        if not isinstance(left, pd.Series) or not isinstance(right, pd.Series):
            low_mask = df_copy['Low'].fillna(float('inf')) == df_copy['rolling_min'].fillna(float('inf'))
        else:
            low_mask = left == right
        potential_lows = df_copy[low_mask]
    except:
        try:
            import numpy as np
            low_mask = np.isclose(df_copy['Low'].values, df_copy['rolling_min'].values)
            potential_lows = df_copy.iloc[np.where(low_mask)[0]]
        except:
            low_indices = []
            for i, (low, rolling_min) in enumerate(zip(df_copy['Low'], df_copy['rolling_min'])):
                if pd.notna(low) and pd.notna(rolling_min) and abs(low - rolling_min) < 0.0001:
                    low_indices.append(i)
            potential_lows = df_copy.iloc[low_indices]

    if len(potential_lows) < 2:
        return None, None, None

    low_indices = potential_lows.index.tolist()

    for i in range(len(low_indices) - 1):
        for j in range(i + 1, len(low_indices)):
            first_low_idx = low_indices[i]
            second_low_idx = low_indices[j]

            try:
                first_pos = df_copy.index.get_loc(first_low_idx)
                second_pos = df_copy.index.get_loc(second_low_idx)
                if second_pos - first_pos < min_distance_between_lows:
                    continue
            except:
                continue  # skip if can't determine position

            try:
                first_low_price = safe_float(df_copy.loc[first_low_idx, 'Low'])
            except:
                continue
            try:
                second_low_price = safe_float(df_copy.loc[second_low_idx, 'Low'])
            except:
                continue

            if abs(first_low_price - second_low_price) / first_low_price > min_depth:
                continue

            try:
                between_lows = df_copy.loc[first_low_idx:second_low_idx]
                resistance_price = safe_float(between_lows['High'].max())
                resistance_idx = between_lows['High'].idxmax()
            except:
                continue

            try:
                after_second_low = df_copy.loc[second_low_idx:]
                breakout = after_second_low[after_second_low['Close'] > resistance_price]
                if not breakout.empty:
                    breakout_idx = breakout.index[0]
                    return first_low_idx, second_low_idx, breakout_idx
            except:
                continue

    return None, None, None

def plot_double_bottom_with_fibonacci(df, first_low, second_low, breakout_point, fib_targets, image_path='double_bottom_with_fibonacci.png'):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')

    plt.scatter(first_low, df.loc[first_low, 'Low'], color='red', label='First Low')
    plt.scatter(second_low, df.loc[second_low, 'Low'], color='red', label='Second Low')
    plt.scatter(breakout_point, df.loc[breakout_point, 'Close'], color='green', label='Breakout Point')

    for target_name, target_price in fib_targets.items():
        target_price = safe_float(target_price)
        plt.axhline(y=target_price, color='blue', linestyle='--', label=f'{target_name}: {target_price:.2f}')

    plt.title('Double Bottom Pattern with Fibonacci Targets')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig(image_path)
    plt.close()
    return image_path

def invokeDoubleBottom(df):
    try:
        df_copy = df.copy()
        if len(df_copy) < 10:
            return "Insufficient data for Double Bottom pattern detection.", None

        first_low, second_low, breakout_point = detect_double_bottom(df_copy)

        if first_low is not None and second_low is not None and breakout_point is not None:
            fib_calculator = FibonacciCalculator(df_copy)
            fib_targets = fib_calculator.calculate_all_fibonacci_levels(first_low, second_low, breakout_point)
            image_path = plot_double_bottom_with_fibonacci(df_copy, first_low, second_low, breakout_point, fib_targets)
            return f"Potential Double Bottom pattern detected with dynamic Fibonacci targets: {fib_targets}", image_path
        else:
            return "No Double Bottom pattern detected.", None
    except Exception as e:
        return f"Error in Double Bottom pattern detection: {e}", None