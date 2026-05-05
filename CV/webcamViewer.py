# 1. read frame
# 2. process input   ← (this is where waitKey + all key checks go)
# 3. process frame
# 4. display frame


import cv2

#init webcam
cap = cv2.VideoCapture(0)           # Creates a VideoCapture object and stores it in variable "cap". 
                                    # This object represents your connection to the webcam. 
                                    # The "0" means "use the default camera".

#check for fails
if not cap.isOpened(): #checks if webcam isn't successfully opened, active high
    print("Camera unavailable")
    exit()


mode = "normal"

while True: # Creates an infinite loop. Keeps webcam running, grabbing frame after frame. Like "main"

    # Step 1 - Read Frame
    ret,frame = cap.read()  # cap.read(): Attempts to grab a single frame (image) from the webcam.
                            # ret → True/False (whether the frame was successfully read)  - ret = return value
                            # frame → the actual image (as a NumPy array)

    if not ret: break       # If reading the frame failed (ret == False), exit the loop. Prevents errors like trying to display a non-existent frame.

    # Step 2 - Process Inputs                                    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('g'):     # grayscale
        mode = "gray"
    elif key == ord('e'):   # edge detection
        mode = "edges"
    elif key == ord('n'):   # normal
        mode = "normal"
    elif key == ord('q'):   # exit/quit
        break

    # Step 3 - Process Frame
    if mode == "gray":
        display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    elif mode == "edges":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        display_frame = cv2.Canny(gray, 100, 200)
        # 100 and 200 are thresholds — you can tweak these

    else:
        display_frame = frame

    
    # Step 4 - Dispay Frame
    cv2.imshow('Webcam feed', display_frame) #shows image within a window | Arguments: 'Webcam feed' → window title & frame → the image to display

#clean up
cap.release()                   # Frees the camera so other apps (or future runs) can use it. VERY important — otherwise the camera can stay "locked".
cv2.destroyAllWindows()         # Closes all OpenCV-created windows. Without this, windows may freeze or stay open after the program ends.