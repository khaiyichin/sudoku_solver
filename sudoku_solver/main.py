from board import Board
from grid import Grid
import numpy as np

# test = Board(4, np.array([[1,0,0,0], [0,0,0,2], [0,3,0,0], [0,0,0,4]]))
board = [
    [0, 0, 0, 8, 0, 0, 4, 0, 9],
    [9, 0, 0, 0, 0, 3, 0, 7, 6],
    [5, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 4, 0, 6, 0, 0, 0, 0],
    [0, 7, 0, 0, 5, 0, 0, 4, 0],
    [0, 0, 0, 0, 7, 0, 2, 0, 0],
    [0, 0, 2, 0, 0, 0, 0, 0, 4],
    [4, 6, 0, 9, 0, 0, 0, 0, 2],
    [1, 0, 5, 0, 0, 6, 0, 0, 0],
]
test = Board(9, np.array(board))
# test = Board(4, np.array([[1,2,3,4], [2,3,4,1], [3,4,1,2], [4,1,2,3]]))
# test = Board(4, np.array([[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,16]]))
# test = Board(9, np.arange(81).reshape(9,9))

# print('initial_board',test.get_values())
# print('grid', test.get_values_in_grids())
# print('row',test.get_values_in_rows())
# print('column',test.get_values_in_columns())
# print('prob',test.get_value_prob(2))
test.solve_board()

print('board', test.get_values())
print('filled', np.count_nonzero(test.get_values()))

# for i in range(9):
#     print('prob =',i+1,test.get_value_prob(i+1))