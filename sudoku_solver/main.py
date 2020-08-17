from board import Board
from grid import Grid
import numpy as np

test = Grid(2)
test2 = Board(2)
test3 = np.array([[1,2,3,4], [2,3,4,1], [3,4,1,2], [4,1,2,3]])

# print(test.get_value_prob(3))
# print(test2.populate_board(test3))