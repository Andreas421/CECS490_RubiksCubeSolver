import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera unavailable")
    exit()

# HSV color ranges
color_ranges = {
    "red1": (np.array([0, 120, 70]), np.array([10, 255, 255])),
    "red2": (np.array([170, 120, 70]), np.array([180, 255, 255])),
    "green": (np.array([35, 80, 50]), np.array([85, 255, 255])),
    "blue": (np.array([90, 80, 50]), np.array([130, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([35, 255, 255])),
    "orange": (np.array([10, 100, 100]), np.array([20, 255, 255])),
    "white": (np.array([0, 0, 180]), np.array([180, 70, 255]))
}

# NEW: helper function so we can reuse color detection for each grid cell
def detect_cell_color(hsv_cell):
    color_counts = {}

    for color_name, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_cell, lower, upper)
        count = cv2.countNonZero(mask)
        color_counts[color_name] = count

    # combine reds (same as your original logic)
    red_count = color_counts["red1"] + color_counts["red2"]

    final_counts = {
        "red": red_count,
        "green": color_counts["green"],
        "blue": color_counts["blue"],
        "yellow": color_counts["yellow"],
        "orange": color_counts["orange"],
        "white": color_counts["white"]
    }

    detected_color = max(final_counts, key=final_counts.get)
    max_count = final_counts[detected_color]

    # CHANGED: lower threshold because each grid cell has fewer pixels
    if max_count < 150:   # was 500 in your original
        return "unknown"

    return detected_color


while True:
    ret, frame = cap.read()
    if not ret:
        break

    #frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape

    # CHANGED: slightly bigger ROI so each of the 9 cells has enough pixels
    box_size = 180   # was 100
    x1 = w // 2 - box_size // 2
    y1 = h // 2 - box_size // 2
    x2 = x1 + box_size
    y2 = y1 + box_size

    roi = frame[y1:y2, x1:x2]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # NEW: define grid size (3x3)
    cell_size = box_size // 3   # splits ROI into 9 equal squares

    grid_colors = []  # NEW: stores detected colors like a 3x3 matrix

    # NEW: loop through rows and columns
    for row in range(3):
        row_colors = []
        for col in range(3):

            # NEW: calculate each cell's position inside ROI
            cx1 = col * cell_size
            cy1 = row * cell_size
            cx2 = cx1 + cell_size
            cy2 = cy1 + cell_size

            # NEW: extract that cell
            cell = hsv_roi[cy1:cy2, cx1:cx2]

            # NEW: detect color for this cell
            detected_color = detect_cell_color(cell)
            row_colors.append(detected_color)

            # NEW: map cell coords back to original frame
            abs_x1 = x1 + cx1
            abs_y1 = y1 + cy1
            abs_x2 = x1 + cx2
            abs_y2 = y1 + cy2

            # NEW: draw grid cell rectangle
            cv2.rectangle(frame, (abs_x1, abs_y1), (abs_x2, abs_y2), (0, 0, 0), 1)

            # NEW: label each grid cell with detected color
            cv2.putText(
                frame,
                detected_color,
                (abs_x1 + 5, abs_y1 + cell_size // 2),
                cv2.FONT_HERSHEY_PLAIN,
                0.8,
                (0, 0, 0),
                1
            )

        grid_colors.append(row_colors)

    # CHANGED: outer box still drawn, but now represents full 3x3 grid
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)

    # NEW: optional debug print of 3x3 grid when p is pressed (like a Rubik’s cube face)
    confirm = cv2.waitKey(1) & 0xFF #new: store key press

    if confirm == ord('p'): #only print to terminal when 'p' pressed
        print("\n--- Captured Face ---")
        for row in grid_colors:
            print(" ".join(row))

    cv2.imshow("Color Box Reader 3x3", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()