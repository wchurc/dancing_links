from collections import defaultdict
import pytest
from dancing_links import SudokuDLX, LatinSquareDLX

easy_ls = [[1, 0],
           [0, 0]]

easy_ls_solution = [[1, 2],
                    [2, 1]]

hard_ls = [[3, 0, 5, 0, 7, 0, 1, 0],
           [7, 0, 0, 6, 0, 1, 0, 3],
           [0, 1, 0, 7, 0, 0, 3, 0],
           [8, 0, 6, 0, 0, 0, 0, 2],
           [0, 0, 0, 0, 0, 8, 4, 0],
           [0, 3, 0, 0, 6, 0, 0, 4],
           [1, 0, 8, 0, 0, 4, 0, 0],
           [0, 8, 0, 0, 1, 0, 5, 6]]

hard_ls_solution = [[3, 6, 5, 4, 7, 2, 1, 8],
                    [7, 5, 2, 6, 4, 1, 8, 3],
                    [2, 1, 4, 7, 8, 6, 3, 5],
                    [8, 4, 6, 1, 3, 5, 7, 2],
                    [6, 7, 3, 5, 2, 8, 4, 1],
                    [5, 3, 1, 8, 6, 7, 2, 4],
                    [1, 2, 8, 3, 5, 4, 6, 7],
                    [4, 8, 7, 2, 1, 3, 5, 6]]

easy_sudoku = [[0, 0, 6, 1, 0, 0, 0, 0, 8],
               [0, 8, 0, 0, 9, 0, 0, 3, 0],
               [2, 0, 0, 0, 0, 5, 4, 0, 0],
               [4, 0, 0, 0, 0, 1, 8, 0, 0],
               [0, 3, 0, 0, 7, 0, 0, 4, 0],
               [0, 0, 7, 9, 0, 0, 0, 0, 3],
               [0, 0, 8, 4, 0, 0, 0, 0, 6],
               [0, 2, 0, 0, 5, 0, 0, 8, 0],
               [1, 0, 0, 0, 0, 2, 5, 0, 0]]

easy_sudoku_solution = [[3, 4, 6, 1, 2, 7, 9, 5, 8],
                        [7, 8, 5, 6, 9, 4, 1, 3, 2],
                        [2, 1, 9, 3, 8, 5, 4, 6, 7],
                        [4, 6, 2, 5, 3, 1, 8, 7, 9],
                        [9, 3, 1, 2, 7, 8, 6, 4, 5],
                        [8, 5, 7, 9, 4, 6, 2, 1, 3],
                        [5, 9, 8, 4, 1, 3, 7, 2, 6],
                        [6, 2, 4, 7, 5, 9, 3, 8, 1],
                        [1, 7, 3, 8, 6, 2, 5, 9, 4]]

hard_sudoku = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 3, 6, 0, 0, 0, 0, 0],
               [0, 7, 0, 0, 9, 0, 2, 0, 0],
               [0, 5, 0, 0, 0, 7, 0, 0, 0],
               [0, 0, 0, 0, 4, 5, 7, 0, 0],
               [0, 0, 0, 1, 0, 0, 0, 3, 0],
               [0, 0, 1, 0, 0, 0, 0, 6, 8],
               [0, 0, 8, 5, 0, 0, 0, 1, 0],
               [0, 9, 0, 0, 0, 0, 4, 0, 0]]

hard_sudoku_solution = [[8, 1, 2, 7, 5, 3, 6, 4, 9],
                        [9, 4, 3, 6, 8, 2, 1, 7, 5],
                        [6, 7, 5, 4, 9, 1, 2, 8, 3],
                        [1, 5, 4, 2, 3, 7, 8, 9, 6],
                        [3, 6, 9, 8, 4, 5, 7, 2, 1],
                        [2, 8, 7, 1, 6, 9, 5, 3, 4],
                        [5, 2, 1, 9, 7, 4, 3, 6, 8],
                        [4, 3, 8, 5, 2, 6, 9, 1, 7],
                        [7, 9, 6, 3, 1, 8, 4, 5, 2]]


def verify_ls(solution):
    assert len(solution) == len(solution[0]), "Latin square width must equal height"

    size = len(solution)
    numbers = set(range(1, size + 1))

    for row in solution:
        assert numbers == set(row), "Latin square row is invalid"

    for i in range(size):
        column = [row[i] for row in solution]
        assert numbers == set(column), "Latin square column is invalid"


def verify_sudoku(solution):
    assert len(solution) == len(solution[0]), "Sudoku width must equal height"

    size = len(solution)
    numbers = set(range(1, size + 1))

    for row in solution:
        assert numbers == set(row), "Sudoku row is invalid"

    for i in range(size):
        column = [row[i] for row in solution]
        assert numbers == set(column), "Sudoku column is invalid"

    def get_zone(row, col):
        """Helper function to identify the zone a cell belongs to"""
        lookup = [[0, 1, 2],
                  [3, 4, 5],
                  [6, 7, 8]]
        return str(lookup[row // 3][col // 3])

    zones = defaultdict(int)
    for row, col in [(row, col) for row in range(size) for col in range(size)]:
        zones[get_zone(row, col)] += 1

    assert all(map(lambda x: x == size, zones.values())), "Sudoku zones are invalid"


def test_easy_latin_square():

    ls = LatinSquareDLX()
    answer = ls.solve(easy_ls)

    assert answer == easy_ls_solution, "Must be able to solve easy latin square."


def test_hard_latin_square():

    ls = LatinSquareDLX()
    answer = ls.solve(hard_ls)

    assert answer == hard_ls_solution, "Must be able to solve large latin square."


def test_easy_sudoku():

    s = SudokuDLX()
    answer = s.solve(easy_sudoku)

    assert answer == easy_sudoku_solution, "Must be able to solve easy sudoku."


def test_hard_sudoku():

    s = SudokuDLX()
    answer = s.solve(hard_sudoku)

    assert answer == hard_sudoku_solution, "Must be able to solve hard sudoku."


def test_can_solve_multiple():

    s = SudokuDLX()
    for i in range(2):
        problems = [easy_sudoku, hard_sudoku]
        solutions = [easy_sudoku_solution, hard_sudoku_solution]
        answer = s.solve(problems[i])

        assert answer == solutions[i], "Must be able to solve sudoku repeatedly."

    l = LatinSquareDLX()
    for i in range(2):
        problems = [easy_ls, hard_ls]
        solutions = [easy_ls_solution, hard_ls_solution]
        answer = l.solve(problems[i])

        assert answer == solutions[i], "Must be able to solve latin squares repeatedly."


def test_can_generate_correct_latin_square():

    l = LatinSquareDLX()
    g = l.generate(size=4)

    # Verify correctness of solutions
    for _, solution in zip(range(10), g):
        verify_ls(solution)

    # Skip ahead
    for _ in range(100):
        next(g)

    # Verify some more solutions
    for _, solution in zip(range(10), g):
        verify_ls(solution)


def test_can_generate_correct_sudoku():

    s = SudokuDLX()
    g = s.generate()

    # Verify correctness of solutions
    for _, solution in zip(range(10), g):
        verify_sudoku(solution)

    # Skip ahead
    for _ in range(100):
        next(g)

    # Verify some more solutions
    for _, solution in zip(range(10), g):
        verify_sudoku(solution)
