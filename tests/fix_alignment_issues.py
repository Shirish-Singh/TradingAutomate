import sys
import os
import re
import shutil

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_alignment_issues_in_file(file_path):
    """
    Fix specific alignment issues in a file.
    
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
        # Fix alignment issues in DoubleBottom.py
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
        
        # Add alignment for DataFrame operations
        if "between_lows = df_copy.loc[first_low_idx:second_low_idx]" in content:
            content = content.replace(
                "neckline_price = between_lows['High'].max()",
                "neckline_price = safe_float(between_lows['High'].max())"
            )
    
    elif filename == "HeadAndShoulder.py":
        # Fix alignment issues in HeadAndShoulder.py
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
        
        # Add alignment for DataFrame operations
        if "left_shoulder_idx = peaks_idx[0]" in content:
            content = content.replace(
                "left_shoulder_price = df_copy.loc[left_shoulder_idx, 'High']",
                "left_shoulder_price = safe_float(df_copy.loc[left_shoulder_idx, 'High'])"
            )
            content = content.replace(
                "head_price = df_copy.loc[head_idx, 'High']",
                "head_price = safe_float(df_copy.loc[head_idx, 'High'])"
            )
            content = content.replace(
                "right_shoulder_price = df_copy.loc[right_shoulder_idx, 'High']",
                "right_shoulder_price = safe_float(df_copy.loc[right_shoulder_idx, 'High'])"
            )
    
    elif filename == "RisingWedge.py":
        # Fix alignment issues in RisingWedge.py
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
        # Fix alignment issues in FallingWedge.py
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
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def fix_all_alignment_issues():
    """Fix alignment issues in all algorithm files"""
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
            backup_path = file_path + ".align_fix_bak"
            shutil.copy2(file_path, backup_path)
            print(f"Created backup at {backup_path}")
            
            try:
                # Fix alignment issues
                fix_alignment_issues_in_file(file_path)
                print(f"Successfully fixed alignment issues in {filename}")
                
            except Exception as e:
                print(f"Error fixing {filename}: {e}")
                # Restore from backup if there was an error
                shutil.copy2(backup_path, file_path)
                print(f"Restored original file from backup")
        else:
            print(f"File {filename} not found in {algos_dir}")

if __name__ == "__main__":
    print("=== Fixing Alignment Issues in Trading Pattern Algorithms ===")
    fix_all_alignment_issues()
    print("\nAll alignment issues have been fixed. Please test the algorithms to verify they work correctly.")
