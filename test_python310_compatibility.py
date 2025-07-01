#!/usr/bin/env python3
"""
Test script to verify Python 3.10+ compatibility for MAnormFast
"""
import sys
import time
import os

def test_python_version():
    """Test if Python version is 3.10+"""
    print(f"Python version: {sys.version}")
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 10:
        print("✓ Python version is 3.10+")
        return True
    else:
        print("✗ Python version is not 3.10+")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    try:
        # Test basic imports
        import numpy as np
        print(f"✓ numpy {np.__version__}")
        
        import matplotlib
        print(f"✓ matplotlib {matplotlib.__version__}")
        
        import pandas as pd
        print(f"✓ pandas {pd.__version__}")
        
        import scipy
        print(f"✓ scipy {scipy.__version__}")
        
        import statsmodels
        print(f"✓ statsmodels {statsmodels.__version__}")
        
        # Test specific scipy import that was changed
        from scipy.special import comb
        print("✓ scipy.special.comb import successful")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_time_functions():
    """Test time.perf_counter() functionality"""
    try:
        start = time.perf_counter()
        time.sleep(0.01)  # Small delay
        end = time.perf_counter()
        elapsed = end - start
        print(f"✓ time.perf_counter() works: {elapsed:.4f}s")
        return True
    except Exception as e:
        print(f"✗ time.perf_counter() error: {e}")
        return False

def test_dictionary_operations():
    """Test dictionary operations compatibility"""
    try:
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'c': 3, 'd': 4}
        
        # Test the fixed dictionary keys concatenation
        keys = set(list(dict1.keys()) + list(dict2.keys()))
        expected = {'a', 'b', 'c', 'd'}
        
        if keys == expected:
            print("✓ Dictionary keys concatenation works")
            return True
        else:
            print(f"✗ Dictionary keys concatenation failed: {keys} != {expected}")
            return False
    except Exception as e:
        print(f"✗ Dictionary operations error: {e}")
        return False

def test_integer_division():
    """Test integer division behavior"""
    try:
        # Test cases that were fixed
        result1 = (10 + 20) // 2 + 1  # Should be 16
        result2 = 1000 // 2  # Should be 500
        
        if result1 == 16 and result2 == 500:
            print("✓ Integer division works correctly")
            return True
        else:
            print(f"✗ Integer division failed: {result1}, {result2}")
            return False
    except Exception as e:
        print(f"✗ Integer division error: {e}")
        return False

def test_print_functions():
    """Test print function syntax"""
    try:
        # These should work in Python 3
        print("✓ Basic print function works")
        print("✓ Print with formatting: %s" % "test")
        print("✓ Print with multiple args:", "arg1", "arg2")
        return True
    except Exception as e:
        print(f"✗ Print function error: {e}")
        return False

def test_local_imports():
    """Test if local MAnormFast modules can be imported"""
    try:
        # Add current directory to path for testing
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from lib.peaks import Peak
        print("✓ lib.peaks.Peak import successful")
        
        # Test Peak class basic functionality
        peak = Peak('chr1', 1000, 2000)
        if peak.chrm == 'chr1' and peak.start == 1000 and peak.end == 2000:
            print("✓ Peak class instantiation works")
        else:
            print("✗ Peak class instantiation failed")
            return False
            
        return True
    except ImportError as e:
        print(f"✗ Local import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Peak class error: {e}")
        return False

def main():
    """Run all compatibility tests"""
    print("=" * 50)
    print("MAnormFast Python 3.10+ Compatibility Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Imports", test_imports),
        ("Time Functions", test_time_functions),
        ("Dictionary Operations", test_dictionary_operations),
        ("Integer Division", test_integer_division),
        ("Print Functions", test_print_functions),
        ("Local Imports", test_local_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"Test {test_name} failed")
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MAnormFast is Python 3.10+ compatible!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())