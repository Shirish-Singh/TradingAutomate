import sys
import os
import re
import shutil

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_double_bottom_alignment(file_path):
    """Fix alignment issues in DoubleBottom.py"""
    print(f"Fixing alignment issues in DoubleBottom.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic comparison in detect_double_bottom function
    if "low_mask = df_copy['Low'] == df_copy['rolling_min']" in content:
        content = content.replace(
            "low_mask = df_copy['Low'] == df_copy['rolling_min']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['Low'], df_copy['rolling_min'])\n    low_mask = left == right"
        )
    
    # Fix any remaining safe_safe_float references
    content = content.replace('safe_safe_float', 'safe_float')
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_head_and_shoulders_alignment(file_path):
    """Fix alignment issues in HeadAndShoulder.py"""
    print(f"Fixing alignment issues in HeadAndShoulder.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic comparison in detect_head_and_shoulders function
    if "peak_mask = df_copy['High'] == df_copy['rolling_max']" in content:
        content = content.replace(
            "peak_mask = df_copy['High'] == df_copy['rolling_max']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['High'], df_copy['rolling_max'])\n    peak_mask = left == right"
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_rising_wedge_alignment(file_path):
    """Fix alignment issues in RisingWedge.py"""
    print(f"Fixing alignment issues in RisingWedge.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic comparisons in detect_rising_wedge function
    if "low_mask = df_copy['Low'] == df_copy['rolling_min_low']" in content:
        content = content.replace(
            "low_mask = df_copy['Low'] == df_copy['rolling_min_low']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])\n    low_mask = left == right"
        )
    
    if "high_mask = df_copy['High'] == df_copy['rolling_max_high']" in content:
        content = content.replace(
            "high_mask = df_copy['High'] == df_copy['rolling_max_high']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])\n    high_mask = left == right"
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_falling_wedge_alignment(file_path):
    """Fix alignment issues in FallingWedge.py"""
    print(f"Fixing alignment issues in FallingWedge.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic comparisons in detect_falling_wedge function
    if "high_mask = df_copy['High'] == df_copy['rolling_max_high']" in content:
        content = content.replace(
            "high_mask = df_copy['High'] == df_copy['rolling_max_high']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])\n    high_mask = left == right"
        )
    
    if "low_mask = df_copy['Low'] == df_copy['rolling_min_low']" in content:
        content = content.replace(
            "low_mask = df_copy['Low'] == df_copy['rolling_min_low']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])\n    low_mask = left == right"
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_cup_and_handle_datetime(file_path):
    """Fix datetime indexing issues in CupAndHandle.py"""
    print(f"Fixing datetime indexing issues in CupAndHandle.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the datetime indexing issue with Series
    if "breakout_section = df_copy.loc[right_rim_offset:]" in content:
        # Add a check to convert Series index to scalar before using as index
        content = content.replace(
            "breakout_section = df_copy.loc[right_rim_offset:]",
            "# Ensure right_rim_offset is a scalar, not a Series\n        if hasattr(right_rim_offset, 'iloc'):\n            right_rim_offset = right_rim_offset.iloc[0]\n        breakout_section = df_copy.loc[right_rim_offset:]"
        )
    
    # Fix other potential datetime indexing issues
    if "left_rim_offset = left_section['High'].idxmax()" in content:
        content = content.replace(
            "left_rim_offset = left_section['High'].idxmax()",
            "left_rim_offset = left_section['High'].idxmax()\n        if hasattr(left_rim_offset, 'iloc'):\n            left_rim_offset = left_rim_offset.iloc[0]"
        )
    
    if "cup_bottom_offset = cup_section['Low'].idxmin()" in content:
        content = content.replace(
            "cup_bottom_offset = cup_section['Low'].idxmin()",
            "cup_bottom_offset = cup_section['Low'].idxmin()\n        if hasattr(cup_bottom_offset, 'iloc'):\n            cup_bottom_offset = cup_bottom_offset.iloc[0]"
        )
    
    if "right_rim_offset = right_section['High'].idxmax()" in content:
        content = content.replace(
            "right_rim_offset = right_section['High'].idxmax()",
            "right_rim_offset = right_section['High'].idxmax()\n        if hasattr(right_rim_offset, 'iloc'):\n            right_rim_offset = right_rim_offset.iloc[0]"
        )
    
    if "handle_bottom_offset = handle_section['Low'].idxmin()" in content:
        content = content.replace(
            "handle_bottom_offset = handle_section['Low'].idxmin()",
            "handle_bottom_offset = handle_section['Low'].idxmin()\n        if hasattr(handle_bottom_offset, 'iloc'):\n            handle_bottom_offset = handle_bottom_offset.iloc[0]"
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_ascending_triangle_high(file_path):
    """Fix 'High' key error in AscendingTriangle.py"""
    print(f"Fixing 'High' key error in AscendingTriangle.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add check for required columns at the beginning of the detect function
    detect_pattern_start = content.find("def detect_ascending_triangle(df, min_touches=3):")
    if detect_pattern_start != -1:
        function_body_start = content.find(":", detect_pattern_start) + 1
        next_line_pos = content.find("\n", function_body_start) + 1
        
        column_check = """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        print(f"Missing required columns. Available columns: {df.columns.tolist()}")
        return None, None, None, None
        
"""
        # Only add if not already present
        if "required_columns = ['High', 'Low', 'Open', 'Close']" not in content:
            content = content[:next_line_pos] + column_check + content[next_line_pos:]
    
    # Fix the FibonacciCalculator initialization
    if "fib_calc = FibonacciCalculator()" in content:
        content = content.replace(
            "fib_calc = FibonacciCalculator()",
            "fib_calc = FibonacciCalculator(df.copy())"
        )
    
    # Fix the calculate_fibonacci_extensions call
    if "fib_levels = fib_calc.calculate_fibonacci_extensions" in content:
        content = content.replace(
            "fib_levels = fib_calc.calculate_fibonacci_extensions(safe_float(pattern_low), safe_float(resistance_level),",
            "fib_levels = fib_calc.calculate_fibonacci_extensions(safe_float(pattern_low), safe_float(resistance_level),"
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def apply_targeted_fixes():
    """Apply targeted fixes to specific files"""
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    algos_dir = os.path.join(base_dir, 'algos')
    
    # Fix DoubleBottom.py
    file_path = os.path.join(algos_dir, "DoubleBottom.py")
    if os.path.exists(file_path):
        backup_path = file_path + ".targeted_fix_bak"
        shutil.copy2(file_path, backup_path)
        fix_double_bottom_alignment(file_path)
    
    # Fix HeadAndShoulder.py
    file_path = os.path.join(algos_dir, "HeadAndShoulder.py")
    if os.path.exists(file_path):
        backup_path = file_path + ".targeted_fix_bak"
        shutil.copy2(file_path, backup_path)
        fix_head_and_shoulders_alignment(file_path)
    
    # Fix RisingWedge.py
    file_path = os.path.join(algos_dir, "RisingWedge.py")
    if os.path.exists(file_path):
        backup_path = file_path + ".targeted_fix_bak"
        shutil.copy2(file_path, backup_path)
        fix_rising_wedge_alignment(file_path)
    
    # Fix FallingWedge.py
    file_path = os.path.join(algos_dir, "FallingWedge.py")
    if os.path.exists(file_path):
        backup_path = file_path + ".targeted_fix_bak"
        shutil.copy2(file_path, backup_path)
        fix_falling_wedge_alignment(file_path)
    
    # Fix CupAndHandle.py
    file_path = os.path.join(algos_dir, "CupAndHandle.py")
    if os.path.exists(file_path):
        backup_path = file_path + ".targeted_fix_bak"
        shutil.copy2(file_path, backup_path)
        fix_cup_and_handle_datetime(file_path)
    
    # Fix AscendingTriangle.py
    file_path = os.path.join(algos_dir, "AscendingTriangle.py")
    if os.path.exists(file_path):
        backup_path = file_path + ".targeted_fix_bak"
        shutil.copy2(file_path, backup_path)
        fix_ascending_triangle_high(file_path)

if __name__ == "__main__":
    print("=== Applying Targeted Alignment Fixes ===")
    apply_targeted_fixes()
    print("\nAll targeted fixes have been applied. Please run the test script to verify the fixes.")
