import cv2

from cube_capture import CubeCapture
from cube_config import BOX_SIZE, CAMERA_INDEX, COLOR_RANGES, FLIP_PREVIEW, MIN_COLOR_PIXELS
from cube_solver import solve_cube
from input_reformat import reformat_cube_state


def detect_cell_color(hsv_cell):
    color_counts = {}

    for color_name, (lower, upper) in COLOR_RANGES.items():
        mask = cv2.inRange(hsv_cell, lower, upper)
        color_counts[color_name] = cv2.countNonZero(mask)

    final_counts = {
        "red": color_counts["red1"] + color_counts["red2"],
        "green": color_counts["green"],
        "blue": color_counts["blue"],
        "yellow": color_counts["yellow"],
        "orange": color_counts["orange"],
        "white": color_counts["white"],
    }

    detected_color = max(final_counts, key=final_counts.get)

    if final_counts[detected_color] < MIN_COLOR_PIXELS:
        return "unknown"

    return detected_color


def read_grid(frame):
    height, width, _ = frame.shape
    x1 = width // 2 - BOX_SIZE // 2
    y1 = height // 2 - BOX_SIZE // 2
    x2 = x1 + BOX_SIZE
    y2 = y1 + BOX_SIZE

    roi = frame[y1:y2, x1:x2]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    cell_size = BOX_SIZE // 3
    grid_colors = []

    for row in range(3):
        row_colors = []
        for col in range(3):
            cx1 = col * cell_size
            cy1 = row * cell_size
            cx2 = cx1 + cell_size
            cy2 = cy1 + cell_size

            cell = hsv_roi[cy1:cy2, cx1:cx2]
            detected_color = detect_cell_color(cell)
            row_colors.append(detected_color)

            abs_x1 = x1 + cx1
            abs_y1 = y1 + cy1
            abs_x2 = x1 + cx2
            abs_y2 = y1 + cy2

            cv2.rectangle(frame, (abs_x1, abs_y1), (abs_x2, abs_y2), (0, 0, 0), 1)
            cv2.putText(
                frame,
                detected_color,
                (abs_x1 + 5, abs_y1 + cell_size // 2),
                cv2.FONT_HERSHEY_PLAIN,
                0.8,
                (0, 0, 0),
                1,
            )

        grid_colors.append(row_colors)

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
    return grid_colors


def print_face(face_matrix):
    print("\n--- Captured Face ---")
    for row in face_matrix:
        print(" ".join(row))


def try_solve(cube_capture):
    print("\n--- All 6 faces captured ---")
    cube_capture.print_color_counts()

    if not cube_capture.validate_cube():
        print("Cube validation failed.")
        return

    print("Cube validation passed.")
    cube_string = reformat_cube_state(cube_capture.get_faces())

    print("\n--- Full Cube String ---")
    print(cube_string)

    print("\n--- Solve Instructions ---")
    print(solve_cube(cube_string))


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cube_capture = CubeCapture()

    if not cap.isOpened():
        print("Camera unavailable")
        return

    print("Controls: p = save current face, r = reset cube, q = quit")

    while True:
        success, frame = cap.read()
        if not success:
            break
        '''
        if FLIP_PREVIEW:
            frame = cv2.flip(frame, 1)
        '''
        grid_colors = read_grid(frame)
        cv2.imshow("Rubik's Cube Scanner", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("p"):
            was_saved = cube_capture.add_face(grid_colors)
            cube_capture.print_captured_faces()
            print_face(grid_colors)

            if was_saved and cube_capture.is_complete():
                try_solve(cube_capture)

        elif key == ord("r"):
            cube_capture.reset()

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
