import sys
import threading

import cv2
import numpy as np
import pydirectinput
from pyautogui._pyautogui_win import _size

canvasWidth = 640
canvasHeight = 360
width, height = _size()
xStatus = 0
yStatus = 0
x = 0
y = 0


def movePlayer():
    pydirectinput.moveTo(round(width * x / canvasWidth), round(height * y / canvasHeight))
    


def checkStatus():
    thread1 = threading.Timer(0.1, checkStatus)
    thread1.daemon = True
    thread1.start()
    thread2 = threading.Thread(target=movePlayer())
    thread2.daemon = True
    thread2.start()


checkStatus()

load_from_disk = True
if load_from_disk:
    penval = np.load('penval.npy')

cap = cv2.VideoCapture(0)
cap.set(3, canvasWidth)
cap.set(4, canvasHeight)

kernel = np.ones((5, 5), np.uint8)

# Initializing the canvas on which we will draw upon
canvas = None
canvas2 = None

# Initilize x1,y1 points
x1, y1 = 0, 0

# Threshold for noise
noiseth = 800

while (1):
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Initialize the canvas as a black image of the same size as the frame.
    if canvas is None:
        canvas = np.zeros_like(frame)
    if canvas2 is None:
        canvas2 = np.zeros_like(frame)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # If you're reading from memory then load the upper and lower ranges
    # from there
    if load_from_disk:
        lower_range = penval[0]
        upper_range = penval[1]

    # Otherwise define your own custom values for upper and lower range.
    else:
        lower_range = np.array([26, 80, 147])
        upper_range = np.array([81, 255, 255])

    mask = cv2.inRange(hsv, lower_range, upper_range)

    # Perform morphological operations to get rid of the noise
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Find Contours
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Make sure there is a contour present and also its size is bigger than
    # the noise threshold.
    if contours and cv2.contourArea(max(contours,
                                        key=cv2.contourArea)) > noiseth:

        c = max(contours, key=cv2.contourArea)
        x2, y2, w, h = cv2.boundingRect(c)

        # If there were no previous points then save the detected x2,y2
        # coordinates as x1,y1.
        # This is true when we writing for the first time or when writing
        # again when the pen had disappeared from view.
        if x1 == 0 and y1 == 0:
            x1, y1 = x2, y2

        else:
            # Draw the line on the canvas
            canvas = cv2.line(canvas, (x1, y1), (x2, y2), [255, 0, 0], 4)

            rectBottomLeftCorner = (int(canvasWidth * 1 / 4), int(canvasHeight * 1 / 4))
            rectTopRightCorner = (int(canvasWidth * 3 / 4), int(canvasHeight * 3 / 4))
            canvas2 = cv2.rectangle(canvas2, rectBottomLeftCorner, rectTopRightCorner, (255, 0, 0), 2)

            x = x2
            y = y2

            # print(x2, "\t", y2)

            if x2 > canvasWidth * 1/4:
                xStatus = 2
            elif x2 < canvasWidth * 3/4:
                xStatus = 1
            else:
                xStatus = 0

            if y2 > canvasHeight * 1 / 4:
                yStatus = 1
            elif y2 < canvasHeight * 3 / 4:
                yStatus = 2
            else:
                yStatus = 0

        # After the line is drawn the new points become the previous points.
        x1, y1 = x2, y2

    else:
        # If there were no contours detected then make x1,y1 = 0
        x1, y1 = 0, 0

    # Merge the canvas and the frame.
    canvas = cv2.add(canvas, canvas2)
    frame = cv2.add(frame, canvas)

    # Optionally stack both frames and show it.
    stacked = np.hstack((canvas, frame))
    cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=0.6, fy=0.6))

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

    # When c is pressed clear the canvas
    if k == ord('c'):
        canvas = None

cv2.destroyAllWindows()
cap.release()
sys.exit()