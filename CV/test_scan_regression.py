import random
import unittest
import kociemba

from scan_engine import ScanEngine, SimulatedCamera
from motor_controller import SimulatedMotorController
from cube_config import FACE_ORDER, COLOR_TO_FACE  # NEW
from facelet_tracker import FaceletTracker  # NEW


class TestScanEngine(unittest.TestCase):

    # NEW - Helper to create a fresh scanning system for each test
    def create_engine(self, restore=False, scramble_moves=None):  # CHANGED
        motor = SimulatedMotorController()
        motor.move_delay = 0

        camera = SimulatedCamera(scramble_moves)  # CHANGED

        return ScanEngine(
            motor,
            camera,
            restore_original_state=restore
        )


    # TEST 1 - Verify scanning without restoration
    def test_25_turn_scan(self):
        engine = self.create_engine(restore=False)
        cube_string = engine.run_scan()

        self.assertEqual(engine.motor_stages, 14)
        self.assertEqual(engine.face_turns, 25)
        self.assertEqual(engine.photo_count, 12)
        self.assertEqual(len(engine.observed_colors), 48)

        # NEW - Verify Kociemba accepts the reconstructed state
        solution = kociemba.solve(cube_string)
        self.assertTrue(isinstance(solution, str))

    # TEST 2 - Verify scanning with restoration
    def test_34_turn_scan(self):
        engine = self.create_engine(restore=True)
        cube_string = engine.run_scan()

        self.assertEqual(engine.motor_stages, 20)
        self.assertEqual(engine.face_turns, 34)
        self.assertEqual(engine.photo_count, 12)
        self.assertEqual(len(engine.observed_colors), 48)

        # NEW - Verify restoration returned all stickers home
        for position, sticker in engine.tracker.positions.items():
            self.assertEqual(position, sticker)

        solution = kociemba.solve(cube_string)
        self.assertTrue(isinstance(solution, str))

    # TEST 3 - Verify conflicting captures don't change saved colors
    def test_conflicting_capture(self):
        engine = self.create_engine()

        # Save a valid initial capture
        engine.capture_top()

        original_colors = engine.observed_colors.copy()
        original_observed = engine.observed.copy()
        original_photos = engine.photo_count

        # NEW - Generate a second capture with one incorrect color
        grid = engine.camera.capture(engine.tracker.get_visible_top())
        grid[2][2] = "red" if grid[2][2] != "red" else "blue"

        class BadCamera:
            def capture(self, visible_facelets=None):
                return grid

        engine.camera = BadCamera()

        # NEW - Conflicting capture should raise an error
        with self.assertRaises(ValueError):
            engine.capture_top()

        # NEW - Verify saved data was not modified
        self.assertEqual(engine.observed_colors, original_colors)
        self.assertEqual(engine.observed, original_observed)
        self.assertEqual(engine.photo_count, original_photos)

    # TEST 4 - Verify motor failures stop scanning
    def test_motor_failure(self):

        class FailedMotor:
            def move(self, command):
                return False

        engine = ScanEngine(FailedMotor(), SimulatedCamera())
        original_positions = engine.tracker.positions.copy()

        # NEW - A failed movement must raise an error
        with self.assertRaises(RuntimeError):
            engine.execute_move("F")

        # NEW - Tracker must not advance after failure
        self.assertEqual(engine.tracker.positions, original_positions)
        self.assertEqual(engine.motor_stages, 0)
        self.assertEqual(engine.face_turns, 0)

    # TEST 5 - Verify incomplete scans cannot be reconstructed
    def test_incomplete_scan(self):
        engine = self.create_engine()

        # NEW - No stickers have been captured yet
        with self.assertRaises(ValueError):
            engine.reconstruct_cube()
    
    # TEST 6 - Verify multiple legal scrambles in both scanning modes
    def test_multiple_scrambles(self):
        rng = random.Random(490)  # NEW - Repeatable random tests

        possible_moves = [
            "F", "F'", "F2",
            "R", "R'", "R2",
            "B", "B'", "B2",
            "L", "L'", "L2"
        ]

        # NEW - Test both restoration configurations
        for restore in [False, True]:

            # NEW - Test 5 different scrambles per configuration
            for test_number in range(5):

                scramble = [
                    rng.choice(possible_moves)
                    for i in range(20)
                ]

                with self.subTest(restore=restore, test=test_number):
                    engine = self.create_engine(
                        restore=restore,
                        scramble_moves=scramble
                    )

                    cube_string = engine.run_scan()

                    # Verify all non-center colors were recorded
                    self.assertEqual(len(engine.observed_colors), 48)

                    # Verify cube string length
                    self.assertEqual(len(cube_string), 54)

                    # NEW - Verify reconstruction against simulated truth
                    expected_string = ""

                    for face in FACE_ORDER:
                        for index in range(9):
                            position = f"{face}{index}"
                            sticker = engine.tracker.positions[position]
                            color = engine.camera.starting_colors[sticker]
                            expected_string += COLOR_TO_FACE[color]

                    self.assertEqual(cube_string, expected_string)

                    # NEW - Verify cube is accepted by Kociemba
                    solution = kociemba.solve(cube_string)
                    self.assertIsInstance(solution, str)
    
    # TEST 7 - Reject incorrect starting orientation
    def test_incorrect_initial_orientation(self):

        # NEW - Simulate a camera with a green top center
        class WrongCenterCamera(SimulatedCamera):
            def capture(self, visible_facelets=None):
                grid = super().capture(visible_facelets)
                grid[1][1] = "green"
                return grid

        motor = SimulatedMotorController()
        motor.move_delay = 0

        engine = ScanEngine(
            motor,
            WrongCenterCamera(),
            restore_original_state=False
        )

        original_positions = engine.tracker.positions.copy()

        # NEW - Scanning should reject the incorrect center
        with self.assertRaises(ValueError):
            engine.run_scan()

        # NEW - Verify no observations or movements were saved
        self.assertEqual(engine.photo_count, 0)
        self.assertEqual(len(engine.observed_colors), 0)
        self.assertEqual(engine.motor_stages, 0)
        self.assertEqual(engine.face_turns, 0)
        self.assertEqual(engine.tracker.positions, original_positions)

    
    # TEST 8 - Verify automatic camera retries
    def test_camera_retries(self):

        # NEW - Simulate a camera failing twice before succeeding
        class FlakyCamera(SimulatedCamera):
            def __init__(self):
                super().__init__()
                self.attempts = 0

            def capture(self, visible_facelets=None):
                self.attempts += 1

                if self.attempts <= 2:
                    raise ValueError("Simulated unstable color")

                return super().capture(visible_facelets)

        motor = SimulatedMotorController()
        motor.move_delay = 0

        camera = FlakyCamera()

        engine = ScanEngine(
            motor,
            camera,
            restore_original_state=False
        )

        cube_string = engine.run_scan()

        # NEW - Two failed attempts plus 12 successful captures
        self.assertEqual(camera.attempts, 14)

        # NEW - Failed captures must not cause extra movements
        self.assertEqual(engine.motor_stages, 14)
        self.assertEqual(engine.face_turns, 25)

        # NEW - Only successful captures are counted
        self.assertEqual(engine.photo_count, 12)
        self.assertEqual(len(engine.observed_colors), 48)

        # NEW - Reconstructed cube must remain valid
        self.assertIsInstance(kociemba.solve(cube_string), str)

    
    # TEST 9 - Verify scanning stops after 3 failed camera attempts
    def test_camera_complete_failure(self):

        # NEW - Simulate a camera that always fails
        class FailedCamera:
            def __init__(self):
                self.attempts = 0

            def capture(self, visible_facelets=None):
                self.attempts += 1
                raise ValueError("Simulated camera failure")

        motor = SimulatedMotorController()
        motor.move_delay = 0

        camera = FailedCamera()

        engine = ScanEngine(
            motor,
            camera,
            restore_original_state=False
        )

        original_positions = engine.tracker.positions.copy()

        # NEW - Scanning must stop after all retries fail
        with self.assertRaises(ValueError):
            engine.run_scan()

        # NEW - Verify exactly 3 capture attempts
        self.assertEqual(camera.attempts, 3)

        # NEW - Verify no motors were commanded
        self.assertEqual(engine.motor_stages, 0)
        self.assertEqual(engine.face_turns, 0)

        # NEW - Verify no observations were saved
        self.assertEqual(engine.photo_count, 0)
        self.assertEqual(len(engine.observed_colors), 0)

        # NEW - Verify tracker positions remain unchanged
        self.assertEqual(engine.tracker.positions, original_positions)

    
    # TEST 10 - Verify camera failure after several motor movements
    def test_camera_failure_mid_scan(self):

        # NEW - Camera succeeds 3 times, then always fails
        class MidScanFailureCamera(SimulatedCamera):
            def __init__(self):
                super().__init__()
                self.attempts = 0

            def capture(self, visible_facelets=None):
                self.attempts += 1

                if self.attempts >= 4:
                    raise ValueError("Simulated mid-scan camera failure")

                return super().capture(visible_facelets)

        # NEW - Record every motor command
        class RecordingMotor(SimulatedMotorController):
            def __init__(self):
                super().__init__()
                self.move_delay = 0
                self.commands = []

            def move(self, command):
                self.commands.append(command)
                return super().move(command)

        motor = RecordingMotor()
        camera = MidScanFailureCamera()

        # NEW - Enable restoration to verify it does NOT run after failure
        engine = ScanEngine(
            motor,
            camera,
            restore_original_state=True
        )

        # NEW - Scanner should stop when all retries fail
        with self.assertRaises(ValueError):
            engine.run_scan()

        # NEW - 3 successful captures + 3 failed attempts
        self.assertEqual(camera.attempts, 6)
        self.assertEqual(engine.photo_count, 3)

        # NEW - Verify no extra motor movements occurred
        self.assertEqual(motor.commands, ["F+B"] * 3)
        self.assertEqual(engine.motor_stages, 3)
        self.assertEqual(engine.face_turns, 6)

        # NEW - Previously recorded colors must remain correct
        expected_colors = {
            sticker: camera.starting_colors[sticker]
            for sticker in engine.observed
        }

        self.assertEqual(engine.observed_colors, expected_colors)
        self.assertGreater(len(engine.observed_colors), 8)
        self.assertLess(len(engine.observed_colors), 48)

        # NEW - Verify tracker stopped at the correct position
        expected_tracker = FaceletTracker()

        for i in range(3):
            expected_tracker.rotate("F+B")

        self.assertEqual(
            engine.tracker.positions,
            expected_tracker.positions
        )

        # NEW - Confirm the cube was NOT restored
        original_tracker = FaceletTracker()

        self.assertNotEqual(
            engine.tracker.positions,
            original_tracker.positions
        )

    
    # TEST 11 - Verify motor failure during scanning
    def test_motor_failure_mid_scan(self):

        # NEW - Motor fails on the fourth movement
        class MidScanFailureMotor(SimulatedMotorController):
            def __init__(self):
                super().__init__()
                self.move_delay = 0
                self.commands = []

            def move(self, command):
                self.commands.append(command)

                # NEW - Simulate failure on fourth command
                if len(self.commands) == 4:
                    print("[MOTOR] ERROR: Movement failed")
                    return False

                return super().move(command)

        motor = MidScanFailureMotor()
        camera = SimulatedCamera()

        # NEW - Enable restoration to check that it never starts
        engine = ScanEngine(
            motor,
            camera,
            restore_original_state=True
        )

        # NEW - Scanner must stop when motor reports failure
        with self.assertRaises(RuntimeError):
            engine.run_scan()

        # NEW - Four commands attempted, only three completed
        self.assertEqual(len(motor.commands), 4)
        self.assertEqual(motor.commands, ["F+B"] * 4)

        self.assertEqual(engine.motor_stages, 3)
        self.assertEqual(engine.face_turns, 6)

        # NEW - Initial capture + three successful movements
        self.assertEqual(engine.photo_count, 4)

        # NEW - Tracker should only contain successful rotations
        expected_tracker = FaceletTracker()

        for i in range(3):
            expected_tracker.rotate("F+B")

        self.assertEqual(
            engine.tracker.positions,
            expected_tracker.positions
        )

        # NEW - Previously recorded observations are preserved
        expected_colors = {
            sticker: camera.starting_colors[sticker]
            for sticker in engine.observed
        }

        self.assertEqual(engine.observed_colors, expected_colors)
        self.assertGreater(len(engine.observed_colors), 0)

        # NEW - No additional movements or restoration attempted
        self.assertEqual(motor.commands, ["F+B"] * 4)


# NEW - Run all tests automatically
if __name__ == "__main__":
    unittest.main()
