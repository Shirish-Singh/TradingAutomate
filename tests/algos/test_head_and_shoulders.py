import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from algos.HeadAndShoulder import invokeHeadAndShoulders, detect_head_and_shoulders, safe_float
from tests.test_utils import generate_test_data, fetch_test_data, align_dataframes_before_operation

def test_head_and_shoulders_with_synthetic_data():
    """Test Head and Shoulders pattern detection with synthetic data"""
    print("Testing Head and Shoulders with synthetic data...")
    
    # Generate synthetic data with a head and shoulders pattern
    df = generate_test_data(pattern_type="head_and_shoulders", length=100)
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'head_and_shoulders_synthetic.csv'))
    
    # Test the pattern detection
    message, image_path = invokeHeadAndShoulders(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def test_head_and_shoulders_with_real_data():
    """Test Head and Shoulders pattern detection with real market data"""
    print("Testing Head and Shoulders with real market data...")
    
    # Fetch real market data
    df = fetch_test_data(ticker="MSFT", period="1y")
    
    # Save the test data for reference
    test_data_dir = os.path.join(os.path.dirname(__file__), '../test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    df.to_csv(os.path.join(test_data_dir, 'head_and_shoulders_real.csv'))
    
    # Test the pattern detection
    message, image_path = invokeHeadAndShoulders(df)
    
    print(f"Result: {message}")
    print(f"Image: {image_path}")
    
    return message, image_path

def fix_alignment_issues():
    """Fix alignment issues in the Head and Shoulders detection algorithm"""
    # Load the original HeadAndShoulder.py file
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../algos/HeadAndShoulder.py'))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add alignment fix to the detect_head_and_shoulders function
    alignment_fix = """
    # Ensure proper alignment of dataframes before operations
    def align_before_compare(left, right):
        if isinstance(left, pd.Series) and isinstance(right, pd.Series):
            left, right = left.align(right, copy=False)
        return left, right
"""
    
    # Insert the alignment fix after the detect_head_and_shoulders function definition
    detect_idx = content.find("def detect_head_and_shoulders")
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
        ("head_price > left_shoulder_price", "head_price, left_shoulder_price = align_before_compare(head_price, left_shoulder_price)\n            if head_price > left_shoulder_price"),
        ("head_price > right_shoulder_price", "head_price, right_shoulder_price = align_before_compare(head_price, right_shoulder_price)\n            if head_price > right_shoulder_price"),
        ("current_low < neckline_price", "current_low, neckline_price = align_before_compare(current_low, neckline_price)\n                if current_low < neckline_price"),
        ("position_ratio = (idx - left_trough_idx)", "position_ratio = float(idx - left_trough_idx)"),
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
        synthetic_result = test_head_and_shoulders_with_synthetic_data()
    except Exception as e:
        print(f"Error with synthetic data: {e}")
        # If there's an error, fix the alignment issues
        fixed_file = fix_alignment_issues()
        print(f"Please review and replace the original file with {fixed_file}")
    
    try:
        real_result = test_head_and_shoulders_with_real_data()
    except Exception as e:
        print(f"Error with real data: {e}")
        # If there's an error, fix the alignment issues
        fixed_file = fix_alignment_issues()
        print(f"Please review and replace the original file with {fixed_file}")
