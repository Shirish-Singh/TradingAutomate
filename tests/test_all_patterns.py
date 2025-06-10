import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
import traceback

# Add the parent directory to the path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the pattern detection functions
from algos.DoubleBottom import invokeDoubleBottom
from algos.DoubleTop import invokeDoubleTop
from algos.HeadAndShoulder import invokeHeadAndShoulders
from algos.RisingWedge import invokeRisingWedge
from algos.FallingWedge import invokeFallingWedge
from algos.CupAndHandle import invokeCupAndHandle
from algos.AscendingTriangle import invokeAscendingTriangle

from tests.test_utils import fetch_test_data

def test_pattern(pattern_name, ticker, period, invoke_func):
    """Test a specific pattern detection algorithm"""
    print(f"\nTesting {pattern_name} pattern with {ticker} data...")
    
    try:
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Fetch test data
            df = fetch_test_data(ticker=ticker, period=period)
            
            # Run the pattern detection function
            message, image_path = invoke_func(df)
            
            # Check for warnings
            warning_messages = [str(warning.message) for warning in w]
            future_warnings = [msg for msg in warning_messages if "FutureWarning" in msg]
            
            if future_warnings:
                print(f"⚠️ {pattern_name} test generated {len(future_warnings)} FutureWarnings:")
                for warning in future_warnings[:3]:  # Show first 3 warnings
                    print(f"  - {warning[:100]}...")
                return False, message, image_path, future_warnings
            else:
                print(f"✅ {pattern_name} test passed without FutureWarnings")
                print(f"  Message: {message}")
                print(f"  Image: {image_path}")
                return True, message, image_path, []
    
    except Exception as e:
        print(f"❌ {pattern_name} test failed with error: {e}")
        print(traceback.format_exc())
        return False, str(e), None, []

def test_all_patterns():
    """Test all pattern detection algorithms"""
    results = {}
    
    # Create a directory for test results
    test_results_dir = os.path.join(os.path.dirname(__file__), 'test_results')
    os.makedirs(test_results_dir, exist_ok=True)
    
    # Test data for each pattern
    test_cases = [
        ("Double Bottom", "AAPL", "1y", invokeDoubleBottom),
        ("Double Top", "META", "1y", invokeDoubleTop),
        ("Head and Shoulders", "MSFT", "1y", invokeHeadAndShoulders),
        ("Rising Wedge", "AMZN", "1y", invokeRisingWedge),
        ("Falling Wedge", "GOOGL", "1y", invokeFallingWedge),
        ("Cup and Handle", "NVDA", "1y", invokeCupAndHandle),
        ("Ascending Triangle", "TSLA", "1y", invokeAscendingTriangle)
    ]
    
    # Test each pattern
    for pattern_name, ticker, period, invoke_func in test_cases:
        success, message, image_path, warnings = test_pattern(pattern_name, ticker, period, invoke_func)
        
        results[pattern_name] = {
            "success": success,
            "message": message,
            "image_path": image_path,
            "warnings": warnings
        }
    
    # Print summary of results
    print("\n=== Test Results Summary ===")
    passed = 0
    failed = 0
    
    for pattern_name, result in results.items():
        status = "✅ Passed" if result["success"] else "❌ Failed"
        print(f"{pattern_name}: {status}")
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
            if result["warnings"]:
                print(f"  - Has FutureWarnings: {len(result['warnings'])}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed} tests")
    print(f"Failed: {failed} tests")
    
    # Write detailed results to a file
    with open(os.path.join(test_results_dir, 'pattern_test_results.txt'), 'w') as f:
        f.write("=== Trading Pattern Algorithm Test Results ===\n\n")
        
        for pattern_name, result in results.items():
            status = "PASSED" if result["success"] else "FAILED"
            f.write(f"{pattern_name}: {status}\n")
            f.write(f"  Message: {result['message']}\n")
            
            if result["image_path"]:
                f.write(f"  Image: {result['image_path']}\n")
            
            if result["warnings"]:
                f.write(f"  Warnings ({len(result['warnings'])}):\n")
                for warning in result["warnings"][:3]:
                    f.write(f"    - {warning[:100]}...\n")
            
            f.write("\n")
        
        f.write(f"Total: {len(results)} tests\n")
        f.write(f"Passed: {passed} tests\n")
        f.write(f"Failed: {failed} tests\n")
    
    return results

if __name__ == "__main__":
    print("=== Testing Trading Pattern Algorithms ===")
    results = test_all_patterns()
    print("\nDetailed test results have been saved to tests/test_results/pattern_test_results.txt")
