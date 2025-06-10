import sys
import os
import shutil

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def restore_original_files():
    """Restore all algorithm files from their backups"""
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
        
        shutil.copy2(backup_path, original_path)
        print(f"Restored {os.path.basename(original_path)}")

if __name__ == "__main__":
    print("=== Restoring Original Algorithm Files ===")
    restore_original_files()
    print("\nAll original files have been restored.")
