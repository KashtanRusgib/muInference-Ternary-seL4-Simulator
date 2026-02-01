"""
Script to run simulator in Astronics CoPilot for avionics testing.
Generate bus scripts from sim results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from testing_harness import TestingHarness

def main():
    # Similar setup as above
    result = {}  # Run scenario
    harness = TestingHarness()
    print(harness.run_test(result, "copilot"))

if __name__ == "__main__":
    main()