import numpy as np
from cell import Cell

class Grid:
    def __init__(self, num):
        # _n describes the number of cells in the longest dimension of a class
        self._n = int(num)
        self._dim = (self._n, self._n)
        self._complete_vals = np.full(np.prod(self._dim), False)

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

        for i in range(self._dim[0]):
            for j in range(self._dim[1]):
                values[i][j] = self._cells[i][j].get_value()

        return values
    
    def get_value_prob(self, value):
        # Get the probability array for this grid for a particular value
        prob_arr = np.empty(self._dim)

        for i in range(self._dim[0]):
            for j in range(self._dim[1]):
                prob_arr[i][j] = self._cells[i][j].get_value_prob('grid', value)

        return prob_arr

    # find a better name
    # This strategy identifies values that can only exist in a set of locations in the grid (which is
    # a subset of the grid) and cancels other probabilities from said set of locations.
    # For example, if the values 1 & 2 are confined to either cells A & B (and nowhere else in the grid),
    # then the other values that has a nonzero probability to be in cells A & B are removed (i.e., probability is
    # now 0) 
    def strategy_3(self):

        num_possible_val = self._n ** 2



        ### STORE PROBABILITIES
        # Store probabilities of each value in grid form
        prob_cache = np.empty((num_possible_val, *self._dim))
        for val in range(1, num_possible_val+1):
            
            # Only evaluate those incomplete; assign those complete with all ones so that we can disqualify them later
            if self._complete_vals[val-1]:
                prob_cache[val-1] = np.ones(self._dim)
                continue            
            
            # reset the probabilities so that the grid probabilities are consistent (do we need this, now that we have multiple probabilites stored by Cell?)
            self.evaluate_value_prob(val)
            
            
            # store each values' probabilities
            prob_cache[val-1] = self.get_value_prob(val)


        ### COMPARE PROBABILITIES
        # Compare probabilities by going through prob_cache
        candidate_prob_list = np.empty((1, *self._dim))
        candidate_val = 0
        disqualified_candidates = np.full(num_possible_val, False) # disqualify a candidate if it was similar before, so we don't check them again
        found_similar = False

        # Go through each value
        for ind in range(len(prob_cache) - 1):
            
            # Disqualify completed probabilities
            if np.any(prob_cache[ind] == 1.0): continue # this value has been confirmed already in the grid
            elif np.sum(prob_cache[ind]) == 0.0: continue # what is this condition for?
            elif disqualified_candidates[ind]: continue # the grid probabilites for this value has been compared already
            
            candidate_prob_list = [prob_cache[ind]] # initialize the list of probabilities from similar candidates
            candidate_val = ind + 1 # the candidate value that its grid probabilities are being compared
            candidate_val_list = [candidate_val] # initialize the list of similar candidates

            # Compare the candidate probability (prob_cache[ind]) with the rest of the elements in prob_cache
            for i in range(1, num_possible_val - ind):
                
                # It could be the index [ind+i] has been similar to a past probability, which means it's not possible to be the same again.
                # Thus no checking needed
                if disqualified_candidates[ind + i]: continue
                
                # Check to see if the candidate probability is similar to prob_cache[ind+i]
                if np.all(prob_cache[ind] == prob_cache[ind+i]):
                    # Store them if it's equal
                    candidate_prob_list = np.append(candidate_prob_list, [prob_cache[ind + i]], axis = 0) # add the probability to the list containing similar probabilities
                    candidate_val_list = np.append(candidate_val_list, ind+i+1) # add to the list of similar candidates
                    disqualified_candidates[ind + i] = True # mark the candidate value as checked
                    found_similar = True

            # if none compared to be similar, move on
            if not found_similar: continue
            else:
                found_similar = False

            # Verify that the candidates pass all 5 conditions
            # is_equal checks the 1st, 2nd, 3rd conditions, so now we have to check the 4th and 5th condition
            # Only have to check the first candidate since all the others are supposed to be identical
            if np.sum(candidate_prob_list[0]) != 1.0:
                continue
            elif len(candidate_val_list) != np.count_nonzero(candidate_prob_list[0]):
                continue

            # Get index of the candidate cells where the probability is nonzero
            index_array = candidate_prob_list[0] != 0.0


            
            ### REPLACE PROBABILITIES
            # iterate through the other non-completed vals to set their probabilites = 0.0 at the index_array position
            for val in range(1, num_possible_val):
                
                if val in candidate_val_list or self._complete_vals[val-1]: continue
                else:
                    # Iterate through each cell to set probabilities
                    for i in range(self._dim[0]):
                        for j in range(self._dim[1]):
                            if index_array[i][j]:
                                self._cells[i][j].set_value_prob('grid', val, 0.0)
                                self._cells[i][j].set_value_prob('row', val, 0.0)
                                self._cells[i][j].set_value_prob('col', val, 0.0)
                                self._cells[i][j].set_value_prob('board', val, 0.0)
            
        self.naked_strategy()

 

    # apply the partial naked  strategy for grid only
    # this naked strategy works for naked pairs, triplets, quads, but may not be complete.
    # Need to be able to pop the last possible values (see *** last_added_cell_ind below)
    def naked_strategy(self):

        '''
        identical_prob_list = ''
        identical_prob_ind_list = ''
        found_identical = False

        for i in range(self._dim[0]):
            for j in range(self._dim[1]):

                if self._cells[i][j].get_value() != 0: continue # the cell has already been filled


                prob_pool = []
                prob_1 = self._cells[i][j].get_prob_array('grid')
                prob_bool_1 = prob_1 != 0.0 # get boolean form
                identical_prob_list = [prob_bool_1]
                identical_prob_ind_list = np.array( [ [i, j] ] )


                # Compare with the remaining of the cells
                for k in range(self._dim[0]):
                    for l in range(self._dim[1]):

                        if (k*self._n + l) <= (i*self._n + j): continue # only compare cells that haven't been compared

                        prob_2 = self._cells[k][l].get_prob_array('grid')
                        prob_bool_2 = prob_2 != 0.0

                        # Compare the probability
                        if np.all(prob_bool_1 == prob_bool_2):
                            found_identical = True
                            identical_prob_list = np.append(identical_prob_list, [prob_bool_2], axis = 0) # store the grid probability of the cell
                            identical_prob_ind_list = np.append(identical_prob_ind_list, [ [k, l] ], axis = 0) # store the position of the cell

                # Verify the number of identical cells is the same as the number of probability occurences
                if found_identical and len(identical_prob_list) == np.count_nonzero(prob_bool_1):
                    
                    # Replace the probabilities
                    for m in range(self._dim[0]):
                        for n in range(self._dim[1]):

                            # Only modify probabilities not part of the identical_prob_ind_list cells
                            if np.any( np.all( np.isin(identical_prob_ind_list, [m, n]), axis = 1 ) ): continue # this checks if the indices [m, n] are part of identical_prob_ind_list
                            else:
                            
                                # Get all the values that their probabilities are to be replaced
                                values = np.where(prob_bool_1)[0] + 1

                                for val in values:
                                    self._cells[m][n].set_value_prob('grid', val, 0.0)
                                    self._cells[m][n].set_value_prob('col', val, 0.0)
                                    self._cells[m][n].set_value_prob('row', val, 0.0)

                else: continue

                found_identical = False

        '''
        

        '''IMPROVED IMPLEMENTATION, WORKS FOR NAKED PAIRS, TRIPLETS, QUADS'''
        found_naked = False

        for i in range(self._dim[0]):
            for j in range(self._dim[1]):

                if self._cells[i][j].get_value() != 0: continue # the cell has already been filled

                # Find the nonzero probabilities in the current cell
                prob = self._cells[i][j].get_prob_array('grid')
                possible_vals_in_cell = np.where(prob != 0.0)[0] + 1                

                possible_val_pool = possible_vals_in_cell
                cell_ind_list = np.array( [ [i, j] ] )

                # Compare with the remaining of the cells
                for k in range(self._dim[0]):
                    for l in range(self._dim[1]):

                        if (k*self._n + l) <= (i*self._n + j): continue # only compare cells that haven't been compared

                        prob = self._cells[k][l].get_prob_array('grid')
                        possible_vals_in_cell = np.where(prob != 0.0)[0] + 1

                        # first check if there number of overlapping values between possible_val_pool and possible_vals_in_cell
                        num_overlapping_vals = np.count_nonzero( np.isin(possible_val_pool, possible_vals_in_cell) )
                        num_new_possible_vals = len(possible_val_pool) + len(possible_vals_in_cell) - num_overlapping_vals

                        if num_overlapping_vals == 0: continue
                        # then check if the addition into the pool will exceed 4
                        elif (num_new_possible_vals > 4): continue # we take naked quads as the max for now; will need proof as we expand grid size 
                        
                        # Check for non-overlapping values
                        new_possible_vals = np.invert(np.isin(possible_vals_in_cell, possible_val_pool))
                        possible_val_pool = np.append(possible_val_pool, possible_vals_in_cell[new_possible_vals]) # add to the pool of possible values
                        cell_ind_list = np.append(cell_ind_list, [ [k, l] ], axis = 0)

                        '''***'''
                        last_added_cell_ind = (k, l) # remember the position of cell that we last took its values

                        # Check if the number of possible values in the pool is the same as the number of possible 'naked' cells
                        if len(possible_val_pool) == len(cell_ind_list):
                            found_naked = True
                            break

                
                if found_naked:
                    
                    # Replace the probabilities
                    for m in range(self._dim[0]):
                        for n in range(self._dim[1]):

                            # Only modify probabilities not part of the cell_ind_list cells
                            if np.any( np.all( np.isin(cell_ind_list, [m, n]), axis = 1 ) ): continue # this checks if the indices [m, n] are part of cell_ind_list
                            else:
                            
                                # Get all the values that their probabilities are to be replaced
                                for val in possible_val_pool:
                                    self._cells[m][n].set_value_prob('grid', val, 0.0)
                                    self._cells[m][n].set_value_prob('col', val, 0.0)
                                    self._cells[m][n].set_value_prob('row', val, 0.0)

                else: continue

    def evaluate_value_prob(self, value):
        if (self._complete_vals[value-1]): return
        
        # Evaluate and reassign probability
        prob_arr = self.get_value_prob(value)

        # Get the number of unknowns in the grid
        # While this would also include instances of 1.0 in the array,
        # the if loop below doesn't use it if 1.0 is encountered
        unknowns = float(np.count_nonzero(prob_arr != 0.0))
        print('DEBUG GRD', unknowns)
        
        # Check if value exists in grid
        if 1.0 in prob_arr:
            for i in range(self._dim[0]):
                for j in range(self._dim[1]):
                    if self._cells[i][j].get_value_prob('grid', value) != 1.0:
                        self._cells[i][j].set_value_prob('grid', value, 0.0)
            
            self._complete_vals[value-1] = True
        else: # value doesn't exist in the grid
            for i in range(self._dim[0]):
                for j in range(self._dim[1]):
                    if self._cells[i][j].get_value_prob('grid', value) != 0.0:
                        self._cells[i][j].set_value_prob('grid', value, 1.0 / unknowns)
                        
            if unknowns == 1.0: self._complete_vals[value-1] = True