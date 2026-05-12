from cube_config import CUBE_COLORS


class CubeValidation:
    def get_center_color(self, face_matrix):
        return face_matrix[1][1]

    def has_valid_shape(self, face_matrix):
        if len(face_matrix) != 3:
            print("Invalid face: face must have exactly 3 rows.")
            return False

        for row in face_matrix:
            if len(row) != 3:
                print("Invalid face: each row must have exactly 3 colors.")
                return False

        return True

    def has_known_colors(self, face_matrix):
        for row in face_matrix:
            for color in row:
                if color not in CUBE_COLORS:
                    print(f"Invalid face: unknown color '{color}'.")
                    return False

        return True

    def validate_face_for_capture(self, face_matrix):
        if not self.has_valid_shape(face_matrix):
            return False

        if not self.has_known_colors(face_matrix):
            print("Face not saved: scan contains an unknown color.")
            return False

        return True

    def validate_complete_cube(self, captured_faces):
        if len(captured_faces) != 6:
            print("Invalid cube: exactly 6 faces are required.")
            return False

        if set(captured_faces.keys()) != CUBE_COLORS:
            missing = CUBE_COLORS - set(captured_faces.keys())
            extra = set(captured_faces.keys()) - CUBE_COLORS
            if missing:
                print("Missing face centers:", ", ".join(sorted(missing)))
            if extra:
                print("Invalid face centers:", ", ".join(sorted(extra)))
            return False

        for center_color, face_matrix in captured_faces.items():
            if not self.has_valid_shape(face_matrix):
                print(f"Invalid cube: bad shape in {center_color} face.")
                return False

            if not self.has_known_colors(face_matrix):
                print(f"Invalid cube: bad color in {center_color} face.")
                return False

            actual_center = self.get_center_color(face_matrix)
            if actual_center != center_color:
                print(
                    f"Invalid cube: stored key '{center_color}' does not match "
                    f"center '{actual_center}'."
                )
                return False

        if not self.verify_color_counts(captured_faces):
            print("Invalid cube: each color must appear exactly 9 times.")
            return False

        return True

    def get_color_counts(self, captured_faces):
        color_counts = {color: 0 for color in CUBE_COLORS}

        for face_matrix in captured_faces.values():
            for row in face_matrix:
                for color in row:
                    if color in color_counts:
                        color_counts[color] += 1

        return color_counts

    def verify_color_counts(self, captured_faces):
        color_counts = self.get_color_counts(captured_faces)
        is_valid = True

        for color, count in sorted(color_counts.items()):
            if count != 9:
                print(f"{color}: {count}/9")
                is_valid = False

        return is_valid

    def print_color_counts(self, captured_faces):
        print("Color counts:")
        for color, count in sorted(self.get_color_counts(captured_faces).items()):
            print(f"- {color}: {count}/9")
