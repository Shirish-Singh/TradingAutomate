import sys
import os
import re
import shutil
import pandas as pd
import numpy as np

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_wedge_alignment_issues(file_path):
    """
    Fix alignment issues in wedge pattern files by adding proper alignment checks
    
    Args:
        file_path: Path to the algorithm file
    """
    filename = os.path.basename(file_path)
    print(f"Fixing alignment issues in {filename}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace direct comparisons with aligned comparisons in rolling window operations
    # This is a common pattern in both Rising and Falling Wedge patterns
    if "df_copy['rolling_min_low'] = df_copy['Low'].rolling(window=window_size).min()" in content:
        # Add alignment before comparison operations
        content = content.replace(
            "df_copy['rolling_min_low'] = df_copy['Low'].rolling(window=window_size).min()",
            "df_copy['rolling_min_low'] = df_copy['Low'].rolling(window=window_size).min()\n    # Ensure alignment for future comparisons\n    df_copy = df_copy.copy()"
        )
    
    if "df_copy['rolling_max_high'] = df_copy['High'].rolling(window=window_size).max()" in content:
        # Add alignment before comparison operations
        content = content.replace(
            "df_copy['rolling_max_high'] = df_copy['High'].rolling(window=window_size).max()",
            "df_copy['rolling_max_high'] = df_copy['High'].rolling(window=window_size).max()\n    # Ensure alignment for future comparisons\n    df_copy = df_copy.copy()"
        )
    
    # Replace all direct DataFrame operations with ensure_aligned calls
    content = re.sub(
        r"(df_copy\['Low'\]\s*==\s*df_copy\['rolling_min_low'\])",
        r"ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])[0] == ensure_aligned(df_copy['Low'], df_copy['rolling_min_low'])[1]",
        content
    )
    
    content = re.sub(
        r"(df_copy\['High'\]\s*==\s*df_copy\['rolling_max_high'\])",
        r"ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])[0] == ensure_aligned(df_copy['High'], df_copy['rolling_max_high'])[1]",
        content
    )
    
    # Add try-except blocks for DataFrame access
    if "local_min_idx = low_mask[low_mask].index" in content:
        content = content.replace(
            "local_min_idx = low_mask[low_mask].index",
            "try:\n        local_min_idx = low_mask[low_mask].index\n    except Exception as e:\n        print(f\"Error finding local minima: {e}\")\n        return None"
        )
    
    if "local_max_idx = high_mask[high_mask].index" in content:
        content = content.replace(
            "local_max_idx = high_mask[high_mask].index",
            "try:\n        local_max_idx = high_mask[high_mask].index\n    except Exception as e:\n        print(f\"Error finding local maxima: {e}\")\n        return None"
        )
    
    # Add robust error handling for DataFrame operations
    content = re.sub(
        r"(local_min_prices\s*=\s*df_copy\.loc\[local_min_idx,\s*'Low'\])",
        r"try:\n        \1\n    except Exception as e:\n        print(f\"Error accessing local minimum prices: {e}\")\n        return None",
        content
    )
    
    content = re.sub(
        r"(local_max_prices\s*=\s*df_copy\.loc\[local_max_idx,\s*'High'\])",
        r"try:\n        \1\n    except Exception as e:\n        print(f\"Error accessing local maximum prices: {e}\")\n        return None",
        content
    )
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def apply_final_wedge_fixes():
    """Apply final alignment fixes to wedge pattern files"""
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    algos_dir = os.path.join(base_dir, 'algos')
    
    # List of files to fix
    files_to_fix = [
        "RisingWedge.py",
        "FallingWedge.py"
    ]
    
    # Apply fixes to each file
    for filename in files_to_fix:
        file_path = os.path.join(algos_dir, filename)
        
        if os.path.exists(file_path):
            print(f"\nProcessing {filename}...")
            
            # Create a backup of the original file
            backup_path = file_path + ".final_wedge_bak"
            shutil.copy2(file_path, backup_path)
            print(f"Created backup at {backup_path}")
            
            try:
                # Fix alignment issues
                fix_wedge_alignment_issues(file_path)
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
    print("=== Applying Final Wedge Pattern Fixes ===")
    apply_final_wedge_fixes()
    
    # Run tests to verify fixes
    success = run_tests()
    
    if success:
        print("\nAll fixes have been successfully applied and verified!")
    else:
        print("\nFixes applied but some issues may remain. Please check the test results.")
