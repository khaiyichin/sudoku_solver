import numpy as np
import copy as cp

class Cell:
    def __init__(self, num, value = 0):
        self._n = int(num)
        self._val = int(value)
        # Populate the probability array
        if self._val == 0:
            self._prob = np.full(self._n, -1.0)
        else:
            self._prob = np.full(self._n, 0.0)
            self._prob[self._val-1] = 1.0

    def get_value(self):
        return self._val

    def get_value_prob(self, value):
        # Remove 1 off the value to convert it into index
        return self._prob[value-1]

    def set_value(self, value):
        self._val = int(value)

    def set_value_prob(self, value, prob):
        # Remove 1 off the value to convert it into index
        self._prob[value-1] = prob

    def get_prob_array(self):
        return self._prob

    def check_and_reset_probability(self):
        confirmed_num = np.count_nonzero(self._prob == 1.0)
        if confirmed_num > 1: print('ERROR! Cell has more than one value according to its probability array.')
        elif confirmed_num == 1:
            self._prob[(self._prob > 0.0) & (self._prob < 1.0)] = 0.0 # why do i need this when the grids/rows/cols do that for me already?!?!

        # If there are no other possibilities, that means the only number that has a probability is the correct value
        nonzeros = np.count_nonzero(self._prob)
        if nonzeros == 1:
            self._prob[self._prob != 0.0] = 1.0