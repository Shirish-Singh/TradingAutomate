import sys
import os
import re
import shutil
import pandas as pd
import numpy as np

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def add_robust_ensure_aligned(file_path):
    """
    Add a more robust ensure_aligned function to the file.
    
    Args:
        file_path: Path to the algorithm file
    """
    filename = os.path.basename(file_path)
    print(f"Adding robust ensure_aligned to {filename}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define a more robust ensure_aligned function
    ensure_aligned_func = """def ensure_aligned(left, right):
    \"\"\"
    Ensure two pandas Series or DataFrames are aligned before operations.
    
    Args:
        left: First pandas Series or DataFrame
        right: Second pandas Series or DataFrame
        
    Returns:
        tuple: (aligned_left, aligned_right)
    \"\"\"
    import pandas as pd
    
    # Handle scalar values
    if not isinstance(left, (pd.Series, pd.DataFrame)) or not isinstance(right, (pd.Series, pd.DataFrame)):
        return left, right
        
    # Handle empty Series/DataFrames
    if (isinstance(left, pd.Series) and len(left) == 0) or (isinstance(left, pd.DataFrame) and left.empty):
        return 0.0, right
    if (isinstance(right, pd.Series) and len(right) == 0) or (isinstance(right, pd.DataFrame) and right.empty):
        return left, 0.0
    
    # Align Series/DataFrames
    if hasattr(left, 'align') and hasattr(right, 'align'):
        try:
            # For Series objects, align on index
            if isinstance(left, pd.Series) and isinstance(right, pd.Series):
                left_aligned, right_aligned = left.align(right, axis=0, copy=False)
                return left_aligned, right_aligned
            # For DataFrame objects, align on both axes
            elif isinstance(left, pd.DataFrame) and isinstance(right, pd.DataFrame):
                left_aligned, right_aligned = left.align(right, axis=None, copy=False)
                return left_aligned, right_aligned
            # For mixed types, convert to compatible types
            else:
                # If one is Series and one is DataFrame, convert Series to DataFrame
                if isinstance(left, pd.Series) and isinstance(right, pd.DataFrame):
                    left = pd.DataFrame(left)
                elif isinstance(left, pd.DataFrame) and isinstance(right, pd.Series):
                    right = pd.DataFrame(right)
                left_aligned, right_aligned = left.align(right, axis=None, copy=False)
                return left_aligned, right_aligned
        except Exception as e:
            # If alignment fails, convert to scalar values as a fallback
            if isinstance(left, (pd.Series, pd.DataFrame)):
                left_val = left.iloc[0] if isinstance(left, pd.Series) else left.iloc[0, 0]
            else:
                left_val = left
                
            if isinstance(right, (pd.Series, pd.DataFrame)):
                right_val = right.iloc[0] if isinstance(right, pd.Series) else right.iloc[0, 0]
            else:
                right_val = right
                
            return left_val, right_val
    
    return left, right
"""
    
    # Replace the existing ensure_aligned function with the more robust one
    if "def ensure_aligned" in content:
        pattern = r"def ensure_aligned\(.*?\):.*?return left, right"
        replacement = ensure_aligned_func
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # Add the ensure_aligned function if it doesn't exist
        import_section_end = content.find("\n\n", content.find("import"))
        if import_section_end == -1:
            import_section_end = content.find("\n", content.find("import"))
        
        content = content[:import_section_end + 2] + ensure_aligned_func + "\n\n" + content[import_section_end + 2:]
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_double_bottom_alignment(file_path):
    """Fix alignment issues in DoubleBottom.py"""
    print(f"Fixing alignment issues in DoubleBottom.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all direct comparisons with ensure_aligned calls
    if "low_mask = df_copy['Low'] == df_copy['rolling_min']" in content:
        content = content.replace(
            "low_mask = df_copy['Low'] == df_copy['rolling_min']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['Low'], df_copy['rolling_min'])\n    low_mask = left == right"
        )
    
    # Add proper alignment for all DataFrame operations
    content = re.sub(
        r"(if\s+)(df_copy\['Low'\]\s*==\s*df_copy\['rolling_min'\])",
        r"\1ensure_aligned(df_copy['Low'], df_copy['rolling_min'])[0] == ensure_aligned(df_copy['Low'], df_copy['rolling_min'])[1]",
        content
    )
    
    # Add try-except blocks for DataFrame access
    if "first_low_price = safe_float(df_copy.loc[first_low_idx, 'Low'])" in content:
        content = content.replace(
            "first_low_price = safe_float(df_copy.loc[first_low_idx, 'Low'])",
            "try:\n                first_low_price = safe_float(df_copy.loc[first_low_idx, 'Low'])\n            except:\n                first_low_price = safe_float(df_copy['Low'].iloc[first_low_idx])"
        )
    
    if "second_low_price = safe_float(df_copy.loc[second_low_idx, 'Low'])" in content:
        content = content.replace(
            "second_low_price = safe_float(df_copy.loc[second_low_idx, 'Low'])",
            "try:\n                second_low_price = safe_float(df_copy.loc[second_low_idx, 'Low'])\n            except:\n                second_low_price = safe_float(df_copy['Low'].iloc[second_low_idx])"
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_head_and_shoulders_alignment(file_path):
    """Fix alignment issues in HeadAndShoulder.py"""
    print(f"Fixing alignment issues in HeadAndShoulder.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all direct comparisons with ensure_aligned calls
    if "peak_mask = df_copy['High'] == df_copy['rolling_max']" in content:
        content = content.replace(
            "peak_mask = df_copy['High'] == df_copy['rolling_max']",
            "# Ensure alignment before comparison\n    left, right = ensure_aligned(df_copy['High'], df_copy['rolling_max'])\n    peak_mask = left == right"
        )
    
    # Add proper alignment for all DataFrame operations
    content = re.sub(
        r"(if\s+)(df_copy\['High'\]\s*==\s*df_copy\['rolling_max'\])",
        r"\1ensure_aligned(df_copy['High'], df_copy['rolling_max'])[0] == ensure_aligned(df_copy['High'], df_copy['rolling_max'])[1]",
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_rising_wedge_alignment(file_path):
    """Fix alignment issues in RisingWedge.py"""
    print(f"Fixing alignment issues in RisingWedge.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all direct comparisons with ensure_aligned calls
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
    
    # Add proper alignment for all DataFrame operations
    content = re.sub(
        r"(if\s+)(df_copy\['Low'\]\s*==\s*df_copy\['rolling_min_low'\])",
        r"\1ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])[0] == ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])[1]",
        content
    )
    
    content = re.sub(
        r"(if\s+)(df_copy\['High'\]\s*==\s*df_copy\['rolling_max_high'\])",
        r"\1ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])[0] == ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])[1]",
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_falling_wedge_alignment(file_path):
    """Fix alignment issues in FallingWedge.py"""
    print(f"Fixing alignment issues in FallingWedge.py...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all direct comparisons with ensure_aligned calls
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
    
    # Add proper alignment for all DataFrame operations
    content = re.sub(
        r"(if\s+)(df_copy\['High'\]\s*==\s*df_copy\['rolling_max_high'\])",
        r"\1ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])[0] == ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])[1]",
        content
    )
    
    content = re.sub(
        r"(if\s+)(df_copy\['Low'\]\s*==\s*df_copy\['rolling_min_low'\])",
        r"\1ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])[0] == ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])[1]",
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def apply_final_fixes():
    """Apply final alignment fixes to all algorithm files"""
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    algos_dir = os.path.join(base_dir, 'algos')
    
    # List of files to fix
    files_to_fix = [
        "DoubleBottom.py",
        "HeadAndShoulder.py",
        "RisingWedge.py",
        "FallingWedge.py"
    ]
    
    # Apply fixes to each file
    for filename in files_to_fix:
        file_path = os.path.join(algos_dir, filename)
        
        if os.path.exists(file_path):
            print(f"\nProcessing {filename}...")
            
            # Create a backup of the original file
            backup_path = file_path + ".final_align2_bak"
            shutil.copy2(file_path, backup_path)
            print(f"Created backup at {backup_path}")
            
            try:
                # Add robust ensure_aligned function
                add_robust_ensure_aligned(file_path)
                
                # Fix specific alignment issues based on the file
                if filename == "DoubleBottom.py":
                    fix_double_bottom_alignment(file_path)
                elif filename == "HeadAndShoulder.py":
                    fix_head_and_shoulders_alignment(file_path)
                elif filename == "RisingWedge.py":
                    fix_rising_wedge_alignment(file_path)
                elif filename == "FallingWedge.py":
                    fix_falling_wedge_alignment(file_path)
                
                print(f"Successfully fixed alignment issues in {filename}")
                
            except Exception as e:
                print(f"Error fixing {filename}: {e}")
                # Restore from backup if there was an error
                shutil.copy2(backup_path, file_path)
                print(f"Restored original file from backup")
        else:
            print(f"File {filename} not found in {algos_dir}")

def run_tests():
    """Run tests to verify all fixes"""
    print("\n=== Running tests to verify fixes ===")
    
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    test_script = os.path.join(base_dir, 'tests', 'test_all_patterns.py')
    
    # Run the test script
    import subprocess
    result = subprocess.run(['python', test_script], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors encountered:")
        print(result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    print("=== Applying Final Alignment Fixes ===")
    apply_final_fixes()
    
    # Run tests to verify fixes
    success = run_tests()
    
    if success:
        print("\nAll fixes have been successfully applied and verified!")
    else:
        print("\nFixes applied but some issues may remain. Please check the test results.")
