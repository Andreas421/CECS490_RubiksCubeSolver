
from facelet_tracker import FaceletTracker
from motor_controller import SimulatedMotorController
from cube_config import FACE_ORDER, FACE_TO_COLOR, COLOR_TO_FACE


#Scanning movement sequences
PHASE_1 = [
    (None, True),
    ("F+B", True),
    ("F+B", True),
    ("F+B", True),
    ("F+B", False),
    ("R+L", True),
    ("R+L", True),
    ("R+L", True),
    ("R+L", False)
]

PHASE_2 = [
    ("L'", False),
    ("F", True),
    ("R+L'", True),
    ("B+F'", True),
    ("R'+L", True),
    ("B'", True)
]

#Optional restoration movements
RESTORE_SEQUENCE = [
    "B",
    "R+L'",
    "B'+F",
    "R'+L",
    "F'",
    "L"
]


#Simulate camera color detection using a scrambled cube
class SimulatedCamera:
    
    def __init__(self, scramble_moves=None):  # CHANGED
        scrambled_cube = FaceletTracker()

        # NEW - Allow different scrambles for testing
        if scramble_moves is None:
            scramble_moves = ["F", "R", "B'", "L", "F2", "R'"]

        # CHANGED - Use the provided scramble
        for move in scramble_moves:
            scrambled_cube.rotate(move)

        # UNCHANGED - Assign colors to original sticker positions
        self.starting_colors = {}

        for position, sticker in scrambled_cube.positions.items():
            self.starting_colors[position] = FACE_TO_COLOR[sticker[0]]


    # NEW - Return a 3x3 matrix of simulated detected colors
    def capture(self, visible_facelets):
        grid_colors = []

        for row in visible_facelets:
            row_colors = []

            for sticker in row:
                row_colors.append(self.starting_colors[sticker])

            grid_colors.append(row_colors)

        return grid_colors



#Coordinates the automated scanning process
class ScanEngine:
    def __init__(self, motor, camera, restore_original_state=True):  
        self.motor = motor
        self.camera = camera  
        self.tracker = FaceletTracker()
        self.restore_original_state = restore_original_state

        self.observed = set()
        self.observed_colors = {}  
        self.photo_count = 0
        self.motor_stages = 0
        self.face_turns = 0


    #Execute a motor movement and update tracker
    def execute_move(self, command):
        movement_complete = self.motor.move(command)

        if not movement_complete:
            raise RuntimeError(f"Motor movement failed: {command}")

        # Only update tracker after movement completes
        self.tracker.rotate(command)

        self.motor_stages += 1
        self.face_turns += len(command.split("+"))

    #Capture and store visible sticker colors

    #Validate entire capture before saving anything
    def capture_top(self, check_initial_center=False):  
        visible = self.tracker.get_visible_top()
        grid_colors = self.camera.capture(visible)

        #Reject missing or incorrectly sized camera data
        if (not isinstance(grid_colors, (list, tuple))
                or len(grid_colors) != 3
                or any(not isinstance(row, (list, tuple)) or len(row) != 3
                    for row in grid_colors)):
            raise ValueError("Camera must return a 3x3 color grid.")
        
        #Verify initial cube orientation before scanning
        if check_initial_center:
            center_color = grid_colors[1][1]
            expected_color = FACE_TO_COLOR["U"]

            if center_color != expected_color:
                raise ValueError(
                    f"Incorrect cube orientation: "
                    f"expected {expected_color} on top, "
                    f"detected {center_color}."
                )

        #Temporarily store colors until validation finishes
        pending_colors = {}

        for row in range(3):
            for col in range(3):
                sticker = visible[row][col]
                detected_color = grid_colors[row][col]

                # Skip center stickers
                if sticker[1:] == "4":
                    continue

                # Reject invalid colors
                if detected_color not in FACE_TO_COLOR.values():
                    raise ValueError(f"Invalid color detected: {detected_color}")

                # Reject conflicting observations
                if sticker in self.observed_colors:
                    if self.observed_colors[sticker] != detected_color:
                        raise ValueError(
                            f"Conflicting color for {sticker}: "
                            f"stored={self.observed_colors[sticker]}, "
                            f"new={detected_color}"
                        )

                # NEW - Stage color without saving it yet
                pending_colors[sticker] = detected_color

        # NEW - Only save after ALL stickers pass validation
        self.observed_colors.update(pending_colors)
        self.observed.update(pending_colors.keys())
        self.photo_count += 1

        return grid_colors

    
    # NEW - Retry failed camera captures without moving motors
    def capture_with_retry(self, check_initial_center=False):
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                return self.capture_top(
                    check_initial_center=check_initial_center
                )

            except (ValueError, RuntimeError) as error:
                print(f"[CAMERA] Attempt {attempt + 1} failed: {error}")

                # NEW - Stop after the final unsuccessful attempt
                if attempt == max_attempts - 1:
                    raise

                print("[CAMERA] Retrying capture...")


    #Reconstruct the cube's current physical state
    def reconstruct_cube(self):

        #Verify every non-center sticker has a recorded color
        required = {
            f"{face}{index}"
            for face in FACE_ORDER
            for index in range(9)
            if index != 4
        }

        if set(self.observed_colors) != required:
            raise ValueError("Cannot reconstruct: missing sticker colors.")

        #Reconstruct colors using the final sticker positions
        reconstructed_colors = {}

        for face in FACE_ORDER:
            for index in range(9):
                position = f"{face}{index}"
                sticker = self.tracker.positions[position]

                if index == 4:
                    # Centers have known colors
                    reconstructed_colors[position] = FACE_TO_COLOR[face]
                else:
                    # Retrieve the recorded color of this sticker
                    reconstructed_colors[position] = self.observed_colors[sticker]

        #Convert the reconstructed colors to Kociemba notation
        cube_string = ""

        for face in FACE_ORDER:
            for index in range(9):
                position = f"{face}{index}"
                color = reconstructed_colors[position]
                cube_string += COLOR_TO_FACE[color]

        #Verify cube string length and color counts
        if len(cube_string) != 54:
            raise ValueError("Invalid cube string length.")

        for face in FACE_ORDER:
            if cube_string.count(face) != 9:
                raise ValueError(f"Invalid sticker count for {face}.")

        return cube_string

    #Run the complete scanning sequence
    def run_scan(self):

        for phase_name, phase_steps in [
            ("Phase 1", PHASE_1),
            ("Phase 2", PHASE_2)
        ]:
            for command, take_photo in phase_steps:

                if command is not None:
                    self.execute_move(command)
                
                if take_photo:
                    #Retry failed captures automatically
                    self.capture_with_retry(
                        check_initial_center=(self.photo_count == 0)
                    )


            print(f"{phase_name}: {len(self.observed)}/48 stickers observed")

        #Restore original scramble if enabled
        if self.restore_original_state:
            print("\nRestoring original scramble...")

            for command in RESTORE_SEQUENCE:
                self.execute_move(command)

            restored = all(
                position == sticker
                for position, sticker in self.tracker.positions.items()
            )

            if not restored:
                raise RuntimeError("Cube restoration failed.")

            print("Original scramble restored: PASSED")

        #Verify all non-center stickers were observed
        required = {
            f"{face}{index}"
            for face in FACE_ORDER
            for index in range(9)
            if index != 4
        }

        if self.observed != required:
            raise RuntimeError("Scanning incomplete: missing stickers.")

        print("\n--- Scan Results ---")
        print("Motor stages:", self.motor_stages)
        print("Face turns:", self.face_turns)
        print("Photos:", self.photo_count)
        print("Stickers observed:", len(self.observed))

        # NEW - Reconstruct and return the final cube state
        cube_string = self.reconstruct_cube()

        print("\nReconstructed cube string:")
        print(cube_string)

        return cube_string




# CHANGED - Test reconstruction and Kociemba integration
if __name__ == "__main__":

    from cube_solver import solve_cube  # NEW

    motor = SimulatedMotorController()
    camera = SimulatedCamera()

    # Change True/False to test both scanning modes
    engine = ScanEngine(
        motor,
        camera,
        restore_original_state=False
    )

    # CHANGED - Scan now returns the reconstructed cube string
    cube_string = engine.run_scan()

    # NEW - Verify against simulated ground truth
    expected_string = ""

    for face in FACE_ORDER:
        for index in range(9):
            position = f"{face}{index}"
            sticker = engine.tracker.positions[position]
            color = camera.starting_colors[sticker]
            expected_string += COLOR_TO_FACE[color]

    assert cube_string == expected_string
    print("\nCube reconstruction verification: PASSED")

    # NEW - Send reconstructed cube to existing solver
    solution = solve_cube(cube_string)

    print("\n--- Kociemba Solution ---")
    print(solution)

    assert solution != "No solution found"
    print("\nScan engine reconstruction test PASSED!")
