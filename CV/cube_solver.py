import kociemba

SOLVED_CUBE = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


def solve_cube(cube_string):
    if len(cube_string) != 54:
        return f"No solution found: cube string must be 54 characters, got {len(cube_string)}."

    if cube_string == SOLVED_CUBE:
        return "Cube is already solved."

    try:
        return kociemba.solve(cube_string)
    except Exception as error:
        print("Error solving cube:", error)
        return "No solution found."
