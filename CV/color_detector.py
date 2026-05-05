import cv2
import numpy as np

cap = cv2.VideoCapture(0) 

if not cap.isOpened():
    print("Camera unavailable")
    exit()

# Color Range LUT
# note: red1 & red2 are needed bc red wraps around hsv color space 0->10 & 170->180
color_ranges = {
    "red1": (np.array([0, 120, 70]), np.array([10, 255, 255])),
    "red2": (np.array([170, 120, 70]), np.array([180, 255, 255])),
    "green": (np.array([35, 80, 50]), np.array([85, 255, 255])),
    "blue": (np.array([90, 80, 50]), np.array([130, 255, 255])),
    "yellow": (np.array([20, 100, 100]), np.array([35, 255, 255])),
    "orange": (np.array([10, 100, 100]), np.array([20, 255, 255])),
    "white": (np.array([0, 0, 180]), np.array([180, 70, 255]))
}

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
    #frame = cv2.flip(frame, 1) -> left out for now

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
    
    #draw box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)

    #print colors in 3x3 grid when p is pressed
    confirm = cv2.waitKey(1) & 0xFF #store key press
    if confirm == ord('p'): #only print to terminal when 'p' pressed
        print("\n--- Captured Face ---")
        for row in grid_colors:
            print(" ".join(row))

    
    cv2.imshow("Color Box Reader 3x3", frame)
    #cv2.imshow("ROI", roi) left out for now but can be used for debugging
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()