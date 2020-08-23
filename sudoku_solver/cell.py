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

    def get_prob_array(self):
        return self._prob