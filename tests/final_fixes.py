import sys
import os
import re
import shutil
import pandas as pd

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_file_issues(file_path):
    """
    Fix all remaining issues in a file.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Fixing issues in {os.path.basename(file_path)}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Get the filename
    filename = os.path.basename(file_path)
    
    # Fix any remaining safe_safe_float references
    content = content.replace('safe_safe_float', 'safe_float')
    
    # Apply specific fixes based on the file
    if filename == "DoubleBottom.py":
        # Fix alignment issues in the detect_double_bottom function
        detect_pattern_start = content.find("def detect_double_bottom")
        if detect_pattern_start != -1:
            # Add check for required columns
            function_body_start = content.find(":", detect_pattern_start) + 1
            next_line_pos = content.find("\n", function_body_start) + 1
            
            column_check = """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None
        
"""
            # Only add if not already present
            if "required_columns = ['High', 'Low', 'Open', 'Close']" not in content:
                content = content[:next_line_pos] + column_check + content[next_line_pos:]
            
            # Fix specific comparison that causes alignment issues
            if "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i-1]" in content:
                content = content.replace(
                    "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i-1]",
                    "safe_float(df_copy['Low'].iloc[i]) < safe_float(df_copy['Low'].iloc[i-1])"
                )
            
            if "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i+1]" in content:
                content = content.replace(
                    "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i+1]",
                    "safe_float(df_copy['Low'].iloc[i]) < safe_float(df_copy['Low'].iloc[i+1])"
                )
            
            # Fix any DataFrame access that might cause alignment issues
            content = content.replace(
                "between_lows['High'].max()",
                "safe_float(between_lows['High'].max())"
            )
    
    elif filename == "HeadAndShoulder.py":
        # Fix alignment issues in the detect_head_and_shoulders function
        detect_pattern_start = content.find("def detect_head_and_shoulders")
        if detect_pattern_start != -1:
            # Add check for required columns
            function_body_start = content.find(":", detect_pattern_start) + 1
            next_line_pos = content.find("\n", function_body_start) + 1
            
            column_check = """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None, None
        
"""
            # Only add if not already present
            if "required_columns = ['High', 'Low', 'Open', 'Close']" not in content:
                content = content[:next_line_pos] + column_check + content[next_line_pos:]
            
            # Fix specific comparison that causes alignment issues
            if "df_copy['High'].iloc[i] > df_copy['High'].iloc[i-1]" in content:
                content = content.replace(
                    "df_copy['High'].iloc[i] > df_copy['High'].iloc[i-1]",
                    "safe_float(df_copy['High'].iloc[i]) > safe_float(df_copy['High'].iloc[i-1])"
                )
            
            if "df_copy['High'].iloc[i] > df_copy['High'].iloc[i+1]" in content:
                content = content.replace(
                    "df_copy['High'].iloc[i] > df_copy['High'].iloc[i+1]",
                    "safe_float(df_copy['High'].iloc[i]) > safe_float(df_copy['High'].iloc[i+1])"
                )
    
    elif filename == "RisingWedge.py":
        # Fix alignment issues in the detect_rising_wedge function
        detect_pattern_start = content.find("def detect_rising_wedge")
        if detect_pattern_start != -1:
            # Add check for required columns
            function_body_start = content.find(":", detect_pattern_start) + 1
            next_line_pos = content.find("\n", function_body_start) + 1
            
            column_check = """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None
        
"""
            # Only add if not already present
            if "required_columns = ['High', 'Low', 'Open', 'Close']" not in content:
                content = content[:next_line_pos] + column_check + content[next_line_pos:]
            
            # Fix specific comparison that causes alignment issues
            if "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i-1]" in content:
                content = content.replace(
                    "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i-1]",
                    "safe_float(df_copy['Low'].iloc[i]) < safe_float(df_copy['Low'].iloc[i-1])"
                )
            
            if "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i+1]" in content:
                content = content.replace(
                    "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i+1]",
                    "safe_float(df_copy['Low'].iloc[i]) < safe_float(df_copy['Low'].iloc[i+1])"
                )
            
            if "df_copy['High'].iloc[i] > df_copy['High'].iloc[i-1]" in content:
                content = content.replace(
                    "df_copy['High'].iloc[i] > df_copy['High'].iloc[i-1]",
                    "safe_float(df_copy['High'].iloc[i]) > safe_float(df_copy['High'].iloc[i-1])"
                )
            
            if "df_copy['High'].iloc[i] > df_copy['High'].iloc[i+1]" in content:
                content = content.replace(
                    "df_copy['High'].iloc[i] > df_copy['High'].iloc[i+1]",
                    "safe_float(df_copy['High'].iloc[i]) > safe_float(df_copy['High'].iloc[i+1])"
                )
    
    elif filename == "FallingWedge.py":
        # Fix alignment issues in the detect_falling_wedge function
        detect_pattern_start = content.find("def detect_falling_wedge")
        if detect_pattern_start != -1:
            # Add check for required columns
            function_body_start = content.find(":", detect_pattern_start) + 1
            next_line_pos = content.find("\n", function_body_start) + 1
            
            column_check = """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None
        
"""
            # Only add if not already present
            if "required_columns = ['High', 'Low', 'Open', 'Close']" not in content:
                content = content[:next_line_pos] + column_check + content[next_line_pos:]
            
            # Fix specific comparison that causes alignment issues
            if "df_copy['High'].iloc[i] > df_copy['High'].iloc[i-1]" in content:
                content = content.replace(
                    "df_copy['High'].iloc[i] > df_copy['High'].iloc[i-1]",
                    "safe_float(df_copy['High'].iloc[i]) > safe_float(df_copy['High'].iloc[i-1])"
                )
            
            if "df_copy['High'].iloc[i] > df_copy['High'].iloc[i+1]" in content:
                content = content.replace(
                    "df_copy['High'].iloc[i] > df_copy['High'].iloc[i+1]",
                    "safe_float(df_copy['High'].iloc[i]) > safe_float(df_copy['High'].iloc[i+1])"
                )
            
            if "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i-1]" in content:
                content = content.replace(
                    "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i-1]",
                    "safe_float(df_copy['Low'].iloc[i]) < safe_float(df_copy['Low'].iloc[i-1])"
                )
            
            if "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i+1]" in content:
                content = content.replace(
                    "df_copy['Low'].iloc[i] < df_copy['Low'].iloc[i+1]",
                    "safe_float(df_copy['Low'].iloc[i]) < safe_float(df_copy['Low'].iloc[i+1])"
                )
    
    elif filename == "CupAndHandle.py":
        # Fix datetime indexing issue
        if "breakout_section.iloc[j]['Close']" in content:
            content = content.replace(
                "if safe_float(breakout_section.iloc[j]['Close']) > right_rim_price:",
                """if j < len(breakout_section) and safe_float(breakout_section.iloc[j]['Close']) > right_rim_price:"""
            )
        
        # Fix datetime indexing with Series
        if "df_copy.loc[breakout_idx, 'Close']" in content:
            content = content.replace(
                "'breakout_price': safe_float(df_copy.loc[breakout_idx, 'Close']),",
                "'breakout_price': safe_float(df_copy.loc[breakout_idx, 'Close']) if breakout_idx in df_copy.index else 0.0,"
            )
    
    elif filename == "AscendingTriangle.py":
        # Fix 'High' key error
        if "fib_calc.calculate_fibonacci_extensions" in content:
            content = content.replace(
                "fib_calc.calculate_fibonacci_extensions(pattern_low, resistance_level,",
                "fib_calc.calculate_fibonacci_extensions(safe_float(pattern_low), safe_float(resistance_level),"
            )
        
        # Ensure df has required columns
        detect_pattern_start = content.find("def detect_ascending_triangle")
        if detect_pattern_start != -1:
            # Add check for required columns
            function_body_start = content.find(":", detect_pattern_start) + 1
            next_line_pos = content.find("\n", function_body_start) + 1
            
            column_check = """
    # Check if DataFrame has required columns
    required_columns = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_columns):
        return None, None, None, None
        
"""
            # Only add if not already present
            if "required_columns = ['High', 'Low', 'Open', 'Close']" not in content:
                content = content[:next_line_pos] + column_check + content[next_line_pos:]
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_all_files():
    """Fix all remaining issues in all algorithm files"""
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
                fix_file_issues(file_path)
                print(f"Successfully fixed issues in {filename}")
                
            except Exception as e:
                print(f"Error fixing {filename}: {e}")
                # Restore from backup if there was an error
                shutil.copy2(backup_path, file_path)
                print(f"Restored original file from backup")
        else:
            print(f"File {filename} not found in {algos_dir}")

def run_all_tests():
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
    print("=== Applying Final Fixes to Trading Pattern Algorithms ===")
    fix_all_files()
    
    # Run tests to verify fixes
    success = run_all_tests()
    
    if success:
        print("\nAll fixes have been successfully applied and verified!")
    else:
        print("\nFixes applied but some issues may remain. Please check the test results.")
