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
            
            # reset the probabilities so that they're consistent in grids
            self.evaluate_value_prob(val)
            
            
            # store each values' probabilities
            prob_cache[val-1] = self.get_value_prob(val)


        ### COMPARE PROBABILITIES
        # Compare probabilities by going through prob_cache
        candidate_prob_list = np.empty((1, *self._dim))
        candidate_val = 0
        disqualified_candidates = np.full(num_possible_val, False) # disqualify a candidate if it was similar before, so we don't check them again
        found_similar = False

        for ind in range(len(prob_cache) - 1):
            
            # Disqualify completed probabilities
            if np.any(prob_cache[ind] == 1.0): continue
            elif np.sum(prob_cache[ind]) == 0.0: continue
            elif disqualified_candidates[ind]: continue
            
            candidate_prob_list = [prob_cache[ind]]
            candidate_val = ind + 1
            candidate_val_list = [candidate_val]

            # Compare the candidate probability (prob_cache[ind]) with the rest of the elements in prob_cache
            for i in range(1, num_possible_val - ind):
                
                # It could be the index [ind+i] has been similar to a past probability, which means it's not possible to be the same again.
                # Thus no checking needed
                if disqualified_candidates[ind + i]: continue
                
                # Check to see if the candidate probability is similar to prob_cache[ind+i]
                is_equal = np.all(prob_cache[ind] == prob_cache[ind+i])

                # Store them if it's equal
                if is_equal:
                    candidate_prob_list = np.append(candidate_prob_list, [prob_cache[ind + i]], axis = 0)
                    candidate_val_list = np.append(candidate_val_list, ind+i+1)
                    disqualified_candidates[ind + i] = True
                    is_equal = False
                    found_similar = True

            # if none compared to be similar, move on
            if not found_similar: continue
            else:
                found_similar = False

            # Verify that the candidates pass all 5 conditions
            # is_equal checks the 1st, 2nd, 3rd conditions, so now we have to check the 4th and 5th condition
            # Only have to check the first candidate
            if np.sum(candidate_prob_list[0]) != 1.0:
                continue
            elif len(candidate_val_list) != np.count_nonzero(candidate_prob_list[0]):
                continue

            # Get index of the candidate cells where the probability is nonzero
            index_array = candidate_prob_list[0] != 0.0


            
            ### REPLACE PROBABILITIES
            # iterate through the non-completed vals to set their probabilites = 0.0 at the index_array position
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
                    
                
            

        # Now that we found list of candidates
        candidate_prob_list[0]

 


        

    def evaluate_value_prob(self, value):
        if (self._complete_vals[value-1]): return
        
        # Evaluate and reassign probability
        prob_arr = self.get_value_prob(value)

        # Get the number of unknowns in the grid
        # While this would also include instances of 1.0 in the array,
        # the if loop below doesn't use it if 1.0 is encountered
        unknowns = float(np.count_nonzero(prob_arr != 0.0))
        
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