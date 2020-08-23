import numpy as np
from cell import Cell

class Grid:
    def __init__(self, num):
        # _n describes the number of cells in the longest dimension of a class
        self._n = int(num)
        self._dim = (self._n, self._n)
        self._complete_vals = np.full(sum(self._dim), False)

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
    
    def get_value_prob(self, value):
        # Get the probability array for this grid for a particular value
        prob_arr = np.empty(self._dim)

        for i in range(self._n):
            for j in range(self._n):
                prob_arr[i][j] = self._cells[i][j].get_value_prob(value)

        return prob_arr

    def evaluate_value_prob(self, value):
        if (self._complete_vals[value-1]): return
        
        # Evaluate and reassign probability
        prob_arr = self.get_value_prob(value)

        # Get the number of unknowns in the grid
        unknowns = float(np.count_nonzero(prob_arr != 0.0))
        
        if 1.0 in prob_arr: # value exists in the grid already
            for i in range(self._dim[0]):
                for j in range(self._dim[1]):
                    if self._cells[i][j].get_value_prob(value) != 1.0:
                        self._cells[i][j].set_value_prob(value, 0.0)
            
            self._complete_vals[value-1] = True

        else: # value doesn't exist in the grid
            for i in range(self._dim[0]):
                for j in range(self._dim[1]):
                    if self._cells[i][j].get_value_prob(value) != 0.0:
                        self._cells[i][j].set_value_prob(value, 1.0 / unknowns)
                        
            if unknowns == 1.0: self._complete_vals[value-1] = True