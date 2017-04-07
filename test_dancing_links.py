import pytest
from dancing_links import SudokuDLX, LatinSquareDLX


def test_easy_latin_square():
    problem = [[1, 0],
               [0, 0]]

    solution = [[1, 2],
                [2, 1]]

    ls = LatinSquareDLX()
    answer = ls.solve(problem)

    assert answer == solution, "Must be able to solve easy latin square."



def test_hard_latin_square():
    problem = [[3,0,5,0,7,0,1,0],
               [7,0,0,6,0,1,0,3],
               [0,1,0,7,0,0,3,0],
               [8,0,6,0,0,0,0,2],
               [0,0,0,0,0,8,4,0],
               [0,3,0,0,6,0,0,4],
               [1,0,8,0,0,4,0,0],
               [0,8,0,0,1,0,5,6]]

    solution = []

    ls = LatinSquareDLX()
    answer = ls.solve(problem)

    assert answer == solution, "Must be able to solve large latin square."


def test_easy_sudoku():
    problem = [[0, 0, 6, 1, 0, 0, 0, 0, 8],
               [0, 8, 0, 0, 9, 0, 0, 3, 0],
               [2, 0, 0, 0, 0, 5, 4, 0, 0],
               [4, 0, 0, 0, 0, 1, 8, 0, 0],
               [0, 3, 0, 0, 7, 0, 0, 4, 0],
               [0, 0, 7, 9, 0, 0, 0, 0, 3],
               [0, 0, 8, 4, 0, 0, 0, 0, 6],
               [0, 2, 0, 0, 5, 0, 0, 8, 0],
               [1, 0, 0, 0, 0, 2, 5, 0, 0]]

    solution = [[3, 4, 6, 1, 2, 7, 9, 5, 8],
                [7, 8, 5, 6, 9, 4, 1, 3, 2],
                [2, 1, 9, 3, 8, 5, 4, 6, 7],
                [4, 6, 2, 5, 3, 1, 8, 7, 9],
                [9, 3, 1, 2, 7, 8, 6, 4, 5],
                [8, 5, 7, 9, 4, 6, 2, 1, 3],
                [5, 9, 8, 4, 1, 3, 7, 2, 6],
                [6, 2, 4, 7, 5, 9, 3, 8, 1],
                [1, 7, 3, 8, 6, 2, 5, 9, 4]]

    s = SudokuDLX()
    answer = s.solve(problem)

    assert answer == solution, "Must be able to solve easy sudoku."


def test_hard_sudoku():
    problem = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 3, 6, 0, 0, 0, 0, 0],
               [0, 7, 0, 0, 9, 0, 2, 0, 0],
               [0, 5, 0, 0, 0, 7, 0, 0, 0],
               [0, 0, 0, 0, 4, 5, 7, 0, 0],
               [0, 0, 0, 1, 0, 0, 0, 3, 0],
               [0, 0, 1, 0, 0, 0, 0, 6, 8],
               [0, 0, 8, 5, 0, 0, 0, 1, 0],
               [0, 9, 0, 0, 0, 0, 4, 0, 0]]

    solution = [[8, 1, 2, 7, 5, 3, 6, 4, 9],
                [9, 4, 3, 6, 8, 2, 1, 7, 5],
                [6, 7, 5, 4, 9, 1, 2, 8, 3],
                [1, 5, 4, 2, 3, 7, 8, 9, 6],
                [3, 6, 9, 8, 4, 5, 7, 2, 1],
                [2, 8, 7, 1, 6, 9, 5, 3, 4],
                [5, 2, 1, 9, 7, 4, 3, 6, 8],
                [4, 3, 8, 5, 2, 6, 9, 1, 7],
                [7, 9, 6, 3, 1, 8, 4, 5, 2]]


    s = SudokuDLX()
    answer = s.solve(problem)

    assert answer == solution, "Must be able to solve hard sudoku."

def test_can_solve_multiple():
    assert False, "Write the test"


def test_can_generate_correct_latin_square():
    assert False, "Write the test"


def test_can_generate_correct_sudoku():
    assert False, "Write the test"
