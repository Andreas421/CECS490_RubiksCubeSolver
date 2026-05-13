from cube_config import COLOR_MAP


class CubeValidation:
    def __init__(self):
        self.valid_colors = set(COLOR_MAP.keys())

    def get_center_color(self, face_matrix):   #return center color
        return face_matrix[1][1]

    def has_valid_colors(self, face_matrix):  #makes sure all detected colors are in color map       
        for row in face_matrix:
            for color in row:
                if color not in self.valid_colors:
                    print("Invalid face: contains a color not found in COLOR_MAP.")
                    return False

        return True
    
    def validate_face_for_capture(self, face_matrix):
        # Check that all detected colors exist in COLOR_MAP
        if not self.has_valid_colors(face_matrix):
            print("Face not saved: invalid color detected.")
            return False

        # Check that the center color is usable
        center_color = self.get_center_color(face_matrix)
        if center_color == "unknown":
            print("Face not saved: center color is unknown.")
            return False

        return True

    def validate_complete_cube(self, captured_faces): #Validate full cube after all faces captured
        if len(captured_faces) != 6:
            print("Invalid cube: exactly 6 faces are required.")
            return False

        for center_color, face_matrix in captured_faces.items():
            if center_color not in self.valid_colors:
                print(f"Invalid cube: '{center_color}' is not a valid center color.")
                return False

            if not self.has_valid_colors(face_matrix):
                print(f"Invalid cube: issue found in {center_color} face.")
                return False

            actual_center = self.get_center_color(face_matrix)
            if actual_center != center_color:
                print(f"Invalid cube: stored key '{center_color}' does not match center '{actual_center}'.")
                return False

        if not self.verify_color_counts(captured_faces):
            print("Invalid cube: each color must appear exactly 9 times.")
            return False

        return True

    def get_color_counts(self, captured_faces): #how many times each color appears in all captured faces
        color_counts = {}

        for color in self.valid_colors:
            if color != "unknown":
                color_counts[color] = 0

        for face_matrix in captured_faces.values():
            for row in face_matrix:
                for color in row:
                    if color != "unknown":
                        color_counts[color] += 1

        return color_counts

    def verify_color_counts(self, captured_faces): #checks each color appears 9 times
        color_counts = self.get_color_counts(captured_faces)

        for color, count in color_counts.items():
            if count != 9:
                print(f"{color}: {count}/9")
                return False

        return True

    def print_color_counts(self, captured_faces):
        color_counts = self.get_color_counts(captured_faces)

        print("Color counts:")
        for color, count in color_counts.items():
            print(f"- {color}: {count}/9")