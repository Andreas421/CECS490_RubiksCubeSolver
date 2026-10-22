import cv2

from cube_config import BOX_SIZE, COLOR_RANGES, MIN_COLOR_PIXELS


# Detect the color of a single sticker using HSV values
def detect_cell_color(hsv_cell):
    color_counts = {}

    for color_name, (lower, upper) in COLOR_RANGES.items():
        mask = cv2.inRange(hsv_cell, lower, upper)
        color_counts[color_name] = cv2.countNonZero(mask)

    # Red requires two HSV ranges
    final_counts = {
        "red": color_counts["red1"] + color_counts["red2"],
        "green": color_counts["green"],
        "blue": color_counts["blue"],
        "yellow": color_counts["yellow"],
        "orange": color_counts["orange"],
        "white": color_counts["white"]
    }

    detected_color = max(final_counts, key=final_counts.get)

    # Reject colors with insufficient matching pixels
    if final_counts[detected_color] < MIN_COLOR_PIXELS:
        return "unknown"

    return detected_color


# Read the colors of all 9 stickers in the camera's 3x3 grid
def read_grid(frame, draw_preview=True):

    height, width, _ = frame.shape

    # Define detection box at the center of the image
    x1 = width // 2 - BOX_SIZE // 2
    y1 = height // 2 - BOX_SIZE // 2
    x2 = x1 + BOX_SIZE
    y2 = y1 + BOX_SIZE

    # Extract region of interest and convert to HSV
    roi = frame[y1:y2, x1:x2]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Divide detection box into 9 equal cells
    cell_size = BOX_SIZE // 3

    # Sample only center 60% to avoid borders and reflections
    sample_margin = cell_size // 5

    grid_colors = []

    for row in range(3):
        row_colors = []

        for col in range(3):

            # Calculate the current cell's position
            cx1 = col * cell_size
            cy1 = row * cell_size
            cx2 = cx1 + cell_size
            cy2 = cy1 + cell_size

            # Extract only the central area of the sticker
            cell = hsv_roi[
                cy1 + sample_margin:cy2 - sample_margin,
                cx1 + sample_margin:cx2 - sample_margin
            ]

            # Detect sticker color
            detected_color = detect_cell_color(cell)
            row_colors.append(detected_color)

            # Draw preview grid only when requested
            if draw_preview:

                abs_x1 = x1 + cx1
                abs_y1 = y1 + cy1
                abs_x2 = x1 + cx2
                abs_y2 = y1 + cy2

                cv2.rectangle(
                    frame,
                    (abs_x1, abs_y1),
                    (abs_x2, abs_y2),
                    (0, 0, 0),
                    1
                )

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

    # Draw the outer detection box
    if draw_preview:
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 0, 0),
            2
        )

    return grid_colors
