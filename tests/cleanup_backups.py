import os
import glob
import sys

def remove_backup_files(directory):
    """
    Remove all backup files (ending with .bak or similar extensions) from the directory and its subdirectories.
    
    Args:
        directory: The directory to clean up
    """
    # Define backup file patterns
    backup_patterns = [
        "*.bak",
        "*.alignment_bak",
        "*.final_align_bak",
        "*.final_align2_bak",
        "*.final_wedge_bak",
        "*.backup"
    ]
    
    removed_count = 0
    
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for pattern in backup_patterns:
            # Find files matching the pattern in the current directory
            backup_files = glob.glob(os.path.join(root, pattern))
            
            # Remove each backup file
            for file_path in backup_files:
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
    
    return removed_count

if __name__ == "__main__":
    # Get the base directory (project root)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    print(f"=== Cleaning up backup files in {base_dir} ===")
    
    # Remove backup files
    count = remove_backup_files(base_dir)
    
    print(f"\nCleanup complete! Removed {count} backup files.")
