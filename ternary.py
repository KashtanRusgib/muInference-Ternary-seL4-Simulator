"""
Implement the Ternary Logic Layer for the μInference Ternary seL4 Simulator project.
Follow ARCHITECTURE.md: Pure Python module for trit states (-1/0/+1 balanced ternary) and operations.
Use Enum or class for Trit with methods for basic logic (AND, OR, NOT) based on Kleene three-valued logic for 'unknown' (0).
Add arithmetic (add, mul) with trit bounds to prevent overflow.
Integrate NumPy for vectorized operations on trit arrays (e.g., for lattice efficiency).
Include docstrings, type hints, and ensure modularity with an abstract base class TernaryEmulator for future swaps.
Add unit test stubs at the bottom (using pytest).
Example: trit_and(-1, 0) should return -1; trit_not(1) should return -1.
"""

from abc import ABC, abstractmethod
from typing import Union, List
import numpy as np


class TernaryEmulator(ABC):
    """Abstract base class for ternary logic emulators to allow future swaps."""

    @abstractmethod
    def trit_and(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def trit_or(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def trit_not(self, a: int) -> int:
        pass

    @abstractmethod
    def trit_add(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def trit_mul(self, a: int, b: int) -> int:
        pass


class Trit:
    """Represents a trit in balanced ternary: -1 (False), 0 (Unknown), 1 (True)."""
    POS = Trit(1)
    ZERO = Trit(0)
    NEG = Trit(-1)

    def __init__(self, value: int):
        if value not in [-1, 0, 1]:
            raise ValueError("Trit value must be -1, 0, or 1")
        self.value = value

    def __repr__(self) -> str:
        return f"Trit({self.value})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Trit):
            return self.value == other.value
        return self.value == other

    def __and__(self, other: Union['Trit', int]) -> 'Trit':
        b = other.value if isinstance(other, Trit) else other
        return Trit(trit_and(self.value, b))

    def __or__(self, other: Union['Trit', int]) -> 'Trit':
        b = other.value if isinstance(other, Trit) else other
        return Trit(trit_or(self.value, b))

    def __invert__(self) -> 'Trit':
        return Trit(trit_not(self.value))

    def __add__(self, other: Union['Trit', int]) -> 'Trit':
        b = other.value if isinstance(other, Trit) else other
        return Trit(trit_add(self.value, b))

    def __mul__(self, other: Union['Trit', int]) -> 'Trit':
        b = other.value if isinstance(other, Trit) else other
        return Trit(trit_mul(self.value, b))


class BalancedTernaryEmulator(TernaryEmulator):
    """Concrete implementation of ternary emulator using balanced ternary logic."""

    def trit_and(self, a: int, b: int) -> int:
        """Kleene AND: False dominates."""
        if a == -1 or b == -1:
            return -1
        elif a == 1 and b == 1:
            return 1
        else:
            return 0

    def trit_or(self, a: int, b: int) -> int:
        """Kleene OR: True dominates."""
        if a == 1 or b == 1:
            return 1
        elif a == -1 and b == -1:
            return -1
        else:
            return 0

    def trit_not(self, a: int) -> int:
        """Kleene NOT: flips True and False, Unknown stays."""
        if a == 1:
            return -1
        elif a == -1:
            return 1
        else:
            return 0

    def trit_add(self, a: int, b: int) -> int:
        """Trit addition with bounds to prevent overflow."""
        s = a + b
        if s > 1:
            return 1
        elif s < -1:
            return -1
        else:
            return s

    def trit_mul(self, a: int, b: int) -> int:
        """Trit multiplication, naturally bounded."""
        return a * b


# Standalone functions for convenience
def trit_and(a: int, b: int) -> int:
    return BalancedTernaryEmulator().trit_and(a, b)

def trit_or(a: int, b: int) -> int:
    return BalancedTernaryEmulator().trit_or(a, b)

def trit_not(a: int) -> int:
    return BalancedTernaryEmulator().trit_not(a)

def trit_add(a: int, b: int) -> int:
    return BalancedTernaryEmulator().trit_add(a, b)

def trit_mul(a: int, b: int) -> int:
    return BalancedTernaryEmulator().trit_mul(a, b)


# NumPy vectorized operations
def trit_and_array(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Vectorized AND for trit arrays."""
    result = np.full_like(a, -1, dtype=int)
    result[(a == 1) & (b == 1)] = 1
    result[~((a == 1) & (b == 1)) & ~((a == -1) | (b == -1))] = 0
    return result

def trit_or_array(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Vectorized OR for trit arrays."""
    result = np.full_like(a, 1, dtype=int)
    result[(a == -1) & (b == -1)] = -1
    result[~((a == 1) | (b == 1)) & ~((a == -1) & (b == -1))] = 0
    return result

def trit_not_array(a: np.ndarray) -> np.ndarray:
    """Vectorized NOT for trit arrays."""
    result = np.copy(a)
    result[a == 1] = -1
    result[a == -1] = 1
    # 0 stays 0
    return result

def trit_add_array(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Vectorized ADD with clamping."""
    return np.clip(a + b, -1, 1)

def trit_mul_array(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Vectorized MUL."""
    return a * b


# Unit tests
import pytest

def test_trit_and():
    try:
        assert trit_and(-1, 0) == -1
        assert trit_and(1, 1) == 1
        assert trit_and(0, 0) == 0
        assert trit_and(1, -1) == -1
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_trit_or():
    try:
        assert trit_or(1, 0) == 1
        assert trit_or(-1, -1) == -1
        assert trit_or(0, 0) == 0
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_trit_not():
    try:
        assert trit_not(1) == -1
        assert trit_not(-1) == 1
        assert trit_not(0) == 0
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_trit_add():
    try:
        assert trit_add(1, 1) == 1  # clamped
        assert trit_add(-1, -1) == -1
        assert trit_add(1, -1) == 0
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_trit_mul():
    try:
        assert trit_mul(1, 1) == 1
        assert trit_mul(-1, -1) == 1
        assert trit_mul(1, -1) == -1
        assert trit_mul(0, 1) == 0
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_trit_class():
    try:
        t1 = Trit(1)
        t0 = Trit(0)
        assert (t1 & t0) == Trit.ZERO
        assert (t1 | t0) == Trit.POS
        assert (~t1) == Trit.NEG
        assert (t1 + t0) == Trit.POS
        assert (t1 * t0) == Trit.ZERO
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_numpy_ops():
    try:
        a = np.array([1, 0, -1])
        b = np.array([0, 1, -1])
        assert np.array_equal(trit_and_array(a, b), np.array([0, 0, -1]))
        assert np.array_equal(trit_or_array(a, b), np.array([1, 1, -1]))
        assert np.array_equal(trit_not_array(a), np.array([-1, 0, 1]))
        assert np.array_equal(trit_add_array(a, b), np.array([1, 1, -1]))
        assert np.array_equal(trit_mul_array(a, b), np.array([0, 0, 1]))
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise


if __name__ == "__main__":
    test_trit_and()
    test_trit_or()
    test_trit_not()
    test_trit_add()
    test_trit_mul()
    test_trit_class()
    test_numpy_ops()
    print("All tests passed!")
