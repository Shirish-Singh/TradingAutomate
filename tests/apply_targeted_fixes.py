import sys
import os
import re
import shutil

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def update_safe_float_function(file_path):
    """
    Update or add the safe_float function in a file.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Updating safe_float function in {os.path.basename(file_path)}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define the improved safe_float function
    improved_safe_float = '''def safe_float(value):
    """
    Safely convert a value to float, handling pandas Series objects.
    
    Args:
        value: Value to convert to float, could be a pandas Series, DataFrame, or scalar
        
    Returns:
        float: The converted float value
    """
    if isinstance(value, pd.Series):
        if len(value) == 0:
            return 0.0
        return float(value.iloc[0])
    elif isinstance(value, pd.DataFrame):
        if value.empty:
            return 0.0
        return float(value.iloc[0, 0])
    return float(value)
'''
    
    # Check if the file already has a safe_float function
    if "def safe_float" in content:
        # Find the start and end of the existing safe_float function
        start_idx = content.find("def safe_float")
        
        # Find the next function definition after safe_float
        next_func_idx = content.find("def ", start_idx + 10)
        
        if next_func_idx != -1:
            # Replace the existing safe_float function
            content = content[:start_idx] + improved_safe_float + content[next_func_idx:]
        else:
            # If we can't find the next function, just add the improved function at the top
            content = improved_safe_float + "\n\n" + content.replace("def safe_float" + content.split("def safe_float", 1)[1], "")
    else:
        # Add the safe_float function after imports
        import_section_end = 0
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_section_end = i
        
        # Insert after imports
        if import_section_end > 0:
            content_parts = content.split('\n')
            content_parts.insert(import_section_end + 1, '')
            content_parts.insert(import_section_end + 2, improved_safe_float)
            content = '\n'.join(content_parts)
        else:
            # If no imports found, add at the beginning
            content = improved_safe_float + "\n\n" + content
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def replace_float_calls(file_path):
    """
    Replace direct float() calls on pandas Series with safe_float().
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Replacing float() calls in {os.path.basename(file_path)}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace float() calls on DataFrame columns/Series with safe_float()
    patterns = [
        (r'float\(([^)]+\[[\'"][^\'"]+[\'"]\])\)', r'safe_float(\1)'),
        (r'float\(([^)]+\.loc\[[^\]]+\])\)', r'safe_float(\1)'),
        (r'float\(([^)]+\.iloc\[[^\]]+\])\)', r'safe_float(\1)'),
        (r'float\(([^)]+\.[\'"][^\'"]+[\'"]\])\)', r'safe_float(\1)'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def add_empty_dataframe_checks(file_path):
    """
    Add checks for empty DataFrames to prevent errors.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Adding empty DataFrame checks to {os.path.basename(file_path)}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add empty checks for min/max/idxmin/idxmax operations
    patterns = [
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\[[\'"]\w+[\'"\]].min\(\)', r'\1["\1"].min() if not \1.empty else float("inf")'),
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\[[\'"]\w+[\'"\]].max\(\)', r'\1["\1"].max() if not \1.empty else float("-inf")'),
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\[[\'"]\w+[\'"\]].idxmin\(\)', r'\1["\1"].idxmin() if not \1.empty else None'),
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\[[\'"]\w+[\'"\]].idxmax\(\)', r'\1["\1"].idxmax() if not \1.empty else None'),
    ]
    
    # Apply patterns carefully to avoid over-replacement
    for pattern, replacement in patterns:
        # Only replace if the pattern doesn't already have an empty check
        if re.search(pattern, content) and "if not" not in re.search(pattern, content).group(0):
            content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def apply_targeted_fixes():
    """Apply targeted fixes to all algorithm files"""
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
        backup_path = file_path + ".targeted_bak"
        shutil.copy2(file_path, backup_path)
        print(f"Created backup at {backup_path}")
        
        try:
            # Update or add safe_float function
            update_safe_float_function(file_path)
            
            # Replace direct float() calls with safe_float()
            replace_float_calls(file_path)
            
            # Add empty DataFrame checks
            add_empty_dataframe_checks(file_path)
            
            print(f"Successfully applied fixes to {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Error fixing {os.path.basename(file_path)}: {e}")
            # Restore from backup if there was an error
            shutil.copy2(backup_path, file_path)
            print(f"Restored original file from backup")

if __name__ == "__main__":
    print("=== Applying Targeted Fixes to Trading Pattern Algorithms ===")
    apply_targeted_fixes()
    print("\nAll targeted fixes have been applied. Please test the algorithms to verify they work correctly.")
