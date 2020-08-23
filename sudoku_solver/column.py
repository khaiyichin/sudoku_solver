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

    def populate(self, cell_arr):
        self._cells = cell_arr
    
    def get_dim(self):
        return self._dim

    def get_values(self):
        values = np.empty(self._dim, int)

        for i in range(self._n):
            values[i] = self._cells[i][0].get_value()

        return values