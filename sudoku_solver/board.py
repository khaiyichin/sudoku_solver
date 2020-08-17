import numpy as np
from grid import Grid
from cell import Cell

'''
TODO:
1. Add method to split cells into columns and rows
2. Complete Column and Row classes.
3. Understand what the heck is going on with the reshape function.
'''

class Board:
    def __init__(self, num, initial_board = None):
        self._n = num
        self._cells = np.array( [ [ Cell(num) for _ in range(self._n * self._n) ] for _ in range(self._n * self._n) ] )
        
        # Create n x n grids in the board
        if not initial_board or not self.verify_arr_dim(initial_board.shape):
            # self.columns = np.array( [ [ Column(num) for _ in range(num) ] for _ in range(num) ] )
            # self.rows = np.array( [ [ Row(num) for _ in range(num) ] for _ in range(num) ] )
            self._grids = np.array( [ [ Grid(num) for _ in range(num) ] for _ in range(num) ] )

        else:
            for i in self._n:
                for j in self._n:
                    self._cells[i][j].set_value(initial_board[i][j])

        # Populate the grids
        print(self._cells)
        self.populate_grids()

        # Populate the rows
        # self.populate_rows()

        # Populate the columns
        # self.populate_columns()

        # Compute the board dimensions
        self.board_dim = np.multiply(self._grids.shape, self._n)

    def split_cells(self, split_into):
        # Split the cells into the one of the following forms
        if split_into == 'GRID':
            return np.reshape(self._cells, (self._n, self._n, -1, self._n)).swapaxes(1, 2).reshape(-1, self._n, self._n)
        elif split_into == 'ROW':
            return None # for now
        elif split_into == 'COLUMN':
            return None # for now
        else:
            print('Specify one of the following to split into: GRID, ROW, or COLUMN.')
            
    def populate_board(self, arr):
        
        # Check to see if array has correct size
        if not self.verify_arr_dim(arr.shape):
            print('Array does not match board size, cannot populate board.')
            return

        # Populate board cell-by-cell
        for i in range(self._n):
            for j in range(self._n):
                print(self._grids[i][j].cells)

    def populate_grids(self):
        # Split the cells in to n x n groups of grids
        # Call split_cell(SPLIT_FORM) here
        print(self.split_cells('GRID'))

        # Populate the grids
        for i in range(self._n):
            for j in range(self._n):
                self._grids[i][j].populate_grid() # INCOMPLETE!

    def verify_arr_dim(self, arr_shape):
        return np.all(arr_shape[0] == self.get_board_dim()[0]) and np.all(arr_shape[1] == self.get_board_dim()[1])

    def get_board_dim(self):
        """Get the dimensions of the board.
        """
        return self.board_dim

    def get_board_grids(self):
        """Get the all the grids in the board.
        """
        return self._grids

    def get_value_prob(self, value):
        """Get the probability matrix for the board for a particular value.

        Args:
            value: The value of interest.

        Returns:
            A matrix of probabilities for the value.
        """

        # The index starts from 0
        board_prob = np.array([])
        board_row_prob = np.array([])

        # Get the probabilities by horizontal grids
        for i in range(self._n):
            for j in range(self._n):

                if (j == 0):
                    board_row_prob = self._grids[i][j].get_value_prob(value)
                else:
                    board_row_prob = np.hstack( (board_row_prob, self._grids[i][j].get_value_prob(value)) )
            
            if (i == 0):
                board_prob = board_row_prob
            else:
                board_prob = np.vstack( (board_prob, board_row_prob) )

        return board_prob