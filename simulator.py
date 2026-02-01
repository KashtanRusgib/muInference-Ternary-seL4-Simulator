"""
Implement the Simulation Runner Layer.
Follow ARCHITECTURE.md: CLI entrypoint with argparse for scenarios (nominal, stress, adversarial).
Orchestrate triplex + lattice: load mock inputs, run evaluations, log metrics (viability scores, trit sums).
Scenario classes (e.g., NominalScenario with clean data, StressScenario with gradients, AdversarialScenario with poisoning).
Integrate ternary.py, lattice.py, triplex.py.
Modularity: Easy to add scenarios.
Unit tests: End-to-end runs for each scenario.
Example: python simulator.py --scenario=nominal -> logs 'Consensus: Execute'.
"""

import argparse
from typing import Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ternary import Trit
from lattice import Lattice
from triplex import TriplexSystem
from parameters import ParameterProvider

class Scenario:
    def __init__(self, name: str, phase: str = "nominal"):
        self.name = name
        self.phase = phase

    def run(self, triplex: TriplexSystem, lattice: Lattice) -> Dict[str, any]:
        raise NotImplementedError

class NominalScenario(Scenario):
    def run(self, triplex: TriplexSystem, lattice: Lattice) -> Dict[str, any]:
        inputs = {"temp": 50}  # Mock clean data
        evals = triplex.evaluate_input(inputs)
        lattice.populate(evals, evals)  # Use evals as actors too
        consensus = triplex.compute_consensus(evals)
        return {"consensus": consensus, "score": sum(e.value for e in evals)}

class StressScenario(Scenario):
    def __init__(self, name: str):
        super().__init__(name, "stress")

    def run(self, triplex: TriplexSystem, lattice: Lattice) -> Dict[str, any]:
        inputs = {"temp": 110}  # Mock stress with gradient
        evals = triplex.evaluate_input(inputs)
        lattice.populate(evals, evals)
        consensus = triplex.compute_consensus(evals)
        return {"consensus": consensus, "score": sum(e.value for e in evals)}

class AdversarialScenario(Scenario):
    def run(self, triplex: TriplexSystem, lattice: Lattice) -> Dict[str, any]:
        inputs = {"temp": -10}  # Mock adversarial
        evals = triplex.evaluate_input(inputs)
        lattice.populate(evals, evals)
        consensus = triplex.compute_consensus(evals)
        return {"consensus": consensus, "score": sum(e.value for e in evals)}

def main():
    parser = argparse.ArgumentParser(description="μInference Simulator")
    parser.add_argument("--scenario", choices=["nominal", "stress", "adversarial"], required=True)
    args = parser.parse_args()

    provider = ParameterProvider()
    # Mock evaluators - adjust for real params later
    evaluators = [lambda inp, p, ph: p.is_within_bound(inp["temp"], "temp", ph == "stress")] * 3
    scenarios = {
        "nominal": NominalScenario("nominal"),
        "stress": StressScenario("stress"),
        "adversarial": AdversarialScenario("adversarial"),
    }
    phase = scenarios[args.scenario].phase
    triplex = TriplexSystem(evaluators, provider, phase)
    lattice = Lattice()

    result = scenarios[args.scenario].run(triplex, lattice)
    print(f"Consensus: {result['consensus']}. Score: {result['score']}")

# Unit tests
def test_simulator():
    try:
        provider = ParameterProvider()
        evaluators = [lambda inp, p, ph: p.is_within_bound(inp["temp"], "temp", ph == "stress")] * 3
        triplex = TriplexSystem(evaluators, provider, "nominal")
        lattice = Lattice()
        # Nominal
        result = NominalScenario("nominal").run(triplex, lattice)
        assert result["consensus"] == Trit(Trit.POS)
        # Stress
        triplex_stress = TriplexSystem(evaluators, provider, "stress")
        result = StressScenario("stress").run(triplex_stress, lattice)
        # Since 110 with gradient 1.1*100=110, should be POS
        assert result["consensus"] == Trit(Trit.POS)
        # Adversarial
        result = AdversarialScenario("adversarial").run(triplex, lattice)
        assert result["consensus"] == Trit(Trit.NEG)
        print("Tests passed")
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    # main()  # Uncomment to run CLI
    test_simulator()