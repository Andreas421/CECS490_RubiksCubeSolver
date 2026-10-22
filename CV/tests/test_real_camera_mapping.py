
import cv2

from real_camera import OpenCVCamera
from motor_controller import SimulatedMotorController
from scan_engine import ScanEngine
from cube_config import FACE_TO_COLOR


# NEW - Initialize real camera and scanning engine
camera = OpenCVCamera()
motor = SimulatedMotorController()

engine = ScanEngine(
    motor,
    camera,
    restore_original_state=False
)

print("Controls: p = capture top face, q = quit")

try:
    while True:
        # NEW - Display real camera preview
        frame = camera.preview_frame()
        cv2.imshow("Camera Mapping Test", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("p"):

            # NEW - Capture through ScanEngine
            try:
                grid_colors = engine.capture_top()
            except ValueError as error:
                print("Capture rejected:", error)
                print("Colors stored:", len(engine.observed_colors))
                print("Successful photos:", engine.photo_count) 
                continue

            print("\n--- Detected Colors ---")
            for row in grid_colors:
                print(" ".join(row))

            # NEW - Compare detected colors with tracked positions
            visible = engine.tracker.get_visible_top()

            print("\n--- Sticker Mapping ---")
            for row in range(3):
                for col in range(3):
                    sticker = visible[row][col]
                    color = grid_colors[row][col]

                    print(f"{sticker}: {color}")

            # NEW - Check our expected top center color
            if grid_colors[1][1] != FACE_TO_COLOR["U"]:
                print("WARNING: Top center should be white.")

            print("\nColors stored:", len(engine.observed_colors))

        # NEW - Reset captured sticker observations
        elif key == ord("r"):
            engine = ScanEngine(
                motor,
                camera,
                restore_original_state=False
            )
            print("\nCaptured observations reset.")

        elif key == ord("q"):
            break
                
finally:
    camera.close()
    cv2.destroyAllWindows()
