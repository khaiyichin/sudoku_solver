import numpy as np
from cell import Cell

class Grid:
    def __init__(self, num):
        self._n = num
        # self.cells = np.array( [ [ Cell(num) for _ in range(num) ] for _ in range(num) ] )

    def populate_grid(self, cell_arr):
        self.cells = cell_arr

    def get_grid_dim(self):
        """Get the dimensions of the grid.
        """
        return self.cells.shape

    def get_values(self):
        """Get all the values in the grid.
        """
        return self.cells

    def get_value_prob(self, value):
        """Get the probability matrix for a grid for a particular value.

        Args:
            value: The value of interest.

        Returns:
            A matrix of probabilities for the value.
        """
        
        # The index starts from 0
        ind = value - 1
        grid_prob = np.zeros(self.get_grid_dim())

        # Iterate through all the cells to obtain the probabilities
        for i in range(self._n):
            for j in range(self._n):
                grid_prob[i][j] = self.cells[i][j].get_prob_array()[ind]

        return grid_prob