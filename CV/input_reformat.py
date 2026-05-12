from cube_config import COLOR_TO_FACE, FACE_ORDER, FACE_ROTATIONS, FACE_TO_COLOR


def rotate_face(face_matrix, degrees):
    """Return a rotated copy of a 3x3 face matrix."""
    if degrees == 0:
        return [row[:] for row in face_matrix]

    if degrees == 90:
        return [list(row) for row in zip(*face_matrix[::-1])]

    if degrees == 180:
        return [row[::-1] for row in face_matrix[::-1]]

    if degrees == 270:
        return [list(row) for row in zip(*face_matrix)][::-1]

    raise ValueError("Rotation must be 0, 90, 180, or 270 degrees.")


def reformat_cube_state(captured_faces):
    """Convert captured color faces into a 54-character Kociemba cube string."""
    if len(captured_faces) != 6:
        raise ValueError("Exactly 6 captured faces are required.")

    cube_string = ""

    for face_label in FACE_ORDER:
        face_color = FACE_TO_COLOR[face_label]

        if face_color not in captured_faces:
            raise ValueError(f"Missing {face_color} face for {face_label} side.")

        rotated_face = rotate_face(captured_faces[face_color], FACE_ROTATIONS[face_label])

        for row in rotated_face:
            for color in row:
                if color not in COLOR_TO_FACE:
                    raise ValueError(f"Invalid color '{color}' found in cube.")

                cube_string += COLOR_TO_FACE[color]

    return cube_string
