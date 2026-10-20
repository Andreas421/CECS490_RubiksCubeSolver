import cv2

from cube_config import CAMERA_INDEX
from color_detector_step1 import read_grid
from collections import Counter  # NEW
from cube_config import COLOR_TO_FACE  # NEW


#Real camera interface for scanning
class OpenCVCamera:
    def __init__(self):
        #Open the physical camera
        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self.cap.isOpened():
            raise RuntimeError("Camera unavailable")

    #Capture multiple frames and verify color consistency
    def capture(self, visible_facelets=None):
        samples = []

        # NEW - Collect 5 separate camera frames
        for i in range(5):
            success, frame = self.cap.read()

            if not success:
                raise RuntimeError("Failed to capture camera frame")

            grid_colors = read_grid(frame, draw_preview=False)
            samples.append(grid_colors)

        # NEW - Determine the most consistent color for each cell
        final_grid = []

        for row in range(3):
            row_colors = []

            for col in range(3):

                # NEW - Get this cell's color across all 5 frames
                readings = [
                    sample[row][col] for sample in samples
                ]

                # NEW - Find most frequently detected color
                color, count = Counter(readings).most_common(1)[0]

                # NEW - Require at least 4 matching readings
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

    #Release the camera when finished
    def close(self):
        self.cap.release()


#Temporary real camera test
if __name__ == "__main__":
    camera = OpenCVCamera()

    print("Controls: p = capture colors, q = quit")

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

            elif key == ord("q"):
                break

    finally:
        camera.close()
        cv2.destroyAllWindows()
