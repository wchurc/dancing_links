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

        if matrix is not None:
            self.build_partial_solution(matrix)

        def search():
            # Check if finished
            if self.right == self:
                # Found a solution. Construct the solution matrix and print it
                solution_matrix = [[0] * len(matrix[0]) for _ in range(len(matrix))]

                for cell in solution_set:
                    row, col, num = [int(x) for x in cell.name.split(':')]
                    solution_matrix[row][col] = num

                pprint(solution_matrix)
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

            # Cover the chosen column
            self.cover(smallest_col)

            # Walk down the column and try choosing every row
            row_cell = smallest_col.down
            while row_cell != smallest_col:

                # Add the chosen row to the solution set
                solution_set.append(row_cell)

                # Cover every column satisfied by the chosen row
                col_cell = row_cell.right
                while col_cell != row_cell:
                    self.cover(col_cell.column)
                    col_cell = col_cell.right

                # Continue the search recursively
                search()

                # Undo the previous operation
                row_cell = solution_set.pop()

                col_cell = row_cell.left
                while col_cell != row_cell:
                    self.uncover(col_cell.column)
                    col_cell = col_cell.left

                row_cell = row_cell.down

            self.uncover(smallest_col)

        search()

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
    @property
    def height(self):
        return 2

    @property
    def width(self):
        return 2

    def build_constraints(self):
        name_fmt = "{0}:{1}:{2}"

        # First construct the headers
        # Constraint 1: Some number from {1,2} must appear in every space
        for row in range(self.height):
            for col in range(self.width):
                new_header = Header(name=name_fmt.format(row, col, 'n'))
                self.add_header(new_header)

        # Constraint 2: Each number from {1,2} must appear in every row in any column
        for num in [1, 2]:
            for row in range(self.height):
                new_header = Header(name=name_fmt.format(row, 'c', num))
                self.add_header(new_header)

        # Constraint 3: Each number from {1,2} must appear in every column in any row
        for num in [1, 2]:
            for col in range(self.width):
                new_header = Header(name=name_fmt.format('r', col, num))
                self.add_header(new_header)

        # Next populate the columns
        for row in range(self.height):
            for col in range(self.width):
                for num in [1, 2]:
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


if __name__ == '__main__':

    ll = LatinSquareDLX()
    ll.build_constraints()
    ll.print()
    print("Covering first column")
    first_col = ll.right
    ll.cover(first_col)
    ll.print()
    print("Uncovering first column")
    ll.uncover(first_col)
    ll.print()
    print('iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')

    latin_square = [[0, 0],
                    [0, 0]]
    ll.solve(latin_square)


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

    sudoku_solution = [[3, 4, 6, 1, 2, 7, 9, 5, 8],
                       [7, 8, 5, 6, 9, 4, 1, 3, 2],
                       [2, 1, 9, 3, 8, 5, 4, 6, 7],
                       [4, 6, 2, 5, 3, 1, 8, 7, 9],
                       [9, 3, 1, 2, 7, 8, 6, 4, 5],
                       [8, 5, 7, 9, 4, 6, 2, 1, 3],
                       [5, 9, 8, 4, 1, 3, 7, 2, 6],
                       [6, 2, 4, 7, 5, 9, 3, 8, 1],
                       [1, 7, 3, 8, 6, 2, 5, 9, 4]]
