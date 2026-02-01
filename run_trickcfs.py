"""
Script to run simulator under TrickCFS for spaceflight sims.
Load sim result, inject to Trick models, run failure injection.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if not os.path.exists('vendor/trick'):
    print("Submodules not initialized")
    sys.exit(1)

from simulator import NominalScenario  # Example
from triplex import TriplexSystem
from lattice import Lattice
from parameters import ParameterProvider
from testing_harness import TestingHarness

def main():
    provider = ParameterProvider("parameters.json")
    evaluators = [lambda x, p=provider, ph="": p.is_within_bound(x.get("temp", 0), "temp", ph == "stress")] * 3
    triplex = TriplexSystem(evaluators)
    lattice = Lattice()
    scenario = NominalScenario("nominal")
    result = scenario.run(triplex, lattice)
    harness = TestingHarness()
    print(harness.run_test(result, "trick"))

if __name__ == "__main__":
    main()