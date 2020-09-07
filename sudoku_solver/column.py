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
        self._section_dim = int(np.sqrt(self._n))
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
            prob_arr[i][0] = self._cells[i][0].get_value_prob('col', value)

        return prob_arr

    def evaluate_value_prob(self, value, use_grid_prior=False):

        # Evaluate and reassign probabilities for this column for a particular value
        if (self._complete_vals[value-1]): return

        # Evaluate and reassign probabilities
        prob_arr = self.get_value_prob(value)

        # Get the number of unknowns in the grid
        # While this would also include instances of 1.0 in the array,
        # the if loop below doesn't use it if 1.0 is encountered
        unknowns = float(np.count_nonzero(prob_arr != 0.0))

        # Evaluate the row in sections ONLY if the grid probability evaluation has been done previously
        sections_total_prob_bool = ''

        if use_grid_prior:  
            # Separate the column probabilities into n sections where n is sqrt(self._n)
            prob_arr_sections = np.split(prob_arr, self._section_dim)

            # Get the total probability in each section
            sections_total_prob = np.sum(prob_arr_sections, axis=1)
            sections_total_prob_bool = np.array(sections_total_prob == 1.0)
            # print(sections_total_prob)
        else:
            sections_total_prob_bool = False

        # Check if value exists in column
        if 1.0 in prob_arr:
            for i in range(self._n):
                if self._cells[i][0].get_value_prob('col', value) != 1.0:
                    self._cells[i][0].set_value_prob('col', value, 0.0)

            self._complete_vals[value-1] = True

        elif np.any(sections_total_prob_bool) and use_grid_prior: # check to see if any of the sections contain a confirmed value
            # Remove all the other section values
            for i in np.nonzero(np.invert(sections_total_prob_bool))[0]: # iterate through the non-1.0 section indices
                for j in range(self._section_dim): # iterate within each section
                    self._cells[i*3 + j][0].set_value_prob('col', value, 0.0)

        else: # value doesn't exist in the column
            for i in range(self._n):
                if self._cells[i][0].get_value_prob('col', value) != 0.0:
                    self._cells[i][0].set_value_prob('col', value, 1.0 / unknowns)
            
            if unknowns == 1.0: self._complete_vals[value-1] = True