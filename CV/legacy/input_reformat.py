from cube_config import COLOR_MAP, COLOR_TO_FACE, FACE_TO_COLOR, FACE_ORDER, FACE_ROTATIONS


# Temporary one-face test function
def reformat_face_state(face_matrix):
    face_string = ""

    for row in face_matrix:
        for color in row:
            if color not in COLOR_MAP:
                raise ValueError(f"Unknown color '{color}'.")
            face_string += COLOR_MAP[color]

    return face_string


def rotate_face(face_matrix, degrees):
    """
    Rotates a 3x3 face matrix clockwise.
    """

    if degrees == 0:
        return [row[:] for row in face_matrix]

    elif degrees == 90:
        return [
            [face_matrix[2][0], face_matrix[1][0], face_matrix[0][0]],
            [face_matrix[2][1], face_matrix[1][1], face_matrix[0][1]],
            [face_matrix[2][2], face_matrix[1][2], face_matrix[0][2]]
        ]

    elif degrees == 180:
        return [
            [face_matrix[2][2], face_matrix[2][1], face_matrix[2][0]],
            [face_matrix[1][2], face_matrix[1][1], face_matrix[1][0]],
            [face_matrix[0][2], face_matrix[0][1], face_matrix[0][0]]
        ]

    elif degrees == 270:
        return [
            [face_matrix[0][2], face_matrix[1][2], face_matrix[2][2]],
            [face_matrix[0][1], face_matrix[1][1], face_matrix[2][1]],
            [face_matrix[0][0], face_matrix[1][0], face_matrix[2][0]]
        ]

    else:
        raise ValueError("Rotation must be 0, 90, 180, or 270 degrees.")


def reformat_cube_state(captured_faces):
    """
    Converts captured faces into a 54-character solver string.
    """

    if len(captured_faces) != 6:
        raise ValueError("Exactly 6 captured faces are required.")

    cube_string = ""

    for face_label in FACE_ORDER:
        face_color = FACE_TO_COLOR[face_label]

        if face_color not in captured_faces:
            raise ValueError(f"Missing {face_color} face for {face_label} side.")

        face_matrix = captured_faces[face_color]

        rotation_degrees = FACE_ROTATIONS[face_label]
        rotated_face = rotate_face(face_matrix, rotation_degrees)

        for row in rotated_face:
            for color in row:
                if color not in COLOR_TO_FACE:
                    raise ValueError(f"Invalid color '{color}' found in cube.")

                cube_string += COLOR_TO_FACE[color]

    return cube_string