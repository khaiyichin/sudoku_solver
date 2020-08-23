import numpy as np

class Row(object):
    # Add Row class here, should be similar with Grid
    def __init__(self, num):
        # _n describes the number of cells in the longest dimension of a class
        self._n = int(num)
        self._dim = (1, self._n)

    def populate(self, cell_arr):
        self._cells = cell_arr
    
    def get_dim(self):
        return self._dim

    def get_values(self):
        values = np.empty(self._n, int)

        for i in range(self._n):
            values[i] = self._cells[0][i].get_value()

        return values