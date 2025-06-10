import sys
import os
import pandas as pd
import numpy as np
import shutil

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def update_safe_float_function(file_path):
    """
    Update the safe_float function in a file to handle all edge cases.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Updating safe_float function in {file_path}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define the improved safe_float function
    improved_safe_float = """def safe_float(value):
    \"\"\"
    Safely convert a value to float, handling pandas Series objects.
    
    Args:
        value: Value to convert to float, could be a pandas Series, DataFrame, or scalar
        
    Returns:
        float: The converted float value
    \"\"\"
    if isinstance(value, pd.Series):
        if len(value) == 0:
            return 0.0
        # Handle Series with DatetimeIndex
        if pd.api.types.is_datetime64_any_dtype(value.dtype):
            return float(value.iloc[0].timestamp())
        return float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        # Handle DataFrame case - extract first value
        if value.empty:
            return 0.0
        return float(value.iloc[0, 0])
    elif pd.api.types.is_datetime64_any_dtype(type(value)):
        # Handle datetime directly
        return float(pd.Timestamp(value).timestamp())
    return float(value)
"""
    
    # Check if the file already has a safe_float function
    if "def safe_float" in content:
        # Replace the existing safe_float function
        start_idx = content.find("def safe_float")
        # Find the end of the safe_float function (start of the next function)
        next_func_pattern = "def "
        next_func_idx = content.find(next_func_pattern, start_idx + len("def safe_float"))
        if next_func_idx != -1:
            # Replace the function
            content = content[:start_idx] + improved_safe_float + content[next_func_idx:]
        else:
            # If we can't find the next function, just add the improved function at the top
            content = improved_safe_float + "\n\n" + content
    else:
        # Add the safe_float function at the beginning after imports
        import_end = 0
        import_keywords = ["import ", "from "]
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in import_keywords):
                import_end = i
        
        # Insert after the last import
        if import_end > 0:
            lines.insert(import_end + 1, "")
            lines.insert(import_end + 2, improved_safe_float)
            content = "\n".join(lines)
        else:
            # If no imports found, add at the beginning
            content = improved_safe_float + "\n\n" + content
    
    # Write the updated content back to a temporary file
    temp_file = file_path + ".new"
    with open(temp_file, 'w') as f:
        f.write(content)
    
    return temp_file

def add_alignment_helper(file_path):
    """
    Add alignment helper function to a file.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Adding alignment helper to {file_path}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define the alignment helper function
    alignment_helper = """
def align_before_compare(left, right):
    \"\"\"
    Align two dataframes or series before performing operations between them.
    
    Args:
        left: Left DataFrame or Series
        right: Right DataFrame or Series
        
    Returns:
        tuple: Aligned left and right objects
    \"\"\"
    if isinstance(left, pd.Series) and isinstance(right, pd.Series):
        left, right = left.align(right, copy=False)
    return left, right
"""
    
    # Check if the file already has the alignment helper
    if "def align_before_compare" not in content:
        # Find the first function definition
        first_func_idx = content.find("def ")
        if first_func_idx != -1:
            # Insert before the first function
            content = content[:first_func_idx] + alignment_helper + "\n" + content[first_func_idx:]
        else:
            # If no function found, add at the end
            content += "\n\n" + alignment_helper
    
    # Write the updated content back to a temporary file
    temp_file = file_path + ".aligned"
    with open(temp_file, 'w') as f:
        f.write(content)
    
    return temp_file

def fix_datetime_indexing(file_path):
    """
    Fix datetime indexing issues in a file.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Fixing datetime indexing in {file_path}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define the datetime helper function
    datetime_helper = """
def ensure_compatible_index(idx, df):
    \"\"\"
    Ensure index is compatible with dataframe for slicing.
    
    Args:
        idx: Index value
        df: DataFrame to check against
        
    Returns:
        Compatible index value
    \"\"\"
    if pd.api.types.is_datetime64_any_dtype(df.index.dtype):
        if not isinstance(idx, pd.Timestamp):
            try:
                return pd.Timestamp(idx)
            except:
                return idx
    return idx
"""
    
    # Check if the file already has the datetime helper
    if "def ensure_compatible_index" not in content:
        # Find the first function definition
        first_func_idx = content.find("def ")
        if first_func_idx != -1:
            # Insert before the first function
            content = content[:first_func_idx] + datetime_helper + "\n" + content[first_func_idx:]
        else:
            # If no function found, add at the end
            content += "\n\n" + datetime_helper
    
    # Fix specific datetime indexing issues
    fixes = [
        # Fix slice operations with potential datetime indices
        ("df_copy.loc[", "df_copy.loc[ensure_compatible_index("),
        (".loc[", ".loc[ensure_compatible_index("),
        ("]", "], df_copy)"),
        # Fix the above over-replacement
        ("ensure_compatible_index(ensure_compatible_index(", "ensure_compatible_index("),
        ("), df_copy)), df_copy)", "), df_copy)"),
    ]
    
    # Only apply the first two fixes to avoid over-replacement
    for old, new in fixes[:2]:
        content = content.replace(old, new)
    
    # Write the updated content back to a temporary file
    temp_file = file_path + ".datetime_fixed"
    with open(temp_file, 'w') as f:
        f.write(content)
    
    return temp_file

def fix_empty_dataframe_checks(file_path):
    """
    Add empty DataFrame checks to prevent errors.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Adding empty DataFrame checks to {file_path}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix specific empty DataFrame issues
    fixes = [
        # Add empty checks for min/max operations
        ("['Low'].min()", "['Low'].min() if not between_peaks.empty else float('inf')"),
        ("['High'].max()", "['High'].max() if not between_peaks.empty else float('-inf')"),
        # Add empty checks for idxmin/idxmax operations
        ("['Low'].idxmin()", "['Low'].idxmin() if not between_peaks.empty else None"),
        ("['High'].idxmax()", "['High'].idxmax() if not between_peaks.empty else None"),
    ]
    
    # Apply fixes with care to avoid over-replacement
    for old, new in fixes:
        if old in content and "if not" not in old:
            content = content.replace(old, new)
    
    # Write the updated content back to a temporary file
    temp_file = file_path + ".empty_fixed"
    with open(temp_file, 'w') as f:
        f.write(content)
    
    return temp_file

def apply_fixes_to_all_algorithms():
    """Apply fixes to all algorithm files"""
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    algos_dir = os.path.join(base_dir, 'algos')
    
    # Get all Python files in the algos directory
    algo_files = [os.path.join(algos_dir, f) for f in os.listdir(algos_dir) 
                 if f.endswith('.py') and not f.startswith('__')]
    
    print(f"Found {len(algo_files)} algorithm files to fix.")
    
    # Apply fixes to each file
    for file_path in algo_files:
        print(f"\nProcessing {os.path.basename(file_path)}...")
        
        # Create a backup of the original file
        backup_path = file_path + ".bak"
        shutil.copy2(file_path, backup_path)
        print(f"Created backup at {backup_path}")
        
        # Apply fixes in sequence
        try:
            # Update safe_float function
            temp_file1 = update_safe_float_function(file_path)
            
            # Add alignment helper
            temp_file2 = add_alignment_helper(temp_file1)
            
            # Fix datetime indexing
            temp_file3 = fix_datetime_indexing(temp_file2)
            
            # Fix empty DataFrame checks
            temp_file4 = fix_empty_dataframe_checks(temp_file3)
            
            # Replace the original file with the fixed version
            shutil.copy2(temp_file4, file_path)
            print(f"Successfully applied fixes to {os.path.basename(file_path)}")
            
            # Clean up temporary files
            for temp_file in [temp_file1, temp_file2, temp_file3, temp_file4]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        except Exception as e:
            print(f"Error fixing {os.path.basename(file_path)}: {e}")
            # Restore from backup if there was an error
            shutil.copy2(backup_path, file_path)
            print(f"Restored original file from backup")

if __name__ == "__main__":
    print("=== Applying Fixes to Trading Pattern Algorithms ===")
    apply_fixes_to_all_algorithms()
    print("\nAll fixes have been applied. Please test the algorithms to verify they work correctly.")
