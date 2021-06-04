import sys
import threading

import cv2
import numpy as np
# from numpy.lib.financial import _convert_when
import pydirectinput
from pyautogui._pyautogui_win import _size


def main():
    width, height = _size()
    currentStatus = 0
    penX = 0
    penY = 0
    keyboardParameters = [0, 0, 0, 0]
    result = 0

    def test(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(currentStatus)
            keyboardParameters[currentStatus] = 'mouseDown'

    load_from_disk = True
    if load_from_disk:
        penval = np.load('npy-files/red.npy')

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    kernel = np.ones((5, 5), np.uint8)

    # Initializing the canvas on which we will draw upon
    canvas = None
    canvas2 = None

    # Initilize x1,y1 points
    x1, y1 = 0, 0

    # Threshold for noise
    noiseth = 10

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
        mask = cv2.dilate(mask, kernel, iterations=3)

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

                rectBottomLeftCorner = (int(1280 * 1 / 4), int(720 * 1 / 4))
                rectTopRightCorner = (int(1280 * 3 / 4), int(720 * 3 / 4))
                canvas2 = cv2.rectangle(canvas2, rectBottomLeftCorner, rectTopRightCorner, (255, 0, 0), 2)

                penX = x2
                penY = y2

                if x2 > 640 + 640 / 2:
                    currentStatus = 3
                elif x2 < 640 - 640 / 2:
                    currentStatus = 1

                if y2 > 360 + 360 / 2:
                    currentStatus = 2
                elif y2 < 360 - 360 / 2:
                    currentStatus = 0


            # After the line is drawn the new points become the previous points.
            x1, y1 = x2, y2

        else:
            # If there were no contours detected then make x1,y1 = 0
            x1, y1 = 0, 0

        # Merge the canvas and the frame.
        canvas = cv2.add(canvas, canvas2)
        frame = cv2.add(frame, canvas)

        # OptionallpenY stack both frames and show it.
        stacked = np.hstack((canvas, frame))
        cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=0.6, fy=0.6))

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
        elif k != 255:
            print(k)
            # print("currentStatus: ", currentStatus)
            keyboardParameters[currentStatus] = k
        cv2.setMouseCallback('Trackbars', test)


    cv2.destroyAllWindows()
    cap.release()
    np.save('npy-files/keyboard', keyboardParameters)

main()