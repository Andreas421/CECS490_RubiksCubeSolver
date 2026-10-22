from motor_controller import ArduinoMotorController
from scan_engine import ScanEngine, SimulatedCamera  
from facelet_tracker import FaceletTracker  # NEW

# NEW - Simulates the Arduino serial connection
class FakeArduinoSerial:
    def __init__(self):
        self.last_command_id = None

    def write(self, data):
        message = data.decode("ascii").strip()
        print("[Pi -> Arduino]", message)

        # Extract command ID from MOVE instruction
        parts = message.split()
        self.last_command_id = parts[1]

    def readline(self):
        # Simulate Arduino movement-complete acknowledgement
        response = f"DONE {self.last_command_id}\n"

        print("[Arduino -> Pi]", response.strip())

        return response.encode("ascii")


# NEW - Simulate incorrect Arduino responses
class FaultyArduinoSerial:
    def __init__(self, response):
        self.response = response
        self.last_message = None

    def write(self, data):
        # NEW - Record the command sent by Raspberry Pi
        self.last_message = data.decode("ascii").strip()

    def readline(self):
        # NEW - Return our intentionally incorrect response
        return self.response.encode("ascii")


# NEW - Test communication
if __name__ == "__main__":
    connection = FakeArduinoSerial()
    motor = ArduinoMotorController(connection)

    assert motor.move("F+B")
    assert motor.move("R+L'")
    assert motor.move("F")

    
    # NEW - Test Arduino communication with full scanning engine
    for restore in [False, True]:

        # NEW - Create fresh virtual Arduino and camera
        connection = FakeArduinoSerial()
        motor = ArduinoMotorController(connection)
        camera = SimulatedCamera()

        # NEW - Connect Arduino-style motor controller to ScanEngine
        engine = ScanEngine(
            motor,
            camera,
            restore_original_state=restore
        )

        # NEW - Run full scanning process
        cube_string = engine.run_scan()

        # NEW - Determine expected results for each mode
        expected_stages = 20 if restore else 14
        expected_turns = 34 if restore else 25

        # NEW - Verify motor commands and acknowledgments
        assert motor.command_id == expected_stages
        assert connection.last_command_id == str(expected_stages)

        # NEW - Verify scanning results
        assert engine.motor_stages == expected_stages
        assert engine.face_turns == expected_turns
        assert engine.photo_count == 12
        assert len(engine.observed_colors) == 48
        assert len(cube_string) == 54

        print(f"\nArduino scan test (restore={restore}): PASSED")

    
    # NEW - Test incorrect acknowledgment ID
    connection = FaultyArduinoSerial("DONE 999\n")
    motor = ArduinoMotorController(connection)

    try:
        motor.move("F")
        raise AssertionError("Incorrect ACK was accepted")
    except RuntimeError as error:
        print("Incorrect ACK test: PASSED")


    # NEW - Test missing Arduino response
    connection = FaultyArduinoSerial("")
    motor = ArduinoMotorController(connection)

    try:
        motor.move("R")
        raise AssertionError("Timeout was not detected")
    except TimeoutError as error:
        print("Communication timeout test: PASSED")


    # NEW - Test Arduino motor error response
    connection = FaultyArduinoSerial("ERR 1 JAM\n")
    motor = ArduinoMotorController(connection)

    try:
        motor.move("B")
        raise AssertionError("Motor error was accepted")
    except RuntimeError as error:
        print("Arduino error response test: PASSED")


    print("\nArduino communication test PASSED!")

    
    # NEW - Verify scanner stops after incorrect Arduino ACK
    connection = FaultyArduinoSerial("DONE 999\n")
    motor = ArduinoMotorController(connection)
    camera = SimulatedCamera()

    engine = ScanEngine(
        motor,
        camera,
        restore_original_state=True
    )

    try:
        engine.run_scan()
        raise AssertionError("Scanning continued after motor error")
    except RuntimeError:
        print("ScanEngine motor error handling: PASSED")

    # NEW - Confirm no movements were recorded
    assert engine.motor_stages == 0
    assert engine.face_turns == 0

    # NEW - Initial camera capture should still be saved
    assert engine.photo_count == 1

    # NEW - Tracker must remain at its original position
    original_tracker = FaceletTracker()
    assert engine.tracker.positions == original_tracker.positions

    # NEW - Confirm only the first motor command was sent
    assert connection.last_message == "MOVE 1 F+B"

    print("Tracker synchronization test: PASSED")

