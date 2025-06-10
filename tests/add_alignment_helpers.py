import sys
import os
import re
import shutil

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def add_alignment_helper(file_path):
    """
    Add alignment helper function to a file.
    
    Args:
        file_path: Path to the algorithm file
    """
    print(f"Adding alignment helper to {os.path.basename(file_path)}...")
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define the alignment helper function
    alignment_helper = '''def ensure_aligned(left, right):
    """
    Ensure two pandas Series or DataFrames are aligned before operations.
    
    Args:
        left: First pandas Series or DataFrame
        right: Second pandas Series or DataFrame
        
    Returns:
        tuple: (aligned_left, aligned_right)
    """
    if hasattr(left, 'align') and hasattr(right, 'align'):
        return left.align(right, axis=0, copy=False)
    return left, right
'''
    
    # Check if the file already has an alignment helper function
    if "def ensure_aligned" not in content:
        # Add the alignment helper function after the safe_float function
        if "def safe_float" in content:
            # Find the end of the safe_float function
            safe_float_start = content.find("def safe_float")
            next_def = content.find("def ", safe_float_start + 10)
            
            if next_def != -1:
                # Insert the alignment helper function before the next function
                content = content[:next_def] + alignment_helper + "\n" + content[next_def:]
            else:
                # If we can't find the next function, add it at the end of imports
                import_section_end = 0
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_section_end = i
                
                # Insert after imports
                content_parts = content.split('\n')
                content_parts.insert(import_section_end + 1, '')
                content_parts.insert(import_section_end + 2, alignment_helper)
                content = '\n'.join(content_parts)
        else:
            # If no safe_float function, add after imports
            import_section_end = 0
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_section_end = i
            
            # Insert after imports
            content_parts = content.split('\n')
            content_parts.insert(import_section_end + 1, '')
            content_parts.insert(import_section_end + 2, alignment_helper)
            content = '\n'.join(content_parts)
    
    # Replace problematic comparison operations with aligned versions
    # Pattern: df['Column1'] > df['Column2']
    comparison_patterns = [
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\[[\'"]([\w\s]+)[\'"]\]\s*([><=!]+)\s*([a-zA-Z_][a-zA-Z0-9_]*)\[[\'"]([\w\s]+)[\'"]\]', 
         r'lambda: ensure_aligned(\1["\2"], \4["\5"])[0] \3 ensure_aligned(\1["\2"], \4["\5"])[1]'),
        
        # Pattern: df.loc[...] > df.loc[...]
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\.loc\[[^\]]+\]\s*([><=!]+)\s*([a-zA-Z_][a-zA-Z0-9_]*)\.loc\[[^\]]+\]', 
         r'lambda: ensure_aligned(\1.loc[...], \3.loc[...])[0] \2 ensure_aligned(\1.loc[...], \3.loc[...])[1]'),
        
        # Pattern: df.iloc[...] > df.iloc[...]
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\.iloc\[[^\]]+\]\s*([><=!]+)\s*([a-zA-Z_][a-zA-Z0-9_]*)\.iloc\[[^\]]+\]', 
         r'lambda: ensure_aligned(\1.iloc[...], \3.iloc[...])[0] \2 ensure_aligned(\1.iloc[...], \3.iloc[...])[1]'),
    ]
    
    # We'll manually fix these in the specific files rather than using regex
    # to avoid breaking the code
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_specific_alignment_issues(file_path):
    """
    Fix specific alignment issues in a file based on its name.
    
    Args:
        file_path: Path to the algorithm file
    """
    filename = os.path.basename(file_path)
    
    if filename == "HeadAndShoulder.py":
        print(f"Fixing specific alignment issues in {filename}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix specific alignment issues in HeadAndShoulder.py
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
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    elif filename == "RisingWedge.py":
        print(f"Fixing specific alignment issues in {filename}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix specific alignment issues in RisingWedge.py
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
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    elif filename == "FallingWedge.py":
        print(f"Fixing specific alignment issues in {filename}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix specific alignment issues in FallingWedge.py
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
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    elif filename == "DoubleBottom.py":
        print(f"Fixing specific alignment issues in {filename}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix specific alignment issues in DoubleBottom.py
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
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    elif filename == "DoubleTop.py":
        print(f"Fixing specific alignment issues in {filename}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix specific alignment issues in DoubleTop.py
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
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    return True

def fix_fibonacci_calculator(file_path):
    """
    Fix the FibonacciCalculator class to handle missing df parameter.
    
    Args:
        file_path: Path to the fibonacci_calculator.py file
    """
    if os.path.basename(file_path) != "fibonacci_calculator.py":
        return False
    
    print(f"Fixing FibonacciCalculator class in {os.path.basename(file_path)}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the __init__ method to make df parameter optional
    if "def __init__(self, df):" in content:
        content = content.replace(
            "def __init__(self, df):",
            "def __init__(self, df=None):"
        )
        
        # Add check for df parameter
        if "self.df = df" in content:
            content = content.replace(
                "self.df = df",
                "self.df = df if df is not None else pd.DataFrame()"
            )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def apply_alignment_fixes():
    """Apply alignment fixes to all algorithm files"""
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
        backup_path = file_path + ".alignment_bak"
        shutil.copy2(file_path, backup_path)
        print(f"Created backup at {backup_path}")
        
        try:
            # Add alignment helper function
            add_alignment_helper(file_path)
            
            # Fix specific alignment issues based on file name
            fix_specific_alignment_issues(file_path)
            
            # Fix FibonacciCalculator if it's the fibonacci_calculator.py file
            fix_fibonacci_calculator(file_path)
            
            print(f"Successfully applied alignment fixes to {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Error fixing {os.path.basename(file_path)}: {e}")
            # Restore from backup if there was an error
            shutil.copy2(backup_path, file_path)
            print(f"Restored original file from backup")

if __name__ == "__main__":
    print("=== Applying Alignment Fixes to Trading Pattern Algorithms ===")
    apply_alignment_fixes()
    print("\nAll alignment fixes have been applied. Please test the algorithms to verify they work correctly.")
