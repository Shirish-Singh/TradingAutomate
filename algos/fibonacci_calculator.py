
import pandas as pd

def safe_float(value):
    """
    Safely convert a value to float, handling pandas Series objects.
    
    Args:
        value: Value to convert to float, could be a pandas Series, DataFrame, or scalar
        
    Returns:
        float: The converted float value
    """
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
    """
    Ensure two pandas Series or DataFrames are aligned before operations.
    
    Args:
        left: First pandas Series or DataFrame
        right: Second pandas Series or DataFrame
        
    Returns:
        tuple: (aligned_left, aligned_right)
    """
    if hasattr(left, 'align') and hasattr(right, 'align'):
        return left.align(right, axis=0, copy=False)
    return left, right


class FibonacciCalculator:
    """
    A class that handles the calculation of Fibonacci retracement and extension levels for trading charts.
    """

    def __init__(self, df=None):
        """
        Initializes the FibonacciCalculator with a given DataFrame.

        :param df: DataFrame containing financial data with 'High' and 'Low' columns.
        """
        self.df = df if df is not None else pd.DataFrame()

    def calculate_fibonacci_levels(self, swing_low_index, swing_high_index):
        """
        Calculates Fibonacci retracement levels between a swing low and swing high.

        :param swing_low_index: The index of the swing low in the chart pattern.
        :param swing_high_index: The index of the swing high in the chart pattern.
        :return: A dictionary containing Fibonacci retracement levels.
        """
        swing_low_price = self.df['Low'].loc[swing_low_index]
        swing_high_price = self.df['High'].loc[swing_high_index]
        price_range = swing_high_price - swing_low_price

        # Fibonacci retracement levels
        fib_levels = {
            'Fibonacci 0.236 Level': swing_low_price + price_range * 0.236,
            'Fibonacci 0.382 Level': swing_low_price + price_range * 0.382,
            'Fibonacci 0.5 Level': swing_low_price + price_range * 0.5,
            'Fibonacci 0.618 Level': swing_low_price + price_range * 0.618,
            'Fibonacci 0.786 Level': swing_low_price + price_range * 0.786,
        }

        return fib_levels

    def calculate_fibonacci_extensions(self, swing_low_index, swing_high_index, breakout_index):
        """
        Calculates Fibonacci extension levels after a breakout from a pattern.

        :param swing_low_index: The index of the swing low in the chart pattern.
        :param swing_high_index: The index of the swing high in the chart pattern.
        :param breakout_index: The index of the breakout point.
        :return: A dictionary containing Fibonacci extension levels.
        """
        swing_high_price = self.df['High'].loc[swing_high_index]
        swing_low_price = self.df['Low'].loc[swing_low_index]
        breakout_price = self.df['High'].loc[breakout_index]
        price_range = swing_high_price - swing_low_price

        # Fibonacci extension levels
        fib_extensions = {
            'Fibonacci 1.618 Extension': breakout_price + price_range * 1.618,
            'Fibonacci 2.618 Extension': breakout_price + price_range * 2.618,
            'Fibonacci 3.618 Extension': breakout_price + price_range * 3.618,
        }

        return fib_extensions

    def calculate_all_fibonacci_levels(self, swing_low_index, swing_high_index, breakout_index):
        """
        Combines both Fibonacci retracement and extension levels in a single dictionary.

        :param swing_low_index: The index of the swing low in the chart pattern.
        :param swing_high_index: The index of the swing high in the chart pattern.
        :param breakout_index: The index of the breakout point.
        :return: A dictionary containing both Fibonacci retracement and extension levels.
        """
        retracements = self.calculate_fibonacci_levels(swing_low_index, swing_high_index)
        extensions = self.calculate_fibonacci_extensions(swing_low_index, swing_high_index, breakout_index)

        # Combine retracements and extensions into one dictionary
        all_fibonacci_levels = {**retracements, **extensions}
        
        return all_fibonacci_levels
