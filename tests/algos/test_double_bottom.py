import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from algos.DoubleBottom import invokeDoubleBottom, detect_double_bottom, safe_float
from tests.test_utils import generate_test_data, fetch_test_data, align_dataframes_before_operation

def test_double_bottom_with_synthetic_data():
    """Test Double Bottom pattern detection with synthetic data"""
    print("Testing Double Bottom with synthetic data...")
    
    # Generate synthetic data with a double bottom pattern
    df = generate_test_data(pattern_type="double_bottom", length=100)
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'double_bottom_synthetic.csv'))
    
    # Test the pattern detection
    message, image_path = invokeDoubleBottom(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def test_double_bottom_with_real_data():
    """Test Double Bottom pattern detection with real market data"""
    print("Testing Double Bottom with real market data...")
    
    # Fetch real market data
    df = fetch_test_data(ticker="AAPL", period="1y")
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'double_bottom_real.csv'))
    
    # Test the pattern detection
    message, image_path = invokeDoubleBottom(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def fix_alignment_issues():
    """Fix alignment issues in the Double Bottom detection algorithm"""
    # Load the original DoubleBottom.py file
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../algos/DoubleBottom.py'))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update the safe_float function to handle DataFrame case
    updated_safe_float = """def safe_float(value):
    \"\"\"
    Safely convert a value to float, handling pandas Series objects.
    
    Args:
        value: Value to convert to float, could be a pandas Series or scalar
        
    Returns:
        float: The converted float value
    \"\"\"
    if isinstance(value, pd.Series):
        return float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        # Handle DataFrame case - extract first value
        return float(value.iloc[0, 0])
    return float(value)
"""
    
    # Replace the old safe_float function with the updated one
    if "def safe_float" in content:
        start_idx = content.find("def safe_float")
        end_idx = content.find("def detect_double_bottom")
        if start_idx != -1 and end_idx != -1:
            content = content[:start_idx] + updated_safe_float + content[end_idx:]
    
    # Add alignment fix to the detect_double_bottom function
    alignment_fix = """
    # Ensure proper alignment of dataframes before operations
    def align_before_compare(left, right):
        if isinstance(left, pd.Series) and isinstance(right, pd.Series):
            left, right = left.align(right, copy=False)
        return left, right
"""
    
    # Insert the alignment fix after the detect_double_bottom function definition
    detect_idx = content.find("def detect_double_bottom")
    if detect_idx != -1:
        # Find the end of the function signature
        sig_end = content.find(":", detect_idx)
        if sig_end != -1:
            # Insert after the first line of the function
            next_line_end = content.find("\n", sig_end)
            if next_line_end != -1:
                content = content[:next_line_end+1] + alignment_fix + content[next_line_end+1:]
    
    # Fix specific alignment issues in the detection logic
    # Look for comparison operations that might need alignment
    fixes = [
        ("current_low < first_bottom_price", "current_low, first_bottom_price = align_before_compare(current_low, first_bottom_price)\n        if current_low < first_bottom_price"),
        ("current_low < neckline_price", "current_low, neckline_price = align_before_compare(current_low, neckline_price)\n        if current_low < neckline_price"),
        ("between_bottoms['Low'].min()", "between_bottoms['Low'].min() if not between_bottoms.empty else float('inf')"),
        ("df_copy['Low'].iloc[i]", "safe_float(df_copy['Low'].iloc[i])"),
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Write the updated content back to the file
    with open(file_path + '.fixed', 'w') as f:
        f.write(content)
    
    print(f"Fixed version written to {file_path}.fixed")
    
    return file_path + '.fixed'

if __name__ == "__main__":
    # First run tests to see if there are issues
    try:
        synthetic_result = test_double_bottom_with_synthetic_data()
    except Exception as e:
        print(f"Error with synthetic data: {e}")
        # If there's an error, fix the alignment issues
        fixed_file = fix_alignment_issues()
        print(f"Please review and replace the original file with {fixed_file}")
    
    try:
        real_result = test_double_bottom_with_real_data()
    except Exception as e:
        print(f"Error with real data: {e}")
        # If there's an error, fix the alignment issues
        fixed_file = fix_alignment_issues()
        print(f"Please review and replace the original file with {fixed_file}")
