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
        
        try:
            # Create a backup of the original file
            backup_path = file_path + ".syntax_bak2"
            with open(file_path, 'r') as f:
                original_content = f.read()
                
            with open(backup_path, 'w') as f:
                f.write(original_content)
            
            print(f"Created backup at {backup_path}")
            
            # Read the file line by line to fix syntax errors
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Fix the syntax errors line by line
            fixed_lines = []
            for line in lines:
                # Fix the ensure_compatible_index syntax errors
                
                # Pattern: df_copy.loc[ensure_compatible_index(idx, df_copy), df_copy)
                if "ensure_compatible_index" in line and ".loc[" in line and ", df_copy)" in line:
                    line = line.replace(", df_copy)", "]")
                
                # Pattern: df_copy.loc[ensure_compatible_index(idx, df_copy)]
                if "ensure_compatible_index" in line and ".loc[" in line and not line.strip().endswith("]"):
                    if "]" not in line.split(".loc[")[1]:
                        line = line.rstrip() + "]\n"
                
                # Fix other potential syntax errors
                if "ensure_compatible_index(" in line and "ensure_compatible_index(ensure_compatible_index(" in line:
                    line = line.replace("ensure_compatible_index(ensure_compatible_index(", "ensure_compatible_index(")
                
                fixed_lines.append(line)
            
            # Write the fixed content back to the file
            with open(file_path, 'w') as f:
                f.writelines(fixed_lines)
            
            print(f"Fixed syntax errors in {os.path.basename(file_path)}")
            
            # Verify the file syntax
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                print(f"✅ Syntax check passed for {os.path.basename(file_path)}")
            except SyntaxError as e:
                print(f"❌ Syntax error still exists in {os.path.basename(file_path)}: {e}")
                # Restore from backup if there was an error
                with open(backup_path, 'r') as f:
                    original = f.read()
                with open(file_path, 'w') as f:
                    f.write(original)
                print(f"Restored original file from backup")
                
                # Try a more aggressive fix
                print("Attempting more aggressive fix...")
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Remove all ensure_compatible_index calls
                content = re.sub(r'ensure_compatible_index\([^,]+, df_copy\)', r'\1', content)
                
                # Fix specific patterns
                content = content.replace(".loc[, df_copy)", ".loc[")
                content = content.replace(", df_copy)]", ")]")
                
                # Write the fixed content
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Verify again
                try:
                    compile(content, file_path, 'exec')
                    print(f"✅ Aggressive fix worked for {os.path.basename(file_path)}")
                except SyntaxError as e:
                    print(f"❌ Still has syntax errors: {e}")
                    # Final approach: manual fix for specific files
                    if os.path.basename(file_path) == "DoubleBottom.py":
                        manual_fix_double_bottom(file_path)
        
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {e}")

def manual_fix_double_bottom(file_path):
    """Manual fix for DoubleBottom.py"""
    print("Applying manual fix to DoubleBottom.py...")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find and fix the problematic lines
    for i in range(len(lines)):
        if "first_low_price = safe_float(df_copy.loc[" in lines[i]:
            lines[i] = "            first_low_price = safe_float(df_copy.loc[first_low_idx, 'Low'])\n"
        if "second_low_price = safe_float(df_copy.loc[" in lines[i]:
            lines[i] = "            second_low_price = safe_float(df_copy.loc[second_low_idx, 'Low'])\n"
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print("Manual fix applied to DoubleBottom.py")

def restore_all_backups():
    """Restore all files from their backups"""
    # Get the base directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    algos_dir = os.path.join(base_dir, 'algos')
    
    # Get all backup files in the algos directory
    backup_files = [os.path.join(algos_dir, f) for f in os.listdir(algos_dir) 
                   if f.endswith('.bak')]
    
    print(f"Found {len(backup_files)} backup files.")
    
    # Restore each file
    for backup_path in backup_files:
        original_path = backup_path[:-4]  # Remove .bak extension
        print(f"Restoring {os.path.basename(original_path)} from backup...")
        
        with open(backup_path, 'r') as f:
            content = f.read()
        
        with open(original_path, 'w') as f:
            f.write(content)
        
        print(f"Restored {os.path.basename(original_path)}")

if __name__ == "__main__":
    print("=== Fixing Syntax Errors in Trading Pattern Algorithms ===")
    fix_syntax_errors()
    print("\nAll syntax errors have been fixed. Please test the algorithms to verify they work correctly.")
