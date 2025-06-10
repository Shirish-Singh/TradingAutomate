import pandas as pd
import matplotlib.pyplot as plt
import os

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

    if (isinstance(left, pd.Series) and left.empty) or (isinstance(left, pd.DataFrame) and left.empty):
        return 0.0, right
    if (isinstance(right, pd.Series) and right.empty) or (isinstance(right, pd.DataFrame) and right.empty):
        return left, 0.0

    try:
        if isinstance(left, pd.Series) and isinstance(right, pd.Series):
            left.index.name = None
            right.index.name = None
            if not left.index.equals(right.index):
                common_idx = left.index.intersection(right.index)
                if len(common_idx) > 0:
                    return left.loc[common_idx], right.loc[common_idx]
                return safe_float(left), safe_float(right)
            return left.align(right, axis=0, copy=False)

        if isinstance(left, pd.DataFrame) and isinstance(right, pd.DataFrame):
            left.index.name = None
            right.index.name = None
            if not left.index.equals(right.index):
                common_idx = left.index.intersection(right.index)
                if len(common_idx) > 0:
                    return left.loc[common_idx], right.loc[common_idx]
                return safe_float(left), safe_float(right)
            return left.align(right, axis=0, copy=False)

        if isinstance(left, pd.Series):
            left = pd.DataFrame(left)
        if isinstance(right, pd.Series):
            right = pd.DataFrame(right)

        left.index.name = None
        right.index.name = None
        if not left.index.equals(right.index):
            common_idx = left.index.intersection(right.index)
            if len(common_idx) > 0:
                return left.loc[common_idx], right.loc[common_idx]
            return safe_float(left), safe_float(right)

        return left.align(right, axis=0, copy=False)

    except Exception:
        left_val = safe_float(left)
        right_val = safe_float(right)
        return left_val, right_val

def detect_head_and_shoulders(df, window_size=5):
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None, None

    df_copy = df.copy()
    if len(df_copy) < window_size * 3:
        return None, None, None, None, None

    df_copy['rolling_max'] = df_copy['High'].rolling(window=window_size, center=True).max()

    left, right = ensure_aligned(df_copy['High'], df_copy['rolling_max'])
    if isinstance(left, pd.DataFrame):
        left = left.iloc[:, 0]
    if isinstance(right, pd.DataFrame):
        right = right.iloc[:, 0]

    # Ensure we're comparing scalar values, not Series to avoid ambiguity errors
    peak_mask = left.eq(right)
    potential_peaks = df_copy[peak_mask]

    if len(potential_peaks) < 3:
        return None, None, None, None, None

    peak_indices = potential_peaks.index.tolist()

    for i in range(len(peak_indices) - 2):
        left_shoulder_idx = peak_indices[i]
        head_idx = peak_indices[i + 1]
        right_shoulder_idx = peak_indices[i + 2]

        left_shoulder_price = float(safe_float(df_copy.loc[left_shoulder_idx, 'High']))
        head_price = float(safe_float(df_copy.loc[head_idx, 'High']))
        right_shoulder_price = float(safe_float(df_copy.loc[right_shoulder_idx, 'High']))

        # Ensure all comparisons are scalar
        if (isinstance(head_price, (int, float)) and 
            isinstance(left_shoulder_price, (int, float)) and 
            isinstance(right_shoulder_price, (int, float)) and 
            head_price > left_shoulder_price and 
            head_price > right_shoulder_price and 
            abs(left_shoulder_price - right_shoulder_price) / left_shoulder_price < 0.1):
            left_section = df_copy.loc[left_shoulder_idx:head_idx]
            right_section = df_copy.loc[head_idx:right_shoulder_idx]

            if left_section.empty or right_section.empty:
                continue

            left_trough_idx = left_section['Low'].idxmin()
            right_trough_idx = right_section['Low'].idxmin()

            left_trough_price = float(safe_float(df_copy.loc[left_trough_idx, 'Low']))
            right_trough_price = float(safe_float(df_copy.loc[right_trough_idx, 'Low']))

            neckline = (left_trough_price, right_trough_price)
            breakdown_point = None
            after_right_shoulder = df_copy.loc[right_shoulder_idx:]

            if after_right_shoulder.empty:
                continue

            for idx, row in after_right_shoulder.iterrows():
                if isinstance(right_trough_idx, pd.Series) or isinstance(left_trough_idx, pd.Series):
                    continue
                if right_trough_idx == left_trough_idx:
                    continue
                try:
                    position_ratio = (idx - left_trough_idx) / (right_trough_idx - left_trough_idx)
                    neckline_price = left_trough_price + position_ratio * (right_trough_price - left_trough_price)
                    current_low = float(safe_float(row['Low']))
                    if current_low < neckline_price:
                        breakdown_point = idx
                        break
                except:
                    continue

            if breakdown_point is not None:
                return left_shoulder_idx, head_idx, right_shoulder_idx, neckline, breakdown_point

    return None, None, None, None, None

def plot_head_and_shoulders(df, left_shoulder, head, right_shoulder, neckline, breakdown_point, image_path='head_and_shoulders_pattern.png'):
    try:
        df_copy = df.copy()
        plt.figure(figsize=(12, 6))
        plt.plot(df_copy.index, df_copy['Close'], label='Close Price')

        plt.scatter(left_shoulder, safe_float(df_copy.loc[left_shoulder, 'High']), color='red', s=100, label='Left Shoulder')
        plt.scatter(head, safe_float(df_copy.loc[head, 'High']), color='red', s=100, label='Head')
        plt.scatter(right_shoulder, safe_float(df_copy.loc[right_shoulder, 'High']), color='red', s=100, label='Right Shoulder')
        plt.scatter(breakdown_point, safe_float(df_copy.loc[breakdown_point, 'Low']), color='green', s=100, label='Breakdown')

        neckline_start = safe_float(neckline[0])
        neckline_end = safe_float(neckline[1])
        plt.plot([left_shoulder, right_shoulder], [neckline_start, neckline_end], 'b--', label='Neckline')

        # Use scalar comparison
        if isinstance(right_shoulder, pd.Series) or isinstance(left_shoulder, pd.Series):
            ratio = 1
        elif right_shoulder != left_shoulder:
            ratio = (breakdown_point - left_shoulder) / (right_shoulder - left_shoulder)
        else:
            ratio = 1
        neckline_at_breakdown = neckline_start + ratio * (neckline_end - neckline_start)

        plt.plot([right_shoulder, breakdown_point], [neckline_end, neckline_at_breakdown], 'b--')

        head_high = safe_float(df_copy.loc[head, 'High'])
        target_price = neckline_at_breakdown - (head_high - neckline_start)
        plt.axhline(y=target_price, color='green', linestyle='--', label=f'Target: {target_price:.2f}')

        plt.title('Head and Shoulders Pattern')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.savefig(image_path)
        plt.close()
        return image_path
    except Exception as e:
        print(f"Error plotting Head and Shoulders pattern: {e}")
        return None

def invokeHeadAndShoulders(df):
    try:
        df_copy = df.copy()
        if len(df_copy) < 15:
            return "Insufficient data for Head and Shoulders pattern detection.", None

        left_shoulder, head, right_shoulder, neckline, breakdown_point = detect_head_and_shoulders(df_copy)

        if all(x is not None for x in [left_shoulder, head, right_shoulder, neckline, breakdown_point]):
            image_path = plot_head_and_shoulders(df_copy, left_shoulder, head, right_shoulder, neckline, breakdown_point)

            if image_path:
                left_price = safe_float(df_copy.loc[left_shoulder, 'High'])
                head_price = safe_float(df_copy.loc[head, 'High'])
                right_price = safe_float(df_copy.loc[right_shoulder, 'High'])
                breakdown_price = safe_float(df_copy.loc[breakdown_point, 'Low'])
                current_price = safe_float(df_copy['Close'].iloc[-1])

                neckline_at_breakdown = neckline[0] + (neckline[1] - neckline[0]) * (breakdown_point - left_shoulder) / (right_shoulder - left_shoulder) if right_shoulder != left_shoulder else neckline[0]
                pattern_height = head_price - neckline_at_breakdown
                target_price = neckline_at_breakdown - pattern_height
                potential_drop = ((target_price / current_price) - 1) * 100

                message = "Head and Shoulders pattern detected!\n\n"
                message += f"Left Shoulder: {left_price:.2f}\n"
                message += f"Head: {head_price:.2f}\n"
                message += f"Right Shoulder: {right_price:.2f}\n"
                message += f"Breakdown Price: {breakdown_price:.2f}\n"
                message += f"Pattern Height: {pattern_height:.2f}\n"
                message += f"Current Price: {current_price:.2f}\n"
                message += f"Target Price: {target_price:.2f} (Potential drop: {potential_drop:.2f}%)\n\n"

                message += "Status: " + ("Breakdown confirmed. Bearish signal active." if current_price < breakdown_price else "Awaiting confirmation of breakdown.")

                return message, image_path
            else:
                return "Error generating Head and Shoulders pattern visualization.", None
        else:
            return "No Head and Shoulders pattern detected in the given timeframe.", None
    except Exception as e:
        return f"Error during Head and Shoulders detection: {e}", None