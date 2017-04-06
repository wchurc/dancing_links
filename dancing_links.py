#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
import math
from pprint import pprint


class Cell(object):
    def __init__(self, name=None, column=None, left=None, right=None, up=None, down=None):
        # The name of a cell is a string in the format of
        # "row:column:number" where matrix[row, column] = number
        self.name = name

        self.column = column or self
        self.left = left or self
        self.right = right or self
        self.up = up or self
        self.down = down or self

    def remove_horizontal(self):
        self.right.left = self.left
        self.left.right = self.right


    def restore_horizontal(self):
        self.right.left = self
        self.left.right = self


    def remove_vertical(self):
        self.up.down = self.down
        self.down.up = self.up


    def restore_vertical(self):
        self.up.down = self
        self.down.up = self


class Header(Cell):
    def __init__(self, *args, **kwargs):
        super(Header, self).__init__(*args, **kwargs)
        self.size = 0

    def add_cell(self, cell):
        cell.down = self
        cell.up = self.up
        self.up.down = cell
        self.up = cell

        cell.column = self
        self.size += 1


class DancingLinks(Cell, metaclass=ABCMeta):

    @property
    @abstractmethod
    def height(self):
        pass

    @property
    @abstractmethod
    def width(self):
        pass

    @abstractmethod
    def build_constraints(self):
        pass

    @abstractmethod
    def build_partial_solution(self, matrix):
        pass

    def cover(self, column):
        # Unlink the column header
        column.remove_horizontal()

        # Walk down the column
        col_cell = column.down
        while col_cell != column:

            # Walk right across the row
            row_cell = col_cell.right
            while row_cell != col_cell:

                # Remove each cell in the row from its column
                # and decrement its column's size
                row_cell.remove_vertical()
                row_cell.column.size -= 1

                row_cell = row_cell.right

            col_cell = col_cell.down

    def uncover(self, column):
        # Walk up the column
        col_cell = column.up
        while col_cell != column:

            # Walk left across the row
            row_cell = col_cell.left
            while row_cell != col_cell:

                # Restore each cell in the row and increment its column's size
                row_cell.restore_vertical()
                row_cell.column.size += 1

                row_cell = row_cell.left

            col_cell = col_cell.up

        # Restore the column header
        column.restore_horizontal()

    def solve(self, matrix=None):

        solution_set = []

        self.clear_links()
        self.build_constraints()

        if matrix is not None:
            solution_set = self.build_partial_solution(matrix)

        self.max_depth = 0

        def search(depth):
            self.max_depth = depth if depth > self.max_depth else self.max_depth

            # Check if finished
            if self.right == self:
                # Found a solution. Construct the solution matrix and print it
                solution_matrix = [[0] * self.width for _ in range(self.height)]

                for cell in solution_set:
                    if len(cell.name.split(':')) != 3:
                        import pdb; pdb.set_trace()
                    row, col, num = map(int, cell.name.split(':'))
                    solution_matrix[row][col] = num

                #pprint(solution_matrix)
                for row in solution_matrix:
                    pprint(row)
                print("\nMax depth: {}\n".format(self.max_depth))
                return

            # Find the column with the smallest number of cells
            min_size = math.inf
            smallest_col = None
            column = self.right
            while column != self:
                if column.size < min_size:
                    min_size = column.size
                    smallest_col = column
                column = column.right

            # Check if out of options
            if smallest_col.size < 1:
                return

            # Cover the chosen column
            self.cover(smallest_col)

            # Walk down the column and try choosing every row
            row_cell = smallest_col.down
            while row_cell != smallest_col:

                # Add the chosen row to the solution set
                if isinstance(row_cell, Header):
                    pdb.set_trace()
                solution_set.append(row_cell)

                # Cover every column satisfied by the chosen row
                col_cell = row_cell.right
                while col_cell != row_cell:
                    self.cover(col_cell.column)
                    col_cell = col_cell.right

                # Continue the search recursively
                search(depth + 1)

                # Undo the previous operation
                row_cell = solution_set.pop()

                col_cell = row_cell.left
                while col_cell != row_cell:
                    self.uncover(col_cell.column)
                    col_cell = col_cell.left

                row_cell = row_cell.down

            self.uncover(smallest_col)

        search(0)
        print("Max depth: {}".format(self.max_depth))

    def add_header(self, column):
        column.left = self.left
        column.right = self
        self.left.right = column
        self.left = column

    def clear_links(self):
        self.left = self
        self.right = self
        self.up = self
        self.down = self

    def print(self):

        column = self.right
        while column != self:
            print("COLUMN: {}".format(column.name))

            cell = column.down
            while cell != column:
                print(cell.name)
                cell = cell.down

            column = column.right

    def build_constraints_from_template(self, template):
        pass


class LatinSquareDLX(DancingLinks):
    def __init__(self, size=2, *args, **kwargs):
        self.size = size
        super(LatinSquareDLX, self).__init__(*args, **kwargs)

    @property
    def height(self):
        return self.size

    @property
    def width(self):
        return self.size

    @property
    def num_range(self):
        return range(self.size)

    def build_constraints(self):
        name_fmt = "{0}:{1}:{2}"

        # First construct the headers
        # Constraint 1: Some number must appear in every space
        for row in range(self.height):
            for col in range(self.width):
                new_header = Header(name=name_fmt.format(row, col, 'n'))
                self.add_header(new_header)

        # Constraint 2: Each number from self.num_range
        # must appear in every row in any column
        for num in self.num_range:
            for row in range(self.height):
                new_header = Header(name=name_fmt.format(row, 'c', num))
                self.add_header(new_header)

        # Constraint 3: Each number from self.num_range
        # must appear in every column in any row
        for num in self.num_range:
            for col in range(self.width):
                new_header = Header(name=name_fmt.format('r', col, num))
                self.add_header(new_header)

        # Next populate the columns
        for row in range(self.height):
            for col in range(self.width):
                for num in self.num_range:
                    prev = None
                    name = name_fmt.format(row, col, num)
                    column = self.right
                    while column != self:
                        col_row, col_col, col_num = column.name.split(':')
                        if (col_row == str(row) or col_row == 'r') and \
                           (col_col == str(col) or col_col == 'c') and \
                           (col_num == str(num) or col_num == 'n'):
                            cell = Cell(name=name)
                            column.add_cell(cell)
                            if prev is not None:
                                cell.right = prev.right
                                cell.left = prev
                                prev.right.left = cell
                                prev.right = cell
                            prev = cell

                        column = column.right


    def build_partial_solution(self, matrix):
        pass


class SudokuDLX(DancingLinks):

    @property
    def height(self):
        return 9

    @property
    def width(self):
        return 9

    @property
    def num_range(self):
        return range(1, 10)

    def build_constraints(self):
        def get_zone(row, col):
            """Helper function to identify the zone a cell belongs to"""
            lookup = [[0, 1, 2],
                      [3, 4, 5],
                      [6, 7, 8]]
            return str(lookup[row // 3][col // 3])

        rcn_fmt = "{0}:{1}:{2}"

        # First construct the headers
        # Constraint 1: Some number must appear in every space
        for row in range(self.height):
            for col in range(self.width):
                new_header = Header(name=rcn_fmt.format(row, col, 'n'))
                self.add_header(new_header)

        # Constraint 2: Each number from num_range
        # must appear in every row in any column
        for num in self.num_range:
            for row in range(self.height):
                new_header = Header(name=rcn_fmt.format(row, 'c', num))
                self.add_header(new_header)

        # Constraint 3: Each number from self.num_range
        # must appear in every column in any row
        for num in self.num_range:
            for col in range(self.width):
                new_header = Header(name=rcn_fmt.format('r', col, num))
                self.add_header(new_header)

        # Constraint 4: Each number from self.num_range
        # must appear in every zone
        zn_format = "{0}:{1}"
        for zone in range(9):
            for num in self.num_range:
                new_header = Header(name=zn_format.format(zone, num))
                self.add_header(new_header)

        # Next populate the columns
        for row in range(self.height):
            for col in range(self.width):
                for num in self.num_range:
                    prev = None
                    name = rcn_fmt.format(row, col, num)
                    column = self.right
                    while column != self:
                        column_name_items = column.name.split(':')
                        if len(column_name_items) == 3:
                            # "r:c:n" has 3 items
                            col_row, col_col, col_num = column_name_items
                            if (col_row == str(row) or col_row == 'r') and \
                               (col_col == str(col) or col_col == 'c') and \
                               (col_num == str(num) or col_num == 'n'):
                                cell = Cell(name=name)
                                column.add_cell(cell)
                                if prev is not None:
                                    cell.right = prev.right
                                    cell.left = prev
                                    prev.right.left = cell
                                    prev.right = cell
                                prev = cell
                        else:
                            # "z:n" has 2 items
                            col_zone, col_num = column_name_items
                            if get_zone(row, col) == col_zone and str(num) == col_num:
                                cell = Cell(name=name)
                                column.add_cell(cell)
                                if prev is not None:
                                    cell.right = prev.right
                                    cell.left = prev
                                    prev.right.left = cell
                                    prev.right = cell
                                prev = cell

                        column = column.right


    def build_partial_solution(self, matrix):
        assert len(matrix[0]) == self.width
        assert len(matrix) == self.height

        solution_set = []
        for row_index, row in enumerate(matrix):
            for col_index, num in enumerate(row):
                if num != 0:
                    # Find a cell that matches row_index col_index, num
                    # Dumb Search: This could probably be sped up by looking at the column names
                    name = "{0}:{1}:{2}".format(row_index, col_index, num)
                    cell = None
                    column = self.right
                    while column != self:
                        row_cell = column.down
                        while row_cell != column:
                            if row_cell.name == name:
                                cell = row_cell
                                break
                            row_cell = row_cell.down
                        if cell is not None:
                            break
                        column = column.right

                    # Add the cell to the solution set
                    assert cell is not None
                    solution_set.append(cell)

                    # Cover all satisfied columns
                    self.cover(cell.column)
                    row_cell = cell.right
                    while row_cell != cell:
                        self.cover(row_cell.column)
                        row_cell = row_cell.right

        return solution_set

if __name__ == '__main__':


    latin_square = [[0, 0],
                    [0, 0]]

    #ll = LatinSquareDLX(size=10)
    #ll.build_constraints()
    #ll.solve()


    latin_square_solution_1 = [[1, 2],
                               [2, 1]]

    latin_square_solution_1 = [[2, 1],
                               [1, 2]]

    exact_cover = [[0, 0, 1, 0, 1, 1, 0],
                   [1, 0, 0, 1, 0, 0, 1],
                   [0, 1, 1, 0, 0, 1, 0],
                   [1, 0, 0, 1, 0, 0, 0],
                   [0, 1, 0, 0, 0, 0, 1],
                   [0, 0, 0, 1, 1, 0, 1]]

    sudoku = [[0, 0, 6, 1, 0, 0, 0, 0, 8],
              [0, 8, 0, 0, 9, 0, 0, 3, 0],
              [2, 0, 0, 0, 0, 5, 4, 0, 0],
              [4, 0, 0, 0, 0, 1, 8, 0, 0],
              [0, 3, 0, 0, 7, 0, 0, 4, 0],
              [0, 0, 7, 9, 0, 0, 0, 0, 3],
              [0, 0, 8, 4, 0, 0, 0, 0, 6],
              [0, 2, 0, 0, 5, 0, 0, 8, 0],
              [1, 0, 0, 0, 0, 2, 5, 0, 0]]

    print("Solving easy sudoku")
    s = SudokuDLX()
    s.solve(sudoku)

    hard_sudoku = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 3, 6, 0, 0, 0, 0, 0],
                   [0, 7, 0, 0, 9, 0, 2, 0, 0],
                   [0, 5, 0, 0, 0, 7, 0, 0, 0],
                   [0, 0, 0, 0, 4, 5, 7, 0, 0],
                   [0, 0, 0, 1, 0, 0, 0, 3, 0],
                   [0, 0, 1, 0, 0, 0, 0, 6, 8],
                   [0, 0, 8, 5, 0, 0, 0, 1, 0],
                   [0, 9, 0, 0, 0, 0, 4, 0, 0]]

    print("Solving hard sudoku")
    s.solve(hard_sudoku)

    sudoku_solution = [[3, 4, 6, 1, 2, 7, 9, 5, 8],
                       [7, 8, 5, 6, 9, 4, 1, 3, 2],
                       [2, 1, 9, 3, 8, 5, 4, 6, 7],
                       [4, 6, 2, 5, 3, 1, 8, 7, 9],
                       [9, 3, 1, 2, 7, 8, 6, 4, 5],
                       [8, 5, 7, 9, 4, 6, 2, 1, 3],
                       [5, 9, 8, 4, 1, 3, 7, 2, 6],
                       [6, 2, 4, 7, 5, 9, 3, 8, 1],
                       [1, 7, 3, 8, 6, 2, 5, 9, 4]]
