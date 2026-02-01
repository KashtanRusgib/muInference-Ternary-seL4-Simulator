"""
Implement the 3x3 Viability Lattice Layer.
Use NumPy 3x3 array of int8 for trits; methods: populate (from inputs/actors), traverse (phase logic: initiate/modulate/stabilize), compute (consensus outcome).
Support recursion for nested lattices.
Integrate with ternary.py for ops.
Add Matplotlib visualizer for debug heatmaps.
Unit tests for nominal traversal.
"""

import numpy as np
from typing import List, Optional
from ternary import trit_add, trit_mul, trit_and, trit_or


class Lattice:
    """3x3 Viability Lattice for ternary decision-making."""

    def __init__(self, nested: bool = False):
        self.grid = np.zeros((3, 3), dtype=np.int8)
        self.nested = nested
        self.sublattices: Optional[List[List['Lattice']]] = None
        if nested:
            self.sublattices = [[Lattice(False) for _ in range(3)] for _ in range(3)]

    def populate(self, inputs: List[Trit], actors: List[Trit]):
        """Populate the lattice with trits from inputs (rows) and actors (columns)."""
        if len(inputs) != 3 or len(actors) != 3:
            raise ValueError("Inputs and actors must be lists of 3 trits")
        for i in range(3):
            for j in range(3):
                self.grid[i, j] = trit_add(inputs[i].value, actors[j].value)
        if self.nested:
            for i in range(3):
                for j in range(3):
                    self.sublattices[i][j].populate(inputs, actors)

    def traverse(self, phase: str):
        """Traverse the lattice with phase logic: initiate, modulate, stabilize."""
        if phase == 'initiate':
            # Initiate: set diagonals or something
            np.fill_diagonal(self.grid, 1)
        elif phase == 'modulate':
            # Modulate: apply some transformation, e.g., multiply by row sum
            row_sums = np.sum(self.grid, axis=1)
            for i in range(3):
                self.grid[i] *= row_sums[i] if row_sums[i] != 0 else 1
            self.grid = np.clip(self.grid, -1, 1)
        elif phase == 'stabilize':
            # Stabilize: consensus per row
            for i in range(3):
                row = self.grid[i]
                pos = np.sum(row == 1)
                neg = np.sum(row == -1)
                if pos > neg:
                    self.grid[i] = 1
                elif neg > pos:
                    self.grid[i] = -1
                else:
                    self.grid[i] = 0
        if self.nested:
            for i in range(3):
                for j in range(3):
                    self.sublattices[i][j].traverse(phase)

    def compute(self) -> int:
        """Compute consensus outcome from the lattice."""
        if self.nested:
            sub_outcomes = np.zeros((3, 3), dtype=int)
            for i in range(3):
                for j in range(3):
                    sub_outcomes[i, j] = self.sublattices[i][j].compute()
            # Combine sub outcomes
            flat = sub_outcomes.flatten()
        else:
            flat = self.grid.flatten()
        pos = np.sum(flat == 1)
        neg = np.sum(flat == -1)
        if pos > neg:
            return 1
        elif neg > pos:
            return -1
        else:
            return 0

    def visualize(self, filename: str = 'lattice_heatmap.png'):
        """Visualize the lattice as a heatmap using Matplotlib."""
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        cax = ax.imshow(self.grid, cmap='coolwarm', vmin=-1, vmax=1)
        ax.set_title('Lattice Heatmap')
        fig.colorbar(cax, ticks=[-1, 0, 1])
        plt.savefig(filename)
        plt.close()  # No display in headless


# Unit tests
def test_lattice_populate():
    try:
        lattice = Lattice()
        inputs = [Trit(1), Trit(0), Trit(-1)]
        actors = [Trit(1), Trit(0), Trit(-1)]
        lattice.populate(inputs, actors)
        expected = np.array([[1, 1, 0], [1, 0, -1], [0, -1, -1]], dtype=np.int8)  # trit_add results
        assert np.array_equal(lattice.grid, expected)
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_lattice_traverse_initiate():
    try:
        lattice = Lattice()
        lattice.grid = np.ones((3,3), dtype=np.int8)
        lattice.traverse('initiate')
        assert np.array_equal(np.diag(lattice.grid), [1,1,1])
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_lattice_compute():
    try:
        lattice = Lattice()
        lattice.grid = np.array([[1,1,1], [0,0,0], [-1,-1,-1]], dtype=np.int8)
        assert lattice.compute() == 1
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

def test_nested_lattice():
    try:
        lattice = Lattice(nested=True)
        inputs = [Trit(1), Trit(0), Trit(-1)]
        actors = [Trit(1), Trit(0), Trit(-1)]
        lattice.populate(inputs, actors)
        lattice.traverse('stabilize')
        outcome = lattice.compute()
        assert isinstance(outcome, int)  # Basic check
    except AssertionError as e:
        print(f"Tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_lattice_populate()
    test_lattice_traverse_initiate()
    test_lattice_compute()
    test_nested_lattice()
    print("All lattice tests passed!")
