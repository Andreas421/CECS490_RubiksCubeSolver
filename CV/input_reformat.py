from cube_config import COLOR_MAP


#temporary 1 face test function
def reformat_face_state(face_matrix):

    if len(face_matrix) != 3 or any(len(row) != 3 for row in face_matrix):
        raise ValueError("Face must be a 3x3 matrix.")

    face_string = ""

    for row in face_matrix:
        for color in row:
            if color not in COLOR_MAP:
                raise ValueError(f"Unknown color '{color}'.")
            face_string += COLOR_MAP[color]

    return face_string