"""
Implement the Parameter Store Layer for the μInference Ternary seL4 Simulator.
Follow ARCHITECTURE.md: Simulates core rope memory with JSON/YAML loader for hardcoded safe values/gradients (e.g., dict of bounds: {'voltage': (min, max, gradient_factor)}).
Enforce immutability via frozen dataclasses (Python 3.7+ stdlib).
Interface ParameterProvider for swappability (e.g., to database).
Methods: load_parameters (from file), get_bound (for key), is_within_bound (input vs. bound with gradient).
Docstrings, type hints.
Unit tests: Load JSON, check immutability, bound validation.
Example: Load {'temp': (0, 100, 1.1)} -> is_within_bound(50, 'temp') = Trit.POS; extreme with gradient.
"""

from dataclasses import dataclass, asdict, is_dataclass
from typing import Dict, Tuple
import json
import os
from ternary import Trit  # For bound checks returning trits

@dataclass(frozen=True)
class ParameterBound:
    min_val: float
    max_val: float
    gradient_factor: float

class ParameterProvider:
    def __init__(self, file_path: str = None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'parameters.json')
        self.parameters = self.load_parameters(file_path)

    def load_parameters(self, file_path: str) -> Dict[str, ParameterBound]:
        absolute_path = os.path.join(os.path.dirname(__file__), file_path)
        with open(absolute_path, 'r') as f:
            data = json.load(f)
        return {k: ParameterBound(**v) for k, v in data.items()}

    def get_bound(self, key: str) -> ParameterBound:
        return self.parameters[key]

    def is_within_bound(self, value: float, key: str, apply_gradient: bool = False) -> Trit:
        bound = self.get_bound(key)
        effective_min = bound.min_val
        effective_max = bound.max_val
        if apply_gradient:
            effective_min *= bound.gradient_factor
            effective_max *= bound.gradient_factor
        if value < effective_min:
            return Trit(Trit.NEG)
        elif value > effective_max:
            return Trit(Trit.NEG)
        else:
            return Trit(Trit.POS)

# Unit tests
def test_parameters():
    try:
        # Mock JSON file - in real, write to temp file
        mock_data = {"temp": {"min_val": 0, "max_val": 100, "gradient_factor": 1.1}}
        with open("test_params.json", "w") as f:
            json.dump(mock_data, f)
        provider = ParameterProvider("test_params.json")
        assert provider.is_within_bound(50, "temp") == Trit(Trit.POS)
        assert provider.is_within_bound(110, "temp", apply_gradient=True) == Trit(Trit.POS)  # 100*1.1=110
        assert provider.is_within_bound(120, "temp", apply_gradient=True) == Trit(Trit.NEG)
        print("Tests passed")
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_parameters()