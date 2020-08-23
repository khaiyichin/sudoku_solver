from board import Board
from grid import Grid
import numpy as np


test = Board(4, np.array([[1,0,0,0], [0,0,0,2], [0,0,0,0], [0,0,0,4]]))
# test = Board(4, np.array([[1,2,3,4], [2,3,4,1], [3,4,1,2], [4,1,2,3]]))
# test = Board(4, np.array([[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,16]]))
# test = Board(9, np.arange(81).reshape(9,9))

print('initial_board',test.get_values())
# print('grid', test.get_values_in_grids())
# print('row',test.get_values_in_rows())
# print('column',test.get_values_in_columns())
print('prob',test.get_value_prob(1))
# print(test2.populate_board(test3))