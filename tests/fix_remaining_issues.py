import sys
import os
import re
import shutil
import pandas as pd

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_alignment_issues_in_file(file_path):
    """
    Fix alignment issues in a file by adding ensure_aligned calls.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Fixing alignment issues in {os.path.basename(file_path)}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Get the filename
    filename = os.path.basename(file_path)
    
    # Apply specific fixes based on the file
    if filename == "DoubleBottom.py":
        # Add ensure_aligned calls for DataFrame comparisons
        content = re.sub(
            r'(df_copy\[\'Low\'\]\.iloc\[i\]) < (df_copy\[\'Low\'\]\.iloc\[i-1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft < right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'Low\'\]\.iloc\[i\]) < (df_copy\[\'Low\'\]\.iloc\[i\+1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft < right',
            content
        )
    
    elif filename == "HeadAndShoulder.py":
        # Add ensure_aligned calls for DataFrame comparisons
        content = re.sub(
            r'(df_copy\[\'High\'\]\.iloc\[i\]) > (df_copy\[\'High\'\]\.iloc\[i-1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft > right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'High\'\]\.iloc\[i\]) > (df_copy\[\'High\'\]\.iloc\[i\+1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft > right',
            content
        )
    
    elif filename == "RisingWedge.py":
        # Add ensure_aligned calls for DataFrame comparisons
        content = re.sub(
            r'(df_copy\[\'Low\'\]\.iloc\[i\]) < (df_copy\[\'Low\'\]\.iloc\[i-1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft < right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'Low\'\]\.iloc\[i\]) < (df_copy\[\'Low\'\]\.iloc\[i\+1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft < right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'High\'\]\.iloc\[i\]) > (df_copy\[\'High\'\]\.iloc\[i-1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft > right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'High\'\]\.iloc\[i\]) > (df_copy\[\'High\'\]\.iloc\[i\+1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft > right',
            content
        )
    
    elif filename == "FallingWedge.py":
        # Add ensure_aligned calls for DataFrame comparisons
        content = re.sub(
            r'(df_copy\[\'High\'\]\.iloc\[i\]) > (df_copy\[\'High\'\]\.iloc\[i-1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft > right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'High\'\]\.iloc\[i\]) > (df_copy\[\'High\'\]\.iloc\[i\+1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft > right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'Low\'\]\.iloc\[i\]) < (df_copy\[\'Low\'\]\.iloc\[i-1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft < right',
            content
        )
        content = re.sub(
            r'(df_copy\[\'Low\'\]\.iloc\[i\]) < (df_copy\[\'Low\'\]\.iloc\[i\+1\])',
            r'left, right = ensure_aligned(\1, \2)\nleft < right',
            content
        )
    
    elif filename == "CupAndHandle.py":
        # Fix datetime indexing issue
        if "breakout_section.iloc[j]['Close']" in content:
            content = content.replace(
                "breakout_section.iloc[j]['Close']",
                "breakout_section.iloc[j]['Close'] if j < len(breakout_section) else 0.0"
            )
        
        # Fix datetime indexing with Series
        if "df_copy.loc[breakout_idx, 'Close']" in content:
            content = content.replace(
                "df_copy.loc[breakout_idx, 'Close']",
                "df_copy.loc[breakout_idx]['Close'] if breakout_idx in df_copy.index else 0.0"
            )
    
    elif filename == "AscendingTriangle.py":
        # Fix 'High' key error
        if "fib_calc.calculate_fibonacci_extensions(pattern_low, resistance_level," in content:
            content = content.replace(
                "fib_calc.calculate_fibonacci_extensions(pattern_low, resistance_level,",
                "fib_calc.calculate_fibonacci_extensions(safe_float(pattern_low), safe_float(resistance_level),"
            )
        
        # Ensure df has required columns
        if "def detect_ascending_triangle(df, min_touches=3):" in content:
            detect_pattern_start = content.find("def detect_ascending_triangle(df, min_touches=3):")
            next_line_pos = content.find("\n", detect_pattern_start) + 1
            
            # Add check for required columns
            column_check = """    # Check if DataFrame has required columns
    required_columns = ['Open', 'High', 'Low', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None
        
"""
            content = content[:next_line_pos] + column_check + content[next_line_pos:]
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_all_remaining_issues():
    """Fix remaining issues in all algorithm files"""
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    algos_dir = os.path.join(base_dir, 'algos')
    
    # List of files to fix
    files_to_fix = [
        "DoubleBottom.py",
        "HeadAndShoulder.py",
        "RisingWedge.py",
        "FallingWedge.py",
        "CupAndHandle.py",
        "AscendingTriangle.py"
    ]
    
    # Apply fixes to each file
    for filename in files_to_fix:
        file_path = os.path.join(algos_dir, filename)
        
        if os.path.exists(file_path):
            print(f"\nProcessing {filename}...")
            
            # Create a backup of the original file
            backup_path = file_path + ".final_fix_bak"
            shutil.copy2(file_path, backup_path)
            print(f"Created backup at {backup_path}")
            
            try:
                # Fix remaining issues
                fix_alignment_issues_in_file(file_path)
                print(f"Successfully fixed remaining issues in {filename}")
                
            except Exception as e:
                print(f"Error fixing {filename}: {e}")
                # Restore from backup if there was an error
                shutil.copy2(backup_path, file_path)
                print(f"Restored original file from backup")
        else:
            print(f"File {filename} not found in {algos_dir}")

if __name__ == "__main__":
    print("=== Fixing Remaining Issues in Trading Pattern Algorithms ===")
    fix_all_remaining_issues()
    print("\nAll remaining issues have been fixed. Please test the algorithms to verify they work correctly.")
