from facelet_tracker import FaceletTracker
from cube_config import FACE_ORDER, FACE_TO_COLOR, COLOR_TO_FACE  
import kociemba 
from motor_controller import SimulatedMotorController  

#Choose whether scanning restores the original scramble
RESTORE_ORIGINAL_STATE = True


# Scanning sequence
# Each entry contains (motor command, capture photo?)

PHASE_1 = [
    (None, True),       # Initial photo
    ("F+B", True),
    ("F+B", True),
    ("F+B", True),
    ("F+B", False),     # Return F and B to starting positions
    ("R+L", True),
    ("R+L", True),
    ("R+L", True),
    ("R+L", False)      # Return R and L to starting positions
]

PHASE_2 = [
    ("L'", False),
    ("F", True),
    ("R+L'", True),
    ("B+F'", True),
    ("R'+L", True),
    ("B'", True)
]

#Initialize tracker, scanning and motor counters
tracker = FaceletTracker()
observed = set()
motor = SimulatedMotorController() 


#Generate a legal scrambled cube for testing
scrambled_cube = FaceletTracker()

for move in ["F", "R", "B'", "L", "F2", "R'"]:
    scrambled_cube.rotate(move)

#Assign an actual color to every original sticker identity
starting_colors = {}

for position, sticker in scrambled_cube.positions.items():
    starting_colors[position] = FACE_TO_COLOR[sticker[0]]

#Store colors as they are discovered during scanning
observed_colors = {}


photo_count = 0
motor_stages = 0
face_turns = 0

#All 48 non-center sticker identities
required = {
    f"{face}{index}"
    for face in FACE_ORDER
    for index in range(9)
    if index != 4
}

#Execute both scanning phases
for phase_name, phase_steps in [
    ("Phase 1", PHASE_1),
    ("Phase 2", PHASE_2)
]:
    for command, take_photo in phase_steps:

        if command is not None:
            #Send command to simulated motor controller
            movement_complete = motor.move(command)

            #Stop if motor reports failure
            if not movement_complete:
                raise RuntimeError(f"Motor movement failed: {command}")

            #Only update tracker AFTER movement completes
            tracker.rotate(command)

            motor_stages += 1
            face_turns += len(command.split("+"))


        if take_photo:
            # Simulate observing the top face
            visible = tracker.get_visible_top()

            for row in visible:
                for sticker in row:
                    if sticker[1:] != "4":
                        observed.add(sticker)

                        #Simulate the camera detecting this sticker's color
                        detected_color = starting_colors[sticker]

                        #Verify repeated observations agree
                        if sticker in observed_colors:
                            assert observed_colors[sticker] == detected_color

                        #Store the color under the original sticker identity
                        observed_colors[sticker] = detected_color


            photo_count += 1

    print(f"\n{phase_name}: {len(observed)}/48 stickers observed")

    if phase_name == "Phase 1":
        print("Missing:", sorted(required - observed))


# NEW - Undo Phase 2 movements if restoration is enabled
RESTORE_SEQUENCE = [
    "B",
    "R+L'",
    "B'+F",
    "R'+L",
    "F'",
    "L"
]

if RESTORE_ORIGINAL_STATE:
    print("\n--- Restoring Original Scramble ---")

    for command in RESTORE_SEQUENCE:
        #Execute restoration through motor controller
        movement_complete = motor.move(command)

        #Stop if movement fails
        if not movement_complete:
            raise RuntimeError(f"Motor restoration failed: {command}")

        #Update tracker after motor completion
        tracker.rotate(command)

        motor_stages += 1
        face_turns += len(command.split("+"))

    #Verify all stickers returned to original positions
    restored = all(
        position == sticker
        for position, sticker in tracker.positions.items()
    )

    assert restored
    print("Original scramble restored: PASSED")



# NEW - Check final results
print("\n--- Final Results ---")
print("Motor stages:", motor_stages)
print("Face turns:", face_turns)
print("Photos:", photo_count)
print("Stickers observed:", len(observed))

assert observed == required

#Expected movements depend on restoration setting
if RESTORE_ORIGINAL_STATE:
    assert motor_stages == 20
    assert face_turns == 34
else:
    assert motor_stages == 14
    assert face_turns == 25

assert photo_count == 12
assert len(set(tracker.positions.values())) == 54


# NEW - Reconstruct colors at the FINAL cube positions
reconstructed_colors = {}

for face in FACE_ORDER:
    for index in range(9):
        position = f"{face}{index}"

        # Find which original sticker currently occupies this position
        sticker = tracker.positions[position]

        if index == 4:
            # Centers are fixed and their colors are known
            reconstructed_colors[position] = FACE_TO_COLOR[face]
        else:
            # Retrieve the color we observed during scanning
            reconstructed_colors[position] = observed_colors[sticker]


# NEW - Independently check against our simulated starting colors
expected_final_colors = {}

for position, sticker in tracker.positions.items():
    expected_final_colors[position] = starting_colors[sticker]

assert reconstructed_colors == expected_final_colors
print("\nFinal cube reconstruction: PASSED")


# NEW - Convert the reconstructed colors into Kociemba format
cube_string = ""

for face in FACE_ORDER:
    for index in range(9):
        position = f"{face}{index}"
        color = reconstructed_colors[position]
        cube_string += COLOR_TO_FACE[color]


# NEW - Verify the final cube string
assert len(cube_string) == 54
assert all(cube_string.count(face) == 9 for face in FACE_ORDER)

print("\nReconstructed cube string:")
print(cube_string)
print("Cube string formatting: PASSED")


# NEW - Verify the reconstructed cube with Kociemba
print("\n--- Kociemba Verification ---")

solution = kociemba.solve(cube_string)

print("Cube accepted by Kociemba: PASSED")
print("Solution:", solution)
print("Number of moves:", len(solution.split()))


print("\nAll scanning sequence tests PASSED!")
