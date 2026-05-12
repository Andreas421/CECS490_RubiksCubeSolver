import cv2
from input_reformat import reformat_face_state, reformat_cube_state
from cube_config import color_ranges
from cube_capture import CubeCapture

cap = cv2.VideoCapture(0) 
cube_capture = CubeCapture()

if not cap.isOpened():
    print("Camera unavailable")
    exit()


#helper function - single cell color detector for reusability
def detect_cell_color(hsv_cell):
    color_counts = {}

    for color_name, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_cell, lower, upper)   # fixed
        count = cv2.countNonZero(mask)
        color_counts[color_name] = count

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

    if max_count < 150:
        return "unknown"

    return detected_color

#main loop
while True:
    #ensure camera can grab a frame before proceeding
    returnVal, frame = cap.read() 
    if not returnVal : break

    #make frame like a mirror so our left is camera's left, etc.
    frame = cv2.flip(frame, 1) #just for testing, will be removed later

    #rectangle parameters
    h, w, _ = frame.shape #h=height, w=width, _=color channels
                            #_ = don't care, we aren't using channels in this case   
    
    #box in center of screen
    box_size = 180
    x1 = w // 2 - box_size // 2  
    y1 = h // 2 - box_size // 2  
    x2 = x1 + box_size  
    y2 = y1 + box_size 

    #set region of interest to the box we just created
    roi = frame[y1:y2, x1:x2]
    #convert colors in that box from rgb to HSV (hue, saturation, value)
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    #define grid 
    cell_size = box_size // 3 #split roi into 9 equal squares

    grid_colors = [] #store detected colors like a 3x3 matrix

    #loop through rows and columns
    for row in range(3):
        row_colors = []
        for col in range(3):
            #calc each cell's position in ROI
            cx1 = col * cell_size
            cy1 = row * cell_size
            cx2 = cx1 + cell_size
            cy2 = cy1 + cell_size

            #extract cell & detect color
            cell = hsv_roi[cy1:cy2, cx1:cx2]
            detected_color = detect_cell_color(cell)
            row_colors.append(detected_color)

            #map cell coords back to frame
            abs_x1 = x1 + cx1
            abs_y1 = y1 + cy1
            abs_x2 = x1 + cx2
            abs_y2 = y1 + cy2

            #draw grid cell rectangle
            cv2.rectangle(frame, (abs_x1, abs_y1), (abs_x2, abs_y2), (0,0,0), 1)
              
            #label each cell with detected color
            cv2.putText(frame, detected_color, (abs_x1 + 5, abs_y1 + cell_size // 2),
                        cv2.FONT_HERSHEY_PLAIN, 0.8, (0,0,0), 1)

        grid_colors.append(row_colors)

    # Flip detected data horizontally
    # ------ JUST FOR TESTING ----------------
    grid_colors = [row[::-1] for row in grid_colors]
    
    #draw box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)

    confirm = cv2.waitKey(1) & 0xFF

    if confirm == ord('p'):
        was_saved = cube_capture.add_face(grid_colors)
        cube_capture.print_captured_faces()

        print("\n--- Captured Face ---")
        for row in grid_colors:
            print(" ".join(row))

        face_string = reformat_face_state(grid_colors)
        print("Reformatted face:", face_string)

        if was_saved and cube_capture.is_complete():
            print("\n--- All 6 faces captured ---")
            cube_capture.print_color_counts()

            if cube_capture.validate_cube():
                print("Cube validation passed.")

                cube_string = reformat_cube_state(cube_capture.get_faces())
                print("\n--- Full Cube String ---")
                print(cube_string)

            else:
                print("Cube validation failed.")

    elif confirm == ord('q'):
        break
    
    cv2.imshow("Color Box Reader 3x3", frame)
    #cv2.imshow("ROI", roi) left out for now but can be used for debugging
    
    
cap.release()
cv2.destroyAllWindows()