"""
One-click script to run all tests across the project: module units, full system, redteam, TrickCFS/CoPilot mocks.
Asserts overall success; logs failures.
"""

import subprocess
import sys
import os

if not os.environ.get("VIRTUAL_ENV"):
    print("Please activate venv: source venv/bin/activate")
    sys.exit(1)

def run_test(file: str) -> bool:
    result = subprocess.run(["python", file], capture_output=True)
    output = result.stdout.decode() + (result.stderr.decode() if result.stderr else '')
    if "passed" in output.lower() and result.returncode == 0:
        print(f"{file} passed")
        return True
    else:
        print(f"{file} failed: {output}")
        return False

def main():
    tests = [
        "ternary.py",
        "lattice.py",
        "triplex.py",
        "simulator.py",
        "parameters.py",
        "testing_harness.py",
        "run_trickcfs.py",
        "run_copilot.py",
        "redteam_tests.py",
        "tests/full_system_tests.py",
        "fpga_interface.py"
    ]
    successes = [run_test(t) for t in tests]
    if all(successes):
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()