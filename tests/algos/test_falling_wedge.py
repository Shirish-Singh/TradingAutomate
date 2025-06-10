import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from algos.FallingWedge import invokeFallingWedge, detect_falling_wedge, safe_float
from tests.test_utils import generate_test_data, fetch_test_data, align_dataframes_before_operation

def test_falling_wedge_with_synthetic_data():
    """Test Falling Wedge pattern detection with synthetic data"""
    print("Testing Falling Wedge with synthetic data...")
    
    # Generate synthetic data with a falling wedge pattern
    df = generate_test_data(pattern_type="falling_wedge", length=100)
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'falling_wedge_synthetic.csv'))
    
    # Test the pattern detection
    message, image_path = invokeFallingWedge(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def test_falling_wedge_with_real_data():
    """Test Falling Wedge pattern detection with real market data"""
    print("Testing Falling Wedge with real market data...")
    
    # Fetch real market data
    df = fetch_test_data(ticker="GOOGL", period="1y")
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'falling_wedge_real.csv'))
    
    # Test the pattern detection
    message, image_path = invokeFallingWedge(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def fix_alignment_issues():
    """Fix alignment issues in the Falling Wedge detection algorithm"""
    # Load the original FallingWedge.py file
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../algos/FallingWedge.py'))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add alignment fix to the detect_falling_wedge function
    alignment_fix = """
    # Ensure proper alignment of dataframes before operations
    def align_before_compare(left, right):
        if isinstance(left, pd.Series) and isinstance(right, pd.Series):
            left, right = left.align(right, copy=False)
        return left, right
"""
    
    # Insert the alignment fix after the detect_falling_wedge function definition
    detect_idx = content.find("def detect_falling_wedge")
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
        ("if safe_float(slope_upper) >= safe_float(slope_lower):", "slope_upper_val, slope_lower_val = align_before_compare(safe_float(slope_upper), safe_float(slope_lower))\n    if slope_upper_val >= slope_lower_val:"),
        ("if current_close > projected_upper_trendline:", "current_close, projected_upper_trendline = align_before_compare(current_close, projected_upper_trendline)\n            if current_close > projected_upper_trendline:"),
        ("x_pos = df_copy.index.get_loc(idx)", "x_pos = float(df_copy.index.get_loc(idx))"),
        ("position_ratio = (breakdown_point - left_shoulder)", "position_ratio = float(breakdown_point - left_shoulder)"),
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
        synthetic_result = test_falling_wedge_with_synthetic_data()
    except Exception as e:
        print(f"Error with synthetic data: {e}")
        # If there's an error, fix the alignment issues
        fixed_file = fix_alignment_issues()
        print(f"Please review and replace the original file with {fixed_file}")
    
    try:
        real_result = test_falling_wedge_with_real_data()
    except Exception as e:
        print(f"Error with real data: {e}")
        # If there's an error, fix the alignment issues
        fixed_file = fix_alignment_issues()
        print(f"Please review and replace the original file with {fixed_file}")
