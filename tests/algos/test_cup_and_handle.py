import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from algos.CupAndHandle import invokeCupAndHandle, detect_cup_and_handle, safe_float
from tests.test_utils import generate_test_data, fetch_test_data, align_dataframes_before_operation

def test_cup_and_handle_with_synthetic_data():
    """Test Cup and Handle pattern detection with synthetic data"""
    print("Testing Cup and Handle with synthetic data...")
    
    # Generate synthetic data with a cup and handle pattern
    df = generate_test_data(pattern_type="cup_and_handle", length=100)
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'cup_and_handle_synthetic.csv'))
    
    # Test the pattern detection
    message, image_path = invokeCupAndHandle(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def test_cup_and_handle_with_real_data():
    """Test Cup and Handle pattern detection with real market data"""
    print("Testing Cup and Handle with real market data...")
    
    # Fetch real market data
    df = fetch_test_data(ticker="NVDA", period="1y")
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'cup_and_handle_real.csv'))
    
    # Test the pattern detection
    message, image_path = invokeCupAndHandle(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def fix_datetime_indexing_issues():
    """Fix datetime indexing issues in the Cup and Handle detection algorithm"""
    # Load the original CupAndHandle.py file
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../algos/CupAndHandle.py'))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update the safe_float function to handle DatetimeIndex issues
    updated_safe_float = """def safe_float(value):
    \"\"\"
    Safely convert a value to float, handling pandas Series objects.
    
    Args:
        value: Value to convert to float, could be a pandas Series or scalar
        
    Returns:
        float: The converted float value
    \"\"\"
    if isinstance(value, pd.Series):
        # Handle Series with DatetimeIndex
        if pd.api.types.is_datetime64_any_dtype(value.dtype):
            return float(value.iloc[0].timestamp())
        return float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        # Handle DataFrame case - extract first value
        return float(value.iloc[0, 0])
    elif pd.api.types.is_datetime64_any_dtype(type(value)):
        # Handle datetime directly
        return float(pd.Timestamp(value).timestamp())
    return float(value)
"""
    
    # Replace the old safe_float function with the updated one
    if "def safe_float" in content:
        start_idx = content.find("def safe_float")
        end_idx = content.find("def detect_cup_and_handle")
        if start_idx != -1 and end_idx != -1:
            content = content[:start_idx] + updated_safe_float + content[end_idx:]
    
    # Fix specific datetime indexing issues in the detection logic
    fixes = [
        # Fix the datetime indexing issue in the slice operation
        ("cup_section = df_copy.loc[left_idx:right_idx]", "cup_section = df_copy.loc[pd.Timestamp(left_idx):pd.Timestamp(right_idx)] if isinstance(left_idx, pd.Timestamp) else df_copy.loc[left_idx:right_idx]"),
        ("handle_section = df_copy.loc[right_idx:handle_end]", "handle_section = df_copy.loc[pd.Timestamp(right_idx):pd.Timestamp(handle_end)] if isinstance(right_idx, pd.Timestamp) else df_copy.loc[right_idx:handle_end]"),
        # Fix the datetime comparison issue
        ("if idx > handle_end:", "if pd.Timestamp(idx) > pd.Timestamp(handle_end) if isinstance(handle_end, pd.Timestamp) else idx > handle_end:"),
        # Add explicit conversion for datetime indices
        ("handle_low_idx = handle_section['Low'].idxmin()", "handle_low_idx = pd.Timestamp(handle_section['Low'].idxmin()) if pd.api.types.is_datetime64_any_dtype(handle_section.index.dtype) else handle_section['Low'].idxmin()"),
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Add helper function to handle datetime indices
    datetime_helper = """
    def ensure_compatible_index(idx, df):
        \"\"\"Ensure index is compatible with dataframe for slicing\"\"\"
        if pd.api.types.is_datetime64_any_dtype(df.index.dtype):
            if not isinstance(idx, pd.Timestamp):
                try:
                    return pd.Timestamp(idx)
                except:
                    return idx
        return idx
"""
    
    # Insert the datetime helper after the detect_cup_and_handle function definition
    detect_idx = content.find("def detect_cup_and_handle")
    if detect_idx != -1:
        # Find the end of the function signature
        sig_end = content.find(":", detect_idx)
        if sig_end != -1:
            # Insert after the first line of the function
            next_line_end = content.find("\n", sig_end)
            if next_line_end != -1:
                content = content[:next_line_end+1] + datetime_helper + content[next_line_end+1:]
    
    # Write the updated content back to the file
    with open(file_path + '.fixed', 'w') as f:
        f.write(content)
    
    print(f"Fixed version written to {file_path}.fixed")
    
    return file_path + '.fixed'

if __name__ == "__main__":
    # First run tests to see if there are issues
    try:
        synthetic_result = test_cup_and_handle_with_synthetic_data()
    except Exception as e:
        print(f"Error with synthetic data: {e}")
        # If there's an error, fix the datetime indexing issues
        fixed_file = fix_datetime_indexing_issues()
        print(f"Please review and replace the original file with {fixed_file}")
    
    try:
        real_result = test_cup_and_handle_with_real_data()
    except Exception as e:
        print(f"Error with real data: {e}")
        # If there's an error, fix the datetime indexing issues
        fixed_file = fix_datetime_indexing_issues()
        print(f"Please review and replace the original file with {fixed_file}")
