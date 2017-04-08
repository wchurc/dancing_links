#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod


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
        self.right.left, self.left.right = self.left, self.right

    def restore_horizontal(self):
        self.right.left, self.left.right = self, self

    def remove_vertical(self):
        self.up.down, self.down.up = self.down, self.up

    def restore_vertical(self):
        self.up.down, self.down.up = self, self

    def walk(self, direction="right", inc=False):
        """Iterate through all links in the direction specified by direction.
        Valid directions are "left, "right", "up", and "down".
        Set inc to True to include the object you are calling walk on.
        """
        if inc:
            yield self
        cell = getattr(self, direction)
        while cell != self:
            yield cell
            cell = getattr(cell, direction)


class Header(Cell):

    def __init__(self, *args, **kwargs):
        super(Header, self).__init__(*args, **kwargs)
        self.size = 0

    def add_cell(self, cell):
        cell.down, cell.up = self, self.up
        self.up.down, self.up = cell, cell

        cell.column = self
        self.size += 1


class DancingLinks(Cell, metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        self._size = 9
        super(DancingLinks, self).__init__(*args, **kwargs)

    @property
    def height(self):
        return self._size

    @property
    def width(self):
        return self._size

    @property
    def num_range(self):
        return range(1, self._size + 1)

    def cover(self, column):
        # Unlink the column header
        column.remove_horizontal()

        for col_cell in column.walk('down'):
            for row_cell in col_cell.walk('right'):
                # Remove each cell in the row from its column
                # and decrement its column's size
                row_cell.remove_vertical()
                row_cell.column.size -= 1

    def uncover(self, column):

        for col_cell in column.walk('up'):
            for row_cell in col_cell.walk('left'):

                # Restore each cell in the row and increment its column's size
                row_cell.restore_vertical()
                row_cell.column.size += 1

        # Restore the column header
        column.restore_horizontal()

    def solve(self, matrix):

        self.clear_links()

        self._size = len(matrix)
        self.build_constraints()

        try:
            answer = next(self._solve(matrix))
        except StopIteration:
            return None
        return answer

    def generate(self, size=9, matrix=None):
        self.clear_links()

        self._size = size
        self.build_constraints()

        return self._solve(matrix)

    def _solve(self, matrix=None):

        solution_set = [] if matrix is None else self.build_partial_solution(matrix)

        def search():

            # Check if finished
            if self.right == self:
                # Found a solution. Construct the solution matrix and print it
                solution_matrix = [[0] * self.width for _ in range(self.height)]

                for cell in solution_set:
                    row, col, num = map(int, cell.name.split(':'))
                    solution_matrix[row][col] = num

                yield solution_matrix

            if self.right == self:
                return

            # Find the column with the smallest number of cells
            smallest_col = min(self.walk(), key=lambda x: x.size)

            # Check if out of options
            if smallest_col.size < 1:
                return

            # Cover the chosen column
            self.cover(smallest_col)

            # Walk down the column and try choosing every row
            for row_cell in smallest_col.walk('down'):

                # Add the chosen row to the solution set
                solution_set.append(row_cell)

                # Cover every column satisfied by the chosen row
                for col_cell in row_cell.walk('right'):
                    self.cover(col_cell.column)

                # Continue the search recursively
                yield from search()

                # Undo the previous operation
                row_cell = solution_set.pop()

                for col_cell in row_cell.walk('left'):
                    self.uncover(col_cell.column)

            self.uncover(smallest_col)

        yield from search()

    def build_partial_solution(self, matrix):
        assert len(matrix[0]) == self.width
        assert len(matrix) == self.height

        solution_set = []
        for row_index, row, col_index, num in ((ri, r, ci, n) for ri, r in enumerate(matrix)
                                                              for ci, n in enumerate(r)):
            if num != 0:
                # Find a cell that matches row_index col_index, num
                # Dumb Search: This could probably be sped up by looking at the column names
                name = "{0}:{1}:{2}".format(row_index, col_index, num)
                cell = None
                for column, row_cell in ((c, r) for c in self.walk()
                                                for r in c.walk('down')):
                    if row_cell.name == name:
                        cell = row_cell
                        break

                # Add the cell to the solution set
                assert cell is not None
                solution_set.append(cell)

                # Cover all satisfied columns
                for row_cell in cell.walk('right', inc=True):
                    self.cover(row_cell.column)

        return solution_set

    def add_header(self, column):
        column.left, column.right = self.left, self
        self.left.right, self.left = column, column

    def clear_links(self):
        self.left, self.right, self.up, self.down = self, self, self, self

    def print(self):

        for column in self.walk():
            print("COLUMN: {}".format(column.name))

            for cell in column.walk('down'):
                print(cell.name)


class LatinSquareDLX(DancingLinks):

    def build_constraints(self):
        name_fmt = "{0}:{1}:{2}"

        # First construct the headers
        # Constraint 1: Some number must appear in every space
        for row, col in ((row, col) for row in range(self.height) for col in range(self.width)):
            new_header = Header(name=name_fmt.format(row, col, 'n'))
            self.add_header(new_header)

        # Constraint 2: Each number from self.num_range must appear in every row in any column
        for num, row in ((num, row) for num in self.num_range for row in range(self.height)):
            new_header = Header(name=name_fmt.format(row, 'c', num))
            self.add_header(new_header)

        # Constraint 3: Each number from self.num_range must appear in every column in any row
        for num, col in ((num, col) for num in self.num_range for col in range(self.width)):
            new_header = Header(name=name_fmt.format('r', col, num))
            self.add_header(new_header)

        # Next populate the columns
        for row, col, num in ((row, col, num) for row in range(self.height)
                                              for col in range(self.width)
                                              for num in self.num_range):
            prev = None
            name = name_fmt.format(row, col, num)

            for column in self.walk():
                col_row, col_col, col_num = column.name.split(':')

                if (col_row == str(row) or col_row == 'r') and \
                   (col_col == str(col) or col_col == 'c') and \
                   (col_num == str(num) or col_num == 'n'):

                    cell = Cell(name=name)
                    column.add_cell(cell)

                    if prev is not None:
                        # Add new cell to its row
                        cell.right, cell.left = prev.right, prev
                        prev.right.left, prev.right = cell, cell
                    prev = cell


class SudokuDLX(DancingLinks):

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
        for row, col in ((row, col) for row in range(self.height) for col in range(self.width)):
            new_header = Header(name=rcn_fmt.format(row, col, 'n'))
            self.add_header(new_header)

        # Constraint 2: Each number from num_range must appear in every row in any column
        for num, row in ((num, row) for num in self.num_range for row in range(self.height)):
            new_header = Header(name=rcn_fmt.format(row, 'c', num))
            self.add_header(new_header)

        # Constraint 3: Each number from self.num_range must appear in every column in any row
        for num, col in ((num, col) for num in self.num_range for col in range(self.width)):
            new_header = Header(name=rcn_fmt.format('r', col, num))
            self.add_header(new_header)

        # Constraint 4: Each number from self.num_range must appear in every zone
        zn_format = "{0}:{1}"
        for zone, num in ((zone, num) for zone in range(9) for num in self.num_range):
            new_header = Header(name=zn_format.format(zone, num))
            self.add_header(new_header)

        # Next populate the columns
        for row, col, num in ((row, col, num) for row in range(self.height)
                                              for col in range(self.width)
                                              for num in self.num_range):
            prev = None
            name = rcn_fmt.format(row, col, num)

            for column in self.walk('right'):

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
                            # Connect the new cell to its row
                            cell.right, cell.left = prev.right, prev
                            prev.right.left, prev.right = cell, cell

                        prev = cell
                else:
                    # "z:n" has 2 items
                    col_zone, col_num = column_name_items
                    if get_zone(row, col) == col_zone and str(num) == col_num:

                        cell = Cell(name=name)
                        column.add_cell(cell)

                        if prev is not None:
                            # Connect the new cell to its row
                            cell.right, cell.left = prev.right, prev
                            prev.right.left, prev.right = cell, cell
                        prev = cell
