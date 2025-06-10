import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

def test_all_patterns():
    """Test all pattern detection algorithms with real market data"""
    results = {}
    
    # Create a directory for test results
    test_results_dir = os.path.join(os.path.dirname(__file__), 'test_results')
    os.makedirs(test_results_dir, exist_ok=True)
    
    # Test data for each pattern
    test_data = {
        "Double Bottom": ("AAPL", "1y"),
        "Double Top": ("META", "1y"),
        "Head and Shoulders": ("MSFT", "1y"),
        "Rising Wedge": ("AMZN", "1y"),
        "Falling Wedge": ("GOOGL", "1y"),
        "Cup and Handle": ("NVDA", "1y"),
        "Ascending Triangle": ("TSLA", "1y")
    }
    
    # Test each pattern
    for pattern_name, (ticker, period) in test_data.items():
        print(f"\n=== Testing {pattern_name} Pattern ===")
        try:
            # Fetch test data
            df = fetch_test_data(ticker=ticker, period=period)
            
            # Run the appropriate pattern detection function
            if pattern_name == "Double Bottom":
                message, image_path = invokeDoubleBottom(df)
            elif pattern_name == "Double Top":
                message, image_path = invokeDoubleTop(df)
            elif pattern_name == "Head and Shoulders":
                message, image_path = invokeHeadAndShoulders(df)
            elif pattern_name == "Rising Wedge":
                message, image_path = invokeRisingWedge(df)
            elif pattern_name == "Falling Wedge":
                message, image_path = invokeFallingWedge(df)
            elif pattern_name == "Cup and Handle":
                message, image_path = invokeCupAndHandle(df)
            elif pattern_name == "Ascending Triangle":
                message, image_path = invokeAscendingTriangle(df)
            
            # Save the result
            results[pattern_name] = {
                "status": "✅ Passed",
                "message": message,
                "image_path": image_path
            }
            
            print(f"✅ {pattern_name} test passed")
            print(f"Message: {message}")
            print(f"Image: {image_path}")
            
        except Exception as e:
            # Save the error
            results[pattern_name] = {
                "status": "❌ Failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            print(f"❌ {pattern_name} test failed: {e}")
            print(traceback.format_exc())
    
    # Print summary of results
    print("\n=== Test Results Summary ===")
    for pattern_name, result in results.items():
        print(f"{pattern_name}: {result['status']}")
        if result['status'] == "❌ Failed":
            print(f"  Error: {result['error']}")
    
    # Count passed and failed tests
    passed = sum(1 for result in results.values() if result['status'] == "✅ Passed")
    failed = sum(1 for result in results.values() if result['status'] == "❌ Failed")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed} tests")
    print(f"Failed: {failed} tests")
    
    # Write detailed results to a file
    with open(os.path.join(test_results_dir, 'test_results.txt'), 'w') as f:
        f.write("=== Trading Pattern Algorithm Test Results ===\n\n")
        for pattern_name, result in results.items():
            f.write(f"{pattern_name}: {result['status']}\n")
            if result['status'] == "✅ Passed":
                f.write(f"  Message: {result['message']}\n")
                f.write(f"  Image: {result['image_path']}\n")
            else:
                f.write(f"  Error: {result['error']}\n")
                f.write(f"  Traceback: {result['traceback']}\n")
            f.write("\n")
        
        f.write(f"Total: {len(results)} tests\n")
        f.write(f"Passed: {passed} tests\n")
        f.write(f"Failed: {failed} tests\n")
    
    return results

if __name__ == "__main__":
    print("=== Verifying Trading Pattern Algorithm Fixes ===")
    results = test_all_patterns()
    print("\nDetailed test results have been saved to tests/test_results/test_results.txt")
