"""
Implement the Triplex Redundancy Layer for the μInference Ternary seL4 Simulator.
Follow ARCHITECTURE.md: Class for three actors evaluating inputs against parameters, with judge for consensus in trit space.
Integrate with ternary.py (use Trit ops) and lattice.py (feed evaluations to lattice if needed).
Pluggable evaluators (e.g., callback functions for custom logic).
Methods: evaluate_input (per actor), compute_consensus (trit voting: majority +1 executes, quarantine on 0 or -1 conflicts).
Docstrings, type hints, modularity.
Unit tests: consensus on clean inputs (+1 all executes), mixed (quarantine), adversarial (-1 rejects).
Example: Three actors agree on +1 -> execute; one 0 -> quarantine.
"""

from enum import Enum
from typing import Callable, List
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ternary import Trit, trit_and, trit_or, trit_not  # Assuming imports from ternary.py
from parameters import ParameterProvider

class TriplexActor:
    def __init__(self, evaluator: Callable[[any, ParameterProvider, str], Trit]):
        self.evaluator = evaluator

    def evaluate(self, input_data: any, provider: ParameterProvider, phase: str) -> Trit:
        return self.evaluator(input_data, provider, phase)

class TriplexSystem:
    def __init__(self, evaluators: List[Callable[[any, ParameterProvider, str], Trit]], provider: ParameterProvider, phase: str = "nominal"):
        if len(evaluators) != 3:
            raise ValueError("Exactly three evaluators required")
        self.actors = [TriplexActor(e) for e in evaluators]
        self.provider = provider
        self.phase = phase

    def evaluate_input(self, input_data: any) -> List[Trit]:
        return [actor.evaluate(input_data, self.provider, self.phase) for actor in self.actors]

    def evaluate_input(self, input_data: any) -> List[Trit]:
        return [actor.evaluate(input_data) for actor in self.actors]

    def compute_consensus(self, evaluations: List[Trit]) -> Trit:
        # Majority voting: +1 if at least two +1, -1 if at least two -1, 0 otherwise (quarantine)
        count_pos = sum(1 for t in evaluations if t == Trit.POS)
        count_neg = sum(1 for t in evaluations if t == Trit.NEG)
        if count_pos >= 2:
            return Trit(Trit.POS)
        elif count_neg >= 2:
            return Trit(Trit.NEG)
        else:
            return Trit(Trit.ZERO)

# Unit tests (using built-in assert for simplicity; replace with pytest)
def test_consensus():
    try:
        provider = ParameterProvider("parameters.json")
        # Clean: all +1
        evaluators = [lambda inp, p, ph: Trit(Trit.POS)] * 3
        triplex = TriplexSystem(evaluators, provider, "nominal")
        evals = triplex.evaluate_input({"temp": 50})
        assert triplex.compute_consensus(evals) == Trit(Trit.POS)
        # Mixed: quarantine
        evaluators = [lambda inp, p, ph: Trit(Trit.POS), lambda inp, p, ph: Trit(Trit.ZERO), lambda inp, p, ph: Trit(Trit.POS)]
        triplex = TriplexSystem(evaluators, provider, "nominal")
        evals = triplex.evaluate_input({"temp": 50})
        assert triplex.compute_consensus(evals) == Trit(Trit.ZERO)
        # Adversarial: reject
        evaluators = [lambda inp, p, ph: Trit(Trit.NEG)] * 3
        triplex = TriplexSystem(evaluators, provider, "nominal")
        evals = triplex.evaluate_input({"temp": 50})
        assert triplex.compute_consensus(evals) == Trit(Trit.NEG)
        print("Tests passed")
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_consensus()