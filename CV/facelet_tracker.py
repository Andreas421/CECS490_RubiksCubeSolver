from cube_config import FACE_ORDER


class FaceletTracker:
    def __init__(self):
        #Tracks which original sticker is in each cube position
        self.positions = {}

        #Initialize all 54 sticker identities
        for face in FACE_ORDER:
            for index in range(9):
                facelet = f"{face}{index}"
                self.positions[facelet] = facelet # which square is taking up the detected square
                                                  # example: self.positions["U6"] = "F2" (sticker originally at F2 is now in U6 position)

    def get_visible_top(self):
        #Return the 9 stickers currently visible to the camera
        top_face = []

        for row in range(3):
            row_facelets = []

            for col in range(3):
                position = f"U{row * 3 + col}"
                row_facelets.append(self.positions[position])

            top_face.append(row_facelets)

        return top_face


    # Simulate a 90-degree clockwise F rotation
    def rotate_front_clockwise(self):
        # Save positions before rotating
        old = self.positions.copy()

        # Rotate the 9 front facelets clockwise
        for row in range(3):
            for col in range(3):
                new_index = row * 3 + col
                old_index = (2 - col) * 3 + row

                self.positions[f"F{new_index}"] = old[f"F{old_index}"]

        # Rotate the adjacent stickers on U, R, D, L
        for i in range(3):
            self.positions[f"R{3 * i}"] = old[f"U{6 + i}"]
            self.positions[f"D{i}"] = old[f"R{6 - 3 * i}"]
            self.positions[f"L{2 + 3 * i}"] = old[f"D{i}"]
            self.positions[f"U{6 + i}"] = old[f"L{8 - 3 * i}"]

    #Simulate a 90-degree clockwise R rotation
    def rotate_right_clockwise(self):
        # Save positions before rotating
        old = self.positions.copy()

        # Rotate the 9 right facelets clockwise
        for row in range(3):
            for col in range(3):
                new_index = row * 3 + col
                old_index = (2 - col) * 3 + row

                self.positions[f"R{new_index}"] = old[f"R{old_index}"]

        # Rotate the adjacent stickers on U, B, D, F
        for i in range(3):
            self.positions[f"U{2 + 3 * i}"] = old[f"F{2 + 3 * i}"]
            self.positions[f"B{6 - 3 * i}"] = old[f"U{2 + 3 * i}"]
            self.positions[f"D{2 + 3 * i}"] = old[f"B{6 - 3 * i}"]
            self.positions[f"F{2 + 3 * i}"] = old[f"D{2 + 3 * i}"]


    #Simulate a 90-degree clockwise B rotation
    def rotate_back_clockwise(self):
        old = self.positions.copy()

        # Rotate the 9 back facelets clockwise
        for row in range(3):
            for col in range(3):
                new_index = row * 3 + col
                old_index = (2 - col) * 3 + row

                self.positions[f"B{new_index}"] = old[f"B{old_index}"]

        # Rotate the adjacent stickers on U, L, D, R
        for i in range(3):
            self.positions[f"L{6 - 3 * i}"] = old[f"U{i}"]
            self.positions[f"D{6 + i}"] = old[f"L{3 * i}"]
            self.positions[f"R{8 - 3 * i}"] = old[f"D{6 + i}"]
            self.positions[f"U{i}"] = old[f"R{2 + 3 * i}"]


    #Simulate a 90-degree clockwise L rotation
    def rotate_left_clockwise(self):
        old = self.positions.copy()

        # Rotate the 9 left facelets clockwise
        for row in range(3):
            for col in range(3):
                new_index = row * 3 + col
                old_index = (2 - col) * 3 + row

                self.positions[f"L{new_index}"] = old[f"L{old_index}"]

        # Rotate the adjacent stickers on U, F, D, B
        for i in range(3):
            self.positions[f"F{3 * i}"] = old[f"U{3 * i}"]
            self.positions[f"D{3 * i}"] = old[f"F{3 * i}"]
            self.positions[f"B{8 - 3 * i}"] = old[f"D{3 * i}"]
            self.positions[f"U{3 * i}"] = old[f"B{8 - 3 * i}"]


    #Universal rotation function using standard cube notation
    def rotate(self, command):

        # Match face letters to our existing rotation functions
        rotations = {
            "F": self.rotate_front_clockwise,
            "R": self.rotate_right_clockwise,
            "B": self.rotate_back_clockwise,
            "L": self.rotate_left_clockwise
        }

        #Split simultaneous move commands (ex: "F+B")
        moves = command.replace(" ", "").split("+")

        #Validate commands before rotating
        if len(moves) > 2:
            raise ValueError(f"Invalid rotation: {command}")

        for move in moves:
            face = move[0] if move else ""
            modifier = move[1:]

            if face not in rotations or modifier not in ("", "'", "2"):
                raise ValueError(f"Invalid rotation: {move}")

        #Only allow opposite faces in paired commands
        if len(moves) == 2:
            faces = {move[0] for move in moves}

            if faces not in ({"F", "B"}, {"R", "L"}):
                raise ValueError("Paired rotations must use opposite faces.")

        #Execute each requested rotation
        for move in moves:
            face = move[0]
            modifier = move[1:]

            if modifier == "'":
                turns = 3   # 3 clockwise turns = 1 counterclockwise
            elif modifier == "2":
                turns = 2   # 180-degree rotation
            else:
                turns = 1   # Standard clockwise rotation

            for i in range(turns):
                rotations[face]()



#Test universal rotation function 
if __name__ == "__main__":

    tracker = FaceletTracker()
    original = tracker.positions.copy()

    # TEST 1 - Clockwise followed by counterclockwise
    tracker.rotate("F")
    tracker.rotate("F'")

    assert tracker.positions == original
    print("Test 1 - F then F': PASSED")

    # TEST 2 - 180-degree rotation twice
    tracker.rotate("R2")
    tracker.rotate("R2")

    assert tracker.positions == original
    print("Test 2 - R2 twice: PASSED")

    # TEST 3 - Paired opposite-face rotations
    tracker.rotate("F+B")

    comparison = FaceletTracker()
    comparison.rotate("F")
    comparison.rotate("B")

    assert tracker.positions == comparison.positions
    print("Test 3 - F+B: PASSED")

    # TEST 4 - Mixed clockwise/counterclockwise
    tracker = FaceletTracker()
    tracker.rotate("R+L'")

    comparison = FaceletTracker()
    comparison.rotate("R")
    comparison.rotate("L'")

    assert tracker.positions == comparison.positions
    print("Test 4 - R+L': PASSED")

    # TEST 5 - Ensure all 54 sticker identities remain unique
    assert len(set(tracker.positions.values())) == 54
    print("Test 5 - All 54 stickers accounted for: PASSED")
