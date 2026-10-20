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


# NEW - Temporary motor controller test
if __name__ == "__main__":
    motor = SimulatedMotorController()

    motor.move("F+B")
    motor.move("R+L'")
    motor.move("F")

    print("\nMotor simulation test PASSED!")
