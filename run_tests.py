#!/usr/bin/env python3

import subprocess
import sys
import os

def main():
    """Run test suite with coverage reporting"""
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Check if pytest is available
        subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: pytest not found. Install with: pip install -r requirements.txt")
        return 1
    
    # Run tests
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--disable-warnings'
    ]
    
    print("Running HLSAnalyzer API tests...")
    print("=" * 50)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    return result.returncode

if __name__ == '__main__':
    exit(main())