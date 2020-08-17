import numpy as np
import copy as cp

class Cell:
    def __init__(self, num, value = 0):
        self._n = num
        self._val = value
        total_possibilities = num * num
        self._prob = np.full(total_possibilities, 0)

    def get_value(self):
        return self._val

    def set_value(self, value):
        self._val = value

    def get_prob_array(self):
        return self._prob