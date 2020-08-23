import numpy as np
from cell import Cell

class Grid:
    def __init__(self, num):
        # _n describes the number of cells in the longest dimension of a class
        self._n = int(num)
        self._dim = (self._n, self._n)

    def populate(self, cell_arr):
        self._cells = cell_arr

    def get_dim(self):
        """Get the dimensions of the grid.
        """
        return self._dim

    def get_values(self):
        """Get all the values in the grid.
        """
        values = np.empty(self._dim, int)

        for i in range(self._n):
            for j in range(self._n):
                values[i][j] = self._cells[i][j].get_value()

        return values