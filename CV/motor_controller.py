import time


# NEW - Simulates motor movements without physical hardware
class SimulatedMotorController:
    def __init__(self):
        self.move_delay = 0.5  # Simulated motor movement time

    def move(self, command):
        # NEW - Display the requested motor movement
        print(f"[MOTOR] Executing: {command}")

        # NEW - Simulate waiting for motor completion
        time.sleep(self.move_delay)

        # NEW - Simulate Arduino completion acknowledgement
        print("[MOTOR] DONE")
        return True


#Motor controller using Arduino-style serial communication
class ArduinoMotorController:
    def __init__(self, connection):
        self.connection = connection
        self.command_id = 0

    def move(self, command):
        # NEW - Give each movement a unique command ID
        self.command_id += 1

        # NEW - Format and send movement instruction
        message = f"MOVE {self.command_id} {command}\n"
        self.connection.write(message.encode("ascii"))

        # NEW - Wait for Arduino completion response
        response = self.connection.readline().decode("ascii").strip()

        # NEW - Confirm the correct movement completed
        if response == f"DONE {self.command_id}":
            return True

        # NEW - Handle missing acknowledgment
        if not response:
            raise TimeoutError("Arduino did not respond.")

        # NEW - Reject unexpected or incorrect responses
        raise RuntimeError(f"Unexpected Arduino response: {response}")


# NEW - Temporary motor controller test
if __name__ == "__main__":
    motor = SimulatedMotorController()

    motor.move("F+B")
    motor.move("R+L'")
    motor.move("F")

    print("\nMotor simulation test PASSED!")
