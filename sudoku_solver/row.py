import numpy as np

class Row(object):
    # Add Row class here, should be similar with Grid
    def __init__(self, num):
        # _n describes the number of cells in the longest dimension of a class
        self._n = int(num)
        self._dim = (1, self._n)
        self._section_dim = int(np.sqrt(self._n))
        self._complete_vals = np.full(self._n, False)

    def populate(self, cell_arr):
        self._cells = cell_arr
    
    def get_dim(self):
        return self._dim

    def get_values(self):
        values = np.empty(self._n, int)

        for i in range(self._n):
            values[i] = self._cells[0][i].get_value()

        return values

    def get_value_prob(self, value):
        # Get the probability array for this row for a particular value
        prob_arr = np.empty(self._dim)
        
        for i in range(self._n):
            prob_arr[0][i] = self._cells[0][i].get_value_prob('row', value)

        return prob_arr

    # apply the naked pairs strategy for row only
    def naked_strategy(self):
        found_naked = False

        for i in range(self._n):

                if self._cells[0][i].get_value() != 0: continue # the cell has already been filled
                # Find the nonzero probabilities in the current cell
                prob = self._cells[0][i].get_prob_array('row')
                possible_vals_in_cell = np.where(prob != 0.0)[0] + 1                

                possible_val_pool = possible_vals_in_cell
                cell_ind_list = np.array( [ i ] )
                
                print('DEBUG i =',i, cell_ind_list, possible_val_pool)

                # Compare with the remaining of the cells
                for j in range(self._n):

                        if j <= i: continue # only compare cells that haven't been compared

                        prob = self._cells[0][j].get_prob_array('row')
                        possible_vals_in_cell = np.where(prob != 0.0)[0] + 1

                        # first check if there number of overlapping values between possible_val_pool and possible_vals_in_cell
                        num_overlapping_vals = np.count_nonzero( np.isin(possible_val_pool, possible_vals_in_cell) )
                        num_new_possible_vals = len(possible_val_pool) + len(possible_vals_in_cell) - num_overlapping_vals

                        print('DEBUG RRR', num_overlapping_vals)

                        if num_overlapping_vals == 0: continue
                        # then check if the addition into the pool will exceed 4
                        elif (num_new_possible_vals > 4): continue # we take naked quads as the max for now; will need proof as we expand row size 
                        

                        # BUG HERE: only append values that haven't occurede
                        new_possible_vals = np.invert(np.isin(possible_vals_in_cell, possible_val_pool))
                        print('DEBUG D1 j =',j, possible_val_pool, possible_vals_in_cell)
                        print(new_possible_vals)
                        print('DEBUG D', possible_vals_in_cell[new_possible_vals])
                        
                        

                        possible_val_pool = np.append(possible_val_pool, possible_vals_in_cell[new_possible_vals]) # add to the pool of possible values
                        print('DEBUG SFA', possible_val_pool)
                        cell_ind_list = np.append(cell_ind_list, [j], axis = 0)
                        '''***'''
                        last_added_cell_ind = j # remember the position of cell that we last took its values

                        # Check if the number of possible values in the pool is the same as the number of possible 'naked' cells
                        if len(possible_val_pool) == len(cell_ind_list):
                            found_naked = True
                            break

                
                if found_naked:
                    
                    # Replace the probabilities
                    for k in range(self._n):

                            # Only modify probabilities not part of the cell_ind_list cells
                            # print('DEBUG Q', cell_ind_list, k)
                            # print('DEBUG Q2', np.all( np.isin(cell_ind_list, [k]), axis = 0 ))
                            if np.any( np.all( np.isin(cell_ind_list, [k]), axis = 0 ) ): continue # this checks if the index k is part of cell_ind_list
                            else:
                            
                                # Get all the values that their probabilities are to be replaced
                                for val in possible_val_pool:
                                    self._cells[0][k].set_value_prob('grid', val, 0.0)
                                    self._cells[0][k].set_value_prob('col', val, 0.0)
                                    self._cells[0][k].set_value_prob('row', val, 0.0)

                else: continue

    def evaluate_value_prob(self, value, use_grid_prior=False):
        if (self._complete_vals[value-1]): return

        # Evaluate and reassign probability
        prob_arr = self.get_value_prob(value)

        # Get the number of unknowns in the grid
        # While this would also include instances of 1.0 in the array,
        # the if loop below doesn't use it if 1.0 is encountered
        unknowns = float(np.count_nonzero(prob_arr != 0.0))

        # Evaluate the row in sections ONLY if the grid probability evaluation has been done previously
        sections_total_prob_bool = ''

        if use_grid_prior:            
            # Separate the row probabilities into n sections where n is sqrt(self._n)
            prob_arr_sections = np.split(prob_arr[0], self._section_dim)
            
            # Get the total probability in each section
            sections_total_prob = np.sum(prob_arr_sections, axis=1)
            sections_total_prob_bool = np.array(sections_total_prob == 1.0)
        else:
            sections_total_prob_bool = False

        # Check if value exists in row
        if 1.0 in prob_arr:
            for i in range(self._n):
                if self._cells[0][i].get_value_prob('row', value) != 1.0:
                    self._cells[0][i].set_value_prob('row', value, 0.0)

            self._complete_vals[value-1] = True
            
        elif np.any(sections_total_prob_bool) and use_grid_prior: # check to see if any of the sections contain a confirmed value
            # Remove all the other section values
            for i in np.nonzero(np.invert(sections_total_prob_bool))[0]: # iterate through the non-1.0 section indices
                for j in range(self._section_dim): # iterate within each section
                    self._cells[0][i*3 + j].set_value_prob('row', value, 0.0)

        else: # value doesn't exist in the row
            for i in range(self._n):
                if self._cells[0][i].get_value_prob('row', value) != 0.0:
                    self._cells[0][i].set_value_prob('row', value, 1.0 / unknowns)
                    
            if unknowns == 1.0: self._complete_vals[value-1] = True