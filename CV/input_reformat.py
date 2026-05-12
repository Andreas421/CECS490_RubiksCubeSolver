from cube_config import COLOR_MAP, COLOR_TO_FACE, FACE_TO_COLOR, FACE_ORDER


# Temporary one-face test function
def reformat_face_state(face_matrix):
    face_string = ""

    for row in face_matrix:
        for color in row:
            if color not in COLOR_MAP:
                raise ValueError(f"Unknown color '{color}'.")
            face_string += COLOR_MAP[color]

    return face_string


def reformat_cube_state(captured_faces): #converts captured faces into 54-char string for solver
    if len(captured_faces) != 6:
        raise ValueError("Exactly 6 captured faces are required.")

    cube_string = ""

    for face_label in FACE_ORDER:
        face_color = FACE_TO_COLOR[face_label]

        if face_color not in captured_faces:
            raise ValueError(f"Missing {face_color} face for {face_label} side.")

        face_matrix = captured_faces[face_color]

        for row in face_matrix:
            for color in row:
                if color not in COLOR_TO_FACE:
                    raise ValueError(f"Invalid color '{color}' found in cube.")

                cube_string += COLOR_TO_FACE[color]

    return cube_string