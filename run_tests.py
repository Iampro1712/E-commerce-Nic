#!/usr/bin/env python3
"""
Script to run tests with proper configuration
"""
import os
import sys
import subprocess

def run_tests():
    """Run the test suite"""
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    
    # Run pytest with coverage
    cmd = [
        sys.executable, '-m', 'pytest',
        '--cov=app',
        '--cov-report=html',
        '--cov-report=term-missing',
        '-v'
    ]
    
    # Add any additional arguments passed to this script
    cmd.extend(sys.argv[1:])
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode

if __name__ == '__main__':
    sys.exit(run_tests())
