import kociemba

SOLVED_CUBE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


def solve_cube(cube_string):
    if cube_string == SOLVED_CUBE:
        return "Cube is already solved."

    try:
        solution = kociemba.solve(cube_string)
        return solution

    except Exception as e:
        print("Error solving cube:", e)
        return "No solution found"