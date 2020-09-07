import numpy as np
import copy as cp

class Cell:
    def __init__(self, num, value = 0):
        self._n = int(num)
        self._val = int(value)
        # Populate the probability arrays
        if self._val == 0:
            self._prob_arrays_dict = \
                {
                    'grid': np.full(self._n, -1.0),
                    'row': np.full(self._n, -1.0),
                    'col': np.full(self._n, -1.0),
                    'board': np.full(self._n, -1.0)
                }
        else:
            self._prob_arrays_dict = \
                {
                    'grid': np.full(self._n, 0.0),
                    'row': np.full(self._n, 0.0),
                    'col': np.full(self._n, 0.0),
                    'board': np.full(self._n, -0.0)
                }
            
            for prob_type in self._prob_arrays_dict.keys():
                self._prob_arrays_dict[prob_type][self._val-1] = 1.0

    def get_value(self):
        return self._val

    def get_value_prob(self, prob_type, value):
        # Remove 1 off the value to convert it into index
        return self._prob_arrays_dict[prob_type][value-1]

    def set_value(self, value):
        self._val = int(value)

    def set_value_prob(self, prob_type, value, prob):
        # Remove 1 off the value to convert it into index
        self._prob_arrays_dict[prob_type][value-1] = prob

    def get_prob_array(self, prob_type):
        return self._prob_arrays_dict[prob_type]

    def check_and_reset_probabilities(self):
        # Synchronize all the board and board group probabilities
        combined_prob = self._prob_arrays_dict['board'] * self._prob_arrays_dict['grid'] * self._prob_arrays_dict['row'] * self._prob_arrays_dict['col']
        
        # Probabilities greater than 1 means that the value has been confirmed by at least on board group
        # Reset any probabilities greater than 1.0 to 1.0
        combined_prob[combined_prob > 1.0] = 1.0

        # Reset and update the probabilities across different board groups
        for prob_type in self._prob_arrays_dict.keys():
            self._prob_arrays_dict[prob_type] = combined_prob

            confirmed_num = np.count_nonzero(combined_prob == 1.0)

            if confirmed_num > 1: print('ERROR! Cell has more than one value according to its probability array.')
            elif confirmed_num == 1:
                self._prob_arrays_dict[prob_type][(combined_prob > 0.0) & (combined_prob < 1.0)] = 0.0

            # If there are no other possibilities, that means the only number that has a probability is the confirmed value
            nonzeros = np.count_nonzero(combined_prob)
            if nonzeros == 1:
                self._prob_arrays_dict[prob_type][combined_prob != 0.0] = 1.0