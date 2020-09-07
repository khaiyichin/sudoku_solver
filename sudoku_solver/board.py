import numpy as np
import time
from grid import Grid
from cell import Cell
from row import Row
from column import Column

'''
TODO:
- Solution doesn't work for all the 'evil' stage of websudoku, i.e., not robust enough.'
- Grid class is still a bit incomplete. Look at notes on how to implement the next strategy/feature/solver.
- for the DEBUG prints, need to have a try catch maybe? at least a termination and error message
- create a .md to explain the reshape formulas
- documentation and styling
- populate_board is incomplete
'''
DEBUG_MODE = False

class Board(object):
    def __new__(cls, *args, **kwargs):
        '''Override the __new__ method to check for argument validity.
        '''
        if args[0] % np.sqrt(args[0]) != 0.0:
            print('The num argument needs to be a perfect square.')
            raise ValueError
            
        instance = super(Board, cls).__new__(cls)
        return instance

    def __init__(self, num, initial_board = None):
        # Set dimensions
        self._n = int(num)
        self._board_dim = (self._n, self._n)
        self._grid_dim = ( int(np.sqrt(self._n)), int(np.sqrt(self._n)) )
        self._row_dim = (1, self._n)
        self._col_dim = (self._n, 1)
        self._complete_vals = np.full(self._n, False) # array to keep track of whether the board has filled up all instances of a particular value
        self._converged_prob = np.full(self._n, False)

        # Initialize board groups
        self._grids = np.array( [ [ Grid(self._grid_dim[0]) for _ in range(self._grid_dim[0]) ] for _ in range(self._grid_dim[1]) ] )
        self._rows = np.array( [ [ Row(self._row_dim[1]) for _ in range(self._row_dim[0]) ] for _ in range(self._row_dim[1]) ] )
        self._columns = np.array( [ [ Column(self._col_dim[0]) for _ in range(self._col_dim[0]) ] for _ in range(self._col_dim[1]) ] )

        # Populate cells if initial board available
        if initial_board is not None and self.verify_arr_dim(initial_board.shape):
            self._cells = np.array( [ [ Cell(self._n, initial_board[i][j]) for j in range(self._n) ] for i in range(self._n) ] )
        else:
            self._cells = np.array( [ [ Cell(self._n) for _ in range(self._n) ] for _ in range(self._n) ] )

        # Populate the board groups to the cells
        self.populate_grids()
        self.populate_rows()
        self.populate_columns()

        # Create self._n of probability matrices
        self._cached_prob = np.empty((self._n, *self._board_dim))
        for i in range(self._n):
            self._cached_prob[i] = self.get_value_prob(i+1)

        # print('check self grid', self._grids)
        # print('check self row', self._rows)
        # print('check self col', self._columns)

    def split_cells(self, split_into): # complete; perhaps think about adding the explanation below to a .md file
        '''
            This split_cells solution is obtained from 
            https://stackoverflow.com/a/16858283

            Explanation of the code:
            In a pure visual representation (ignoring the [] and | operators), we can describe a 4x4 matrix A:
            [ a b c d ]
            | e f g h |
            | i j k l |
            [ m n o p ]
            
            Moving to code representation, B is represented as a 4 dimension array-of-arrays.
            We define A by: A = np.array([ [a,b,c,d], [e,f,g,h], [i,j,k,l], [m,n,o,p] ])
            We can get the elements by:
            print(A) ==> 
                [[a b c d]
                [e f g h]
                [i j k l]
                [m n o p]]
            print(A[0]) ==> [ a b c d ]

            (Visual rep) A can be grouped into 4 groups of 2x2 grids which we call B:
            [ [ a b ] , [ e f ] ]
            | [ c d ] , [ g h ] |
            | ------- , ------- |
            | [ i j ] , [ m n ] |
            [ [ k l ] , [ o p ] ]

            (Code rep) This is done with the first reshape: it breaks the matrix into grids, which means there are 4 dimensions:
            1. 2 rows of grids
            2. Within each grid row, 2 columns of grids
            3. Within each grid, 2 rows of elements
            4. Within each element row, 2 elements

            We get B by doing: B = np.reshape(A, (2,2,2,2)). Then,
            print(B) ==>
                [[[[a b]
                   [c d]]

                  [[e f]
                   [g h]]]

                 [[[i j]
                   [k l]]

                  [[m n]
                   [o p]]]]
            print(B[0]) ==>
                [[[a b]
                  [c d]]

                 [[e f]
                  [g h]]]
            print(B[0][1]) ==>
                [[e f]
                 [g h]]
            print(B[0][1][0]) ==> [e f]
            print(B[0][1][0][0]) ==> e

            (Visual rep) The swapawes swaps the middle two axes so that the grids are 'untouched' from the matrix A.
            Instead of B, what we want is C:            
            [ [ a b ] , [ c d ] ]
            | [ e f ] , [ g h ] |
            | ------- , ------- |
            | [ i j ] , [ k l ] |
            [ [ m n ] , [ o p ] ]
            Note that this is different from B because the elements' positions in A 'remain'.
            
            (Code rep) With that, we get (compare with B):
            print(C[0]) ==>
                [[[a b]
                  [e f]]

                 [[c d]
                  [g h]]]
            print(B[0][1]) ==>
                [[c d]
                 [g h]]
            
            (Visual rep) The third reshape is to remove the top dimension, so accessing the matrix is slightly easier (one dimension less).
            The new matrix D is then:
            [ [ a b ] , [ c d ] , [ i j ] , [ k l ] ]
            [ [ e f ] , [ g h ] , [ m n ] , [ o p ] ]

            (Code rep) We get D by doing: D = np.reshape(C, (4, 2, 2)).
            print(D) ==>
                [[[a b]
                  [e f]]

                 [[c d]
                  [g h]]

                 [[i j]
                  [m n]]

                 [[k l]
                  [o p]]]
            print(D[0]) ==>
                [[a b]
                 [e f]]
            print(D[0][1]) ==>[e f]            
        '''
        n_out_rows = 0
        n_out_cols = 0
        n_in_rows = 0
        n_in_cols = 0

        # Split the cells into the one of the following forms
        if split_into == 'GRID':
            n_out_rows = self._grid_dim[0]
            n_out_cols = self._grid_dim[1]
            n_in_rows = self._grid_dim[0]
            n_in_cols = self._grid_dim[1]
        elif split_into == 'ROW':
            n_out_rows = self._n
            n_out_cols = 1
            n_in_rows = self._row_dim[0]
            n_in_cols = self._row_dim[1]
        elif split_into == 'COLUMN':
            n_out_rows = 1
            n_out_cols = self._n
            n_in_rows = self._col_dim[0]
            n_in_cols = self._col_dim[1]
        else:
            print('Specify one of the following to split into: GRID, ROW, or COLUMN.')

        return np.reshape(self._cells, (n_out_rows, n_out_cols, n_in_rows, n_in_cols)).swapaxes(1, 2).reshape(n_out_rows * n_out_cols, n_in_rows, n_in_cols)
            
    def populate_board(self, arr): # incomplete
        
        # Check to see if array has correct size
        if not self.verify_arr_dim(arr.shape):
            print('Array does not match board size, cannot populate board.')
            raise ValueError

        # Populate board cell-by-cell
        print('error: to-do')
        return
        for i in range(self._n):
            for j in range(self._n):
                print(self._grids[i][j].cells)

    def populate_grids(self):  # complete
        # Split the cells into (sqrt(self._board_dim[0]) x sqrt(self._board_dim[1]) x self._grid_dim[0] x self._grid_dim[1]) groups (grids)
        split_cells = self.split_cells('GRID')

        # Populate the grids
        for i in range(self._grid_dim[0]):
            for j in range(self._grid_dim[1]):
                self._grids[i][j].populate(split_cells[self._grid_dim[0]*i + j])

    def populate_rows(self): # complete
        # Split the cells into (self._n x self._row_dim[0] x self._row_dim[1]) groups (rows)
        split_cells = self.split_cells('ROW')

        # Populate the rows in the board
        for i in range(self._row_dim[1]):
            self._rows[i][0].populate(split_cells[i])

    def populate_columns(self): # complete
        # Split the cells into (self._n x self._row_dim[0] x self._row_dim[1]) groups (columns)
        split_cells = self.split_cells('COLUMN')

        # Populate the rows in the board
        for i in range(self._col_dim[0]):
            self._columns[0][i].populate(split_cells[i])

    def get_values(self): # complete
        values = np.empty(self._board_dim, int)

        for i in range(self._board_dim[0]):
            for j in range(self._board_dim[1]):
                values[i][j] = self._cells[i][j].get_value()
        
        return values

    def get_values_in_grids(self): # complete
        values = np.empty((*self._grid_dim, *self._grid_dim), int)

        for i in range(self._grid_dim[0]):
            for j in range(self._grid_dim[1]):
                values[i][j] = self._grids[i][j].get_values()

        return values

    def get_values_in_rows(self): # complete
        values = np.empty((self._n, *self._row_dim), int)

        for i in range(self._n):
            values[i] = self._rows[i][0].get_values()
        
        return values

    def get_values_in_columns(self): # complete
        values = np.empty((self._n, *self._col_dim), int)

        for i in range(self._n):
            values[i] = self._columns[0][i].get_values()
        
        return values

    def verify_arr_dim(self, arr_shape): # complete
        return np.all(arr_shape == self.get_board_dim())

    def get_board_dim(self): # complete
        """Get the dimensions of the board.
        """
        return self._board_dim

    def get_board_grids(self): # complete
        """Get the all the grids in the board.
        """
        return self._grids

    def get_value_prob(self, value): # complete
        """Get the probability matrix for the board for a particular value.

        Args:
            value: The value of interest.

        Returns:
            A matrix of probabilities for the value.
        """
        # The index starts from 0
        board_prob = np.empty(self._board_dim)

        # Get the probabilities by horizontal grids
        for i in range(self._board_dim[0]):
            for j in range(self._board_dim[1]):
                board_prob[i][j] = self._cells[i][j].get_value_prob('board' ,value)

        return board_prob

    def evaluate(self): # may be incomplete, since solver is not robust enough

        while not np.all(self._converged_prob):

            # Iterate over all possible values
            for val in range(1, self._n+1):
                
                # If a particular value has been completely filled, move on
                if self._complete_vals[val-1] or np.mean(self._cached_prob[val-1]) == 1.0:
                    self._converged_prob[val-1] = True
                    continue

                # Evaluate the probabilites of a value
                self.evaluate_value_prob(val)

                # Update the board probabilty cache if probabilities not yet converged
                prob_arr = self.get_value_prob(val)

                # Check convergence; the probabilities should match up to the maximum number of occurences of a particular value
                if (prob_arr == self._cached_prob[val-1]).all():
                    self._converged_prob[val-1] = True
                else:
                    self._cached_prob[val-1] = prob_arr

        
        # this is called here to synchronize the cell probabilities
        for cell_row in self._cells:
            for cell in cell_row:
                cell.check_and_reset_probabilities()

        # Strategy one: iterate between each board groups
        # Strategy two: iterate through each board group before moving to next board group.

        # Once converged, strategy two: section probability based elimination
        for val in range(1, self._n+1):
            # first evaluate all grids and store that prob
            # Evaluate the probabilities for a particular value
            for i in range(self._grid_dim[0]):
                for j in range(self._grid_dim[1]):
                    self._grids[i][j].evaluate_value_prob(val)
            
            # then check row probs
            for i in range(self._row_dim[1]):
                for j in range(self._row_dim[0]):
                    self._rows[i][j].evaluate_value_prob(val, True)

            # Then check for grids again            
            for i in range(self._grid_dim[0]):
                for j in range(self._grid_dim[1]):
                    self._grids[i][j].evaluate_value_prob(val)

            # then check col probs
            for i in range(self._col_dim[1]):
                for j in range(self._col_dim[0]):
                    self._columns[i][j].evaluate_value_prob(val, True)

        # Strategy 3: based on the three conditions below, any two or more values that have:
        # 1. the same number of probability occurences
        # 2. the same location for those occurences
        # 3. the same probabilities in each of the locations
        # 4. the sum of each values' probabilities = 1.0
        # 5. Number of occurences must match number of candidates
        # then we can cancel all the other values' probabilities that do not satisfy the conditions above in those locations
        # for i in range(self._grid_dim[0]):
        #     for j in range(self._grid_dim[1]):
        #         if i==2 and j==1: print('DEBUG HERERERERaeearsrsareasraserse')
        #         self._grids[i][j].strategy_3()
        #         if i==2 and j==1: print('DEBUG done')

        # FOR DEBUG PURPOSES
        self._grids[2][1].strategy_3()

        # Perform validity check for each cell
        for cell_row in self._cells:
            for cell in cell_row:
                cell.check_and_reset_probabilities()

        

    def evaluate_value_prob(self, value): # incomplete; run the grid evaluation twice with row once and col once respective after each grid evaluation
        
        # Evaluate the probabilities for a particular value
        for i in range(self._grid_dim[0]):
            for j in range(self._grid_dim[1]):
                self._grids[i][j].evaluate_value_prob(value)
                # if i==2 and j==1:print('intermediate', i, j, value, self.get_value_prob(value))
                self._rows[self._grid_dim[0]*i + j][0].evaluate_value_prob(value)
                # print('intermediate', i, j, value, self.get_value_prob(value))
                self._columns[0][self._grid_dim[0]*i + j].evaluate_value_prob(value)
                # print('intermediate', i, j, value, self.get_value_prob(value))

    def update(self): # may be incomplete since solver is not robust enough
        
        # Track any updates
        updated = False

        # Go through all the cells
        for i in range(self._board_dim[0]):
            for j in range(self._board_dim[0]):
                # Only assign if the value is unfilled and there's a confirmed value in the cell
                if (self._cells[i][j].get_value() == 0):
                    prob_array = self._cells[i][j].get_prob_array('board')
                    
                    # Fill in the value if there's a 100% probability
                    if 1 in prob_array:
                        self._cells[i][j].set_value(np.nonzero(prob_array == 1)[0][0] + 1)
                        
                        # If there's at least on number updated, then there's change to the board
                        if not updated: updated = True

        # Reset self._converged_prob after updating if there are still unfilled values        
        for ind in range(self._n):
            if np.count_nonzero(self.get_values() == ind+1) < self._n:
                self._converged_prob[ind] = False
            else: # declare the search for that value complete
                self._complete_vals[ind] = True

        return updated

    def solve_board(self): # should be complete
        
        start_time = time.perf_counter()
        counter = 0
        while not np.all(self._complete_vals):
            
            # Evaluate probabilities
            self.evaluate()

            # Update board
            if not self.update():

                # Try strategy one where you evaluate all grid probabilities and then check row and column by sections.
                end_time = time.perf_counter()
                print('DEBUG Cannot solve board in ' + str(end_time - start_time) + 's and ' + str(counter) + ' step(s).')
                return

            counter += 1

            if DEBUG_MODE:
                board = self.get_values()
                print('DEBUG MODE: Board after step ' + str(counter) + '.')
                print(board)
                print('DEBUG MODE: Filled values = ' + str(np.count_nonzero(board)))

        end_time = time.perf_counter()
        print('Board solved in ' + str(end_time - start_time) + 's and ' + str(counter) + ' step(s)!')
        return