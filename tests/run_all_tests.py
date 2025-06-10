import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import importlib
import traceback

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from tests.algos.test_double_bottom import test_double_bottom_with_synthetic_data, fix_alignment_issues as fix_double_bottom
from tests.algos.test_double_top import test_double_top_with_synthetic_data, fix_alignment_issues as fix_double_top
from tests.algos.test_head_and_shoulders import test_head_and_shoulders_with_synthetic_data, fix_alignment_issues as fix_head_and_shoulders
from tests.algos.test_rising_wedge import test_rising_wedge_with_synthetic_data, fix_alignment_issues as fix_rising_wedge
from tests.algos.test_falling_wedge import test_falling_wedge_with_synthetic_data, fix_alignment_issues as fix_falling_wedge
from tests.algos.test_cup_and_handle import test_cup_and_handle_with_synthetic_data, fix_datetime_indexing_issues as fix_cup_and_handle

def run_all_tests():
    """Run all pattern detection tests and apply fixes if needed"""
    results = {}
    fixed_files = []
    
    # Test Double Bottom
    print("\n=== Testing Double Bottom Pattern ===")
    try:
        message, image_path = test_double_bottom_with_synthetic_data()
        results["Double Bottom"] = (message, image_path)
        print("✅ Double Bottom test passed")
    except Exception as e:
        print(f"❌ Double Bottom test failed: {e}")
        print(traceback.format_exc())
        fixed_file = fix_double_bottom()
        fixed_files.append(fixed_file)
    
    # Test Double Top
    print("\n=== Testing Double Top Pattern ===")
    try:
        message, image_path = test_double_top_with_synthetic_data()
        results["Double Top"] = (message, image_path)
        print("✅ Double Top test passed")
    except Exception as e:
        print(f"❌ Double Top test failed: {e}")
        print(traceback.format_exc())
        fixed_file = fix_double_top()
        fixed_files.append(fixed_file)
    
    # Test Head and Shoulders
    print("\n=== Testing Head and Shoulders Pattern ===")
    try:
        message, image_path = test_head_and_shoulders_with_synthetic_data()
        results["Head and Shoulders"] = (message, image_path)
        print("✅ Head and Shoulders test passed")
    except Exception as e:
        print(f"❌ Head and Shoulders test failed: {e}")
        print(traceback.format_exc())
        fixed_file = fix_head_and_shoulders()
        fixed_files.append(fixed_file)
    
    # Test Rising Wedge
    print("\n=== Testing Rising Wedge Pattern ===")
    try:
        message, image_path = test_rising_wedge_with_synthetic_data()
        results["Rising Wedge"] = (message, image_path)
        print("✅ Rising Wedge test passed")
    except Exception as e:
        print(f"❌ Rising Wedge test failed: {e}")
        print(traceback.format_exc())
        fixed_file = fix_rising_wedge()
        fixed_files.append(fixed_file)
    
    # Test Falling Wedge
    print("\n=== Testing Falling Wedge Pattern ===")
    try:
        message, image_path = test_falling_wedge_with_synthetic_data()
        results["Falling Wedge"] = (message, image_path)
        print("✅ Falling Wedge test passed")
    except Exception as e:
        print(f"❌ Falling Wedge test failed: {e}")
        print(traceback.format_exc())
        fixed_file = fix_falling_wedge()
        fixed_files.append(fixed_file)
    
    # Test Cup and Handle
    print("\n=== Testing Cup and Handle Pattern ===")
    try:
        message, image_path = test_cup_and_handle_with_synthetic_data()
        results["Cup and Handle"] = (message, image_path)
        print("✅ Cup and Handle test passed")
    except Exception as e:
        print(f"❌ Cup and Handle test failed: {e}")
        print(traceback.format_exc())
        fixed_file = fix_cup_and_handle()
        fixed_files.append(fixed_file)
    
    # Summary of results
    print("\n=== Test Results Summary ===")
    for pattern, (message, _) in results.items():
        status = "✅ Passed" if "detected" in message and "Error" not in message else "❌ Failed"
        print(f"{pattern}: {status}")
    
    # Apply fixes if needed
    if fixed_files:
        print("\n=== Fixed Files ===")
        for fixed_file in fixed_files:
            print(f"- {fixed_file}")
        
        apply_fixes = input("\nDo you want to apply all fixes? (y/n): ")
        if apply_fixes.lower() == 'y':
            for fixed_file in fixed_files:
                original_file = fixed_file.replace('.fixed', '')
                os.rename(fixed_file, original_file)
                print(f"Applied fix: {original_file}")
    else:
        print("\nAll tests passed! No fixes needed.")

def apply_all_fixes():
    """Apply all fixes without running tests"""
    fixed_files = []
    
    # Fix Double Bottom
    print("Fixing Double Bottom...")
    fixed_files.append(fix_double_bottom())
    
    # Fix Double Top
    print("Fixing Double Top...")
    fixed_files.append(fix_double_top())
    
    # Fix Head and Shoulders
    print("Fixing Head and Shoulders...")
    fixed_files.append(fix_head_and_shoulders())
    
    # Fix Rising Wedge
    print("Fixing Rising Wedge...")
    fixed_files.append(fix_rising_wedge())
    
    # Fix Falling Wedge
    print("Fixing Falling Wedge...")
    fixed_files.append(fix_falling_wedge())
    
    # Fix Cup and Handle
    print("Fixing Cup and Handle...")
    fixed_files.append(fix_cup_and_handle())
    
    # Apply all fixes
    print("\n=== Applying All Fixes ===")
    for fixed_file in fixed_files:
        original_file = fixed_file.replace('.fixed', '')
        os.rename(fixed_file, original_file)
        print(f"Applied fix: {original_file}")

if __name__ == "__main__":
    print("=== Trading Pattern Algorithm Test Suite ===")
    print("1. Run all tests")
    print("2. Apply all fixes directly")
    choice = input("Enter your choice (1/2): ")
    
    if choice == '1':
        run_all_tests()
    elif choice == '2':
        apply_all_fixes()
    else:
        print("Invalid choice. Exiting.")
