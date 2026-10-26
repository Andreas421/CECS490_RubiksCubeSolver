import cv2
import time
import numpy as np

from cube_config import CAMERA_INDEX
from color_detector_step1 import read_grid
from collections import Counter  
from cube_config import COLOR_TO_FACE  
from cube_config import CAMERA_INDEX, BOX_SIZE  
from color_detector_step1 import read_grid, detect_cell_color  

#Real camera interface for scanning
class OpenCVCamera:
    def __init__(self):
        #Open the physical camera
        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self.cap.isOpened():
            raise RuntimeError("Camera unavailable")

    # Capture multiple frames and verify color consistency
    def capture(self, visible_facelets=None):
        # Allow camera/cube image to stabilize
        time.sleep(0.2)

        # Discard 2 potentially buffered frames
        for i in range(2):
            if not self.cap.grab():
                raise RuntimeError("Failed to refresh camera frame")
        
        samples = []
 
        # Collect 5 separate camera frames
        for i in range(5):
            success, frame = self.cap.read()

            if not success:
                raise RuntimeError("Failed to capture camera frame")

            grid_colors = read_grid(frame, draw_preview=False)
            samples.append(grid_colors)

        # Determine the most consistent color for each cell
        final_grid = []

        for row in range(3):
            row_colors = []

            for col in range(3):

                # Get this cell's color across all 5 frames
                readings = [
                    sample[row][col] for sample in samples
                ]

                # Find most frequently detected color
                color, count = Counter(readings).most_common(1)[0]

                # Require at least 4 matching readings
                if count < 4 or color not in COLOR_TO_FACE:
                    raise ValueError(
                        f"Unstable color at row {row + 1}, "
                        f"col {col + 1}: {readings}"
                    )

                row_colors.append(color)

            final_grid.append(row_colors)

        return final_grid

    #Provide a live preview with our detection grid
    def preview_frame(self):
        success, frame = self.cap.read()

        if not success:
            raise RuntimeError("Failed to read camera frame")

        read_grid(frame, draw_preview=True)

        return frame
   
    # Read HSV values from the center sticker
    def inspect_center_hsv(self):
        success, frame = self.cap.read()

        if not success:
            raise RuntimeError("Failed to read camera frame")

        height, width = frame.shape[:2]

        # Match our existing center-only sampling area
        cell_size = BOX_SIZE // 3
        sample_margin = cell_size // 5
        half_size = cell_size // 2 - sample_margin

        center_x = width // 2
        center_y = height // 2

        # Extract center 60% of the middle sticker
        sample = frame[
            center_y - half_size:center_y + half_size,
            center_x - half_size:center_x + half_size
        ]

        # Convert BGR to HSV
        hsv_sample = cv2.cvtColor(sample, cv2.COLOR_BGR2HSV)

        # Calculate median HSV values
        pixels = hsv_sample.reshape(-1, 3)
        hsv_values = np.median(pixels, axis=0).astype(int)

        # Identify color using existing detection function
        detected_color = detect_cell_color(hsv_sample)

        print(
            f"HSV: H={hsv_values[0]}, "
            f"S={hsv_values[1]}, "
            f"V={hsv_values[2]}"
        )
        print("Detected color:", detected_color)

    #Release the camera when finished
    def close(self):
        self.cap.release()


#Temporary real camera test
if __name__ == "__main__":
    camera = OpenCVCamera()

    print("Controls: p = capture colors, h = inspect HSV, q = quit")

    try:
        while True:
            frame = camera.preview_frame()

            cv2.imshow("Real Camera Test", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("p"):
                grid_colors = camera.capture()

                print("\n--- Captured Colors ---")
                for row in grid_colors:
                    print(" ".join(row))
                      
            elif key == ord("h"):
                camera.inspect_center_hsv()

            elif key == ord("q"):
                break

    finally:
        camera.close()
        cv2.destroyAllWindows()
