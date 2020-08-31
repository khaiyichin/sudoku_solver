import numpy as np

class Row(object):
    # Add Row class here, should be similar with Grid
    def __init__(self, num):
        # _n describes the number of cells in the longest dimension of a class
        self._n = int(num)
        self._dim = (1, self._n)
        self._complete_vals = np.full(self._n, False)

    def populate(self, cell_arr):
        self._cells = cell_arr
    
    def get_dim(self):
        return self._dim

    def get_values(self):
        values = np.empty(self._n, int)

        for i in range(self._n):
            values[0][i] = self._cells[0][i].get_value()

        return values

    def get_value_prob(self, value):
        # Get the probability array for this row for a particular value
        prob_arr = np.empty(self._dim)
        
        for i in range(self._n):
            prob_arr[0][i] = self._cells[0][i].get_value_prob(value)

        return prob_arr

    def evaluate_value_prob(self, value):
        if (self._complete_vals[value-1]): return

        # Evaluate and reassign probability
        prob_arr = self.get_value_prob(value)

        # Get the number of unknowns in the grid
        # While this would also include instances of 1.0 in the array,
        # the if loop below doesn't use it if 1.0 is encountered
        unknowns = float(np.count_nonzero(prob_arr != 0.0))

        # Check if value exists in row
        if 1.0 in prob_arr:
            for i in range(self._n):
                if self._cells[0][i].get_value_prob(value) != 1.0:
                    self._cells[0][i].set_value_prob(value, 0.0)

            self._complete_vals[value-1] = True
        else: # value doesn't exist in the row
            for i in range(self._n):
                if self._cells[0][i].get_value_prob(value) != 0.0:
                    self._cells[0][i].set_value_prob(value, 1.0 / unknowns)
                    
            if unknowns == 1.0: self._complete_vals[value-1] = True