from cube_validation import CubeValidation


class CubeCapture:
    def __init__(self):
        # Stores scanned faces using center color as the key
        self.faces = {}
        self.validator = CubeValidation()

    def get_center_color(self, face_matrix):
        return face_matrix[1][1]

    def add_face(self, face_matrix):
        # Validate face before saving it
        if not self.validator.validate_face_for_capture(face_matrix):
            return False

        center_color = self.get_center_color(face_matrix)

        already_captured = center_color in self.faces

        # Store or replace a copy of the face matrix
        self.faces[center_color] = [row[:] for row in face_matrix]

        if already_captured:
            print(f"Updated {center_color} face.")
        else:
            print(f"Saved {center_color} face.")

        print(f"Captured {self.face_count()}/6 faces.")

        return True

    def face_count(self):
        return len(self.faces)

    def is_complete(self):
        return self.face_count() == 6

    def get_faces(self):
        return self.faces

    def print_captured_faces(self):
        if not self.faces:
            print("No faces captured yet.")
            return

        print("Captured faces:")
        for color in self.faces:
            print(f"- {color}")

    def validate_cube(self):
        return self.validator.validate_complete_cube(self.faces)

    def print_color_counts(self):
        self.validator.print_color_counts(self.faces)