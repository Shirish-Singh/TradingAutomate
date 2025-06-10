import sys
import os
import re

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_syntax_errors():
    """Fix syntax errors in the algorithm files caused by the previous fixes"""
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
        backup_path = file_path + ".syntax_bak"
        with open(file_path, 'r') as f:
            original_content = f.read()
            
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        print(f"Created backup at {backup_path}")
        
        # Fix the syntax errors
        fixed_content = original_content
        
        # Fix the ensure_compatible_index syntax errors
        # Pattern: ensure_compatible_index(ensure_compatible_index(idx, 'column'])
        pattern1 = r"ensure_compatible_index\(ensure_compatible_index\(([^,]+), ([^)]+)\]\)"
        replacement1 = r"ensure_compatible_index(\1, df_copy), df_copy)"
        fixed_content = re.sub(pattern1, replacement1, fixed_content)
        
        # Pattern: df_copy.loc[ensure_compatible_index(idx, 'column'])
        pattern2 = r"\.loc\[ensure_compatible_index\(([^,]+), ([^)]+)\]\)"
        replacement2 = r".loc[ensure_compatible_index(\1, df_copy)]"
        fixed_content = re.sub(pattern2, replacement2, fixed_content)
        
        # Pattern: df.loc[ensure_compatible_index(idx, df_copy), 'column']
        pattern3 = r"\.loc\[ensure_compatible_index\(([^,]+), df_copy\), ([^]]+)\]"
        replacement3 = r".loc[ensure_compatible_index(\1, df_copy), \2]"
        fixed_content = re.sub(pattern3, replacement3, fixed_content)
        
        # Write the fixed content back to the file
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        print(f"Fixed syntax errors in {os.path.basename(file_path)}")

if __name__ == "__main__":
    print("=== Fixing Syntax Errors in Trading Pattern Algorithms ===")
    fix_syntax_errors()
    print("\nAll syntax errors have been fixed. Please test the algorithms to verify they work correctly.")
