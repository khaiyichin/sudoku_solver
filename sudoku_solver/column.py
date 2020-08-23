import numpy as np

class Column(object):
    # Add Column class here, should be similar with Grid
    def __init__(self, num):
        '''

        num: number of cells within the Column class
        '''
        # _n describes the number of cells in the longest dimension of a class
        self._n = int(num)
        self._dim = (self._n, 1)
        self._complete_vals = np.full(self._n, False)

    def populate(self, cell_arr):
        self._cells = cell_arr
    
    def get_dim(self):
        return self._dim

    def get_values(self):
        values = np.empty(self._dim, int)

        for i in range(self._n):
            values[i][0] = self._cells[i][0].get_value()

        return values

    def get_value_prob(self, value):
        # Get the probability array for this column for a particular value
        prob_arr = np.empty(self._dim)

        for i in range(self._n):
            prob_arr[i][0] = self._cells[i][0].get_value_prob(value)

        return prob_arr

    def evaluate_value_prob(self, value):
        # Evaluate and reassign probabilities for this column for a particular value
        if (self._complete_vals[value-1]): return

        # Evaluate and reassign probabilities
        prob_arr = self.get_value_prob(value)

        # Get the number of unknowns in the grid
        unknowns = float(np.count_nonzero(prob_arr != 0.0))

        if 1.0 in prob_arr: # value exists in the column already
            for i in range(self._n):
                if self._cells[i][0].get_value_prob(value) != 1.0:
                    self._cells[i][0].set_value_prob(value, 0.0)

            self._complete_vals[value-1] = True

        else: # value doesn't exist in the column
            for i in range(self._n):
                if self._cells[i][0].get_value_prob(value) != 0.0:
                    self._cells[i][0].set_value_prob(value, 1.0 / unknowns)
            
            if unknowns == 1.0: self._complete_vals[value-1] = True