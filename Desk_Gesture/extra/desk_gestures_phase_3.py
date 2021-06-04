import time
import sys
import subprocess
import threading

import cv2
import numpy as np
import pydirectinput
import pyautogui

width, height = pyautogui.size()
canvasWidth, canvasHeight = 640, 360
currentStatus = -1
x = 0
y = 0
keyboardParameters = np.load('npy-files/keyboard.npy')
stateChanged = False
# -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
currentStatus2 = -1
x3 = 0
y3 = 0
# -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
currentStatus3 = -1
x4 = 0
y4 = 0

print(keyboardParameters)


def farthest_point(defects, contour, centroid):
    if defects is not None and centroid is not None:
        s = defects[:, 0][:, 0]
        cx, cy = centroid

        x = np.array(contour[s][:, 0][:, 0], dtype=np.float)
        y = np.array(contour[s][:, 0][:, 1], dtype=np.float)

        xp = cv2.pow(cv2.subtract(x, cx), 2)
        yp = cv2.pow(cv2.subtract(y, cy), 2)
        dist = cv2.sqrt(cv2.add(xp, yp))

        dist_max_i = np.argmax(dist)

        if dist_max_i < len(s):
            farthest_defect = s[dist_max_i]
            farthest_point = tuple(contour[farthest_defect][0])
            return farthest_point
        else:
            return None


def isMouseClick(element):
    return element == 'mouseDown'


def changeState(state):
    stateChanged = not state


def movePlayer():
    if currentStatus != -1:
        if isMouseClick(keyboardParameters[currentStatus]):
            print("helloooooo")
            pydirectinput.mouseDown()
        else:
            pydirectinput.keyDown(chr(int(keyboardParameters[currentStatus])))
    else:
        for elem in keyboardParameters:
            if isMouseClick(elem):
                pydirectinput.mouseUp()
            else:
                pydirectinput.keyUp(chr(int(elem)))

    if currentStatus2 == 0:
        pydirectinput.mouseDown()
    elif currentStatus2 == 1:
        pydirectinput.click()
    elif currentStatus2 == 2:
        pydirectinput.doubleClick()
    elif currentStatus2 == 3:
        print(currentStatus2)
    else:
        pydirectinput.mouseUp()


def moveMouse():
    # print("hi?")
    pydirectinput.moveTo(round(width * (x3) / canvasWidth), round(height * y3 / canvasHeight))


def checkStatus():
    thread1 = threading.Timer(0.1, checkStatus)
    thread1.daemon = True
    thread1.start()
    thread2 = threading.Thread(target=movePlayer())
    thread2.daemon = True
    thread2.start()
    thread3 = threading.Thread(target=moveMouse())
    thread3.daemon = True
    thread3.start()


checkStatus()

load_from_disk = True
if load_from_disk:
    penval = np.load('npy-files/point_2.npy')
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    penval2 = np.load('npy-files/point_3.npy')
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    penval3 = np.load('npy-files/point_1.npy')

cap = cv2.VideoCapture(0)
cap.set(3, canvasWidth)
cap.set(4, canvasHeight)

kernel = np.ones((5, 5), np.uint8)

# Making window size adjustable
cv2.namedWindow('Trackbars', cv2.WINDOW_NORMAL)
# cv2.namedWindow('DeskGestures', cv2.WINDOW_NORMAL)

# Initializing the canvas on which we will draw upon
canvas = None
canvas2 = None
canvas3 = None

# Initilize x1,y1 points
x1, y1 = 0, 0
# -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
x12, y12, = 0, 0
# -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
prevX3, prevY3, = 0, 0

# Threshold for noise
noiseth = 10

# Threshold for wiper, the size of the contour must be bigger than for us to
# clear the canvas 
wiper_thresh = 40000

# A variable which tells when to clear canvas, if its True then we clear the canvas
clear = False


def centroid(max_contour):
    moment = cv2.moments(max_contour)
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
        return cx, cy
    else:
        return None


while (1):
    canvas3 = None

    _, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Initialize the canvas as a black image of the same size as the frame.
    if canvas is None:
        canvas = np.zeros_like(frame)
    if canvas2 is None:
        canvas2 = np.zeros_like(frame)
    if canvas3 is None:
        canvas3 = np.zeros_like(frame)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # If you're reading from memory then load the upper and lower ranges
    # from there
    if load_from_disk:

        lower_range = penval[0]
        upper_range = penval[1]
        # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
        lower_range2 = penval2[0]
        upper_range2 = penval2[1]
        # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
        lower_range3 = penval3[0]
        upper_range3 = penval3[1]

    # Otherwise define your own custom values for upper and lower range.
    else:
        lower_range = np.array([26, 80, 147])
        upper_range = np.array([81, 255, 255])

    mask = cv2.inRange(hsv, lower_range, upper_range)
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    mask2 = cv2.inRange(hsv, lower_range2, upper_range2)
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    mask3 = cv2.inRange(hsv, lower_range3, upper_range3)

    # Perform morphological operations to get rid of the noise
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=3)
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    mask2 = cv2.erode(mask2, kernel, iterations=1)
    mask2 = cv2.dilate(mask2, kernel, iterations=3)
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    mask3 = cv2.erode(mask3, kernel, iterations=1)
    mask3 = cv2.dilate(mask3, kernel, iterations=3)

    # Find Contours
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    contours2, hierarchy2 = cv2.findContours(
        mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    contours3, hierarchy3 = cv2.findContours(
        mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    """-----------------------------------------------------------------BIG CODE 1 (Green) START----------------------------------------------------------------------------------------"""
    # Make sure there is a contour present and also its size is bigger than
    # the noise threshold.
    if contours and cv2.contourArea(max(contours,
                                        key=cv2.contourArea)) > noiseth:

        c = max(contours, key=cv2.contourArea)
        # cnt_centroid = centroid(c)

        # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
        # hull = cv2.convexHull(c, returnPoints=False)
        # defects = cv2.convexityDefects(c, hull)
        # far_point = farthest_point(defects, c, cnt_centroid)
        # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------

        # x2, y2, w, h = cv2.boundingRect(c)
        # if (far_point != None):
        #     x2, y2 = far_point

        (x2, y2), r = cv2.minEnclosingCircle(c)
        x2 = int(x2)
        y2 = int(y2)

        # If there were no previous points then save the detected x2,y2
        # coordinates as x1,y1.
        # This is true when we writing for the first time or when writing
        # again when the pen had disappeared from view.
        if x1 == 0 and y1 == 0:
            x1, y1 = x2, y2

        else:
            # Draw the line on the canvas
            canvas = cv2.line(canvas, (x1, y1), (x2, y2), (0, 128, 0), 4)

            rectBottomLeftCorner = (int(canvasWidth * 1 / 4), int(canvasHeight * 1 / 4))
            rectTopRightCorner = (int(canvasWidth * 3 / 4), int(canvasHeight * 3 / 4))
            canvas2 = cv2.rectangle(canvas2, rectBottomLeftCorner, rectTopRightCorner, (255, 0, 0), 2)

            x = x2
            y = y2

            if x2 > canvasWidth * 3 / 4:
                currentStatus = 3
            elif x2 < canvasWidth * 1 / 4:
                currentStatus = 1
            else:
                currentStatus = -1

            if y2 > canvasHeight * 3 / 4:
                currentStatus = 2
            elif y2 < canvasHeight * 1 / 4:
                currentStatus = 0

        # After the line is drawn the new points become the previous points.
        x1, y1 = x2, y2

    else:
        # If there were no contours detected then make x1,y1 = 0
        x1, y1 = 0, 0
        x, y = 0, 0
    """-----------------------------------------------------------------BIG CODE 1 (Green) END-------------------------------------------------------------------------------------------"""

    """-----------------------------------------------------------------BIG CODE 3 (Raspberry Pink) START----------------------------------------------------------------------------------------"""
    if contours3 and cv2.contourArea(max(contours3,
                                         key=cv2.contourArea)) > noiseth:

        c = max(contours3, key=cv2.contourArea)
        (currX3, currY3), r3 = cv2.minEnclosingCircle(c)
        currX3 = int(currX3)
        currY3 = int(currY3)

        if prevX3 == 0 and prevY3 == 0:
            prevX3, prevY3 = currX3, currY3

        else:
            canvas = cv2.line(canvas, (prevX3, prevY3), (currX3, currY3), (147, 20, 255), 4)

            x4 = currX3
            y4 = currY3

        # After the line is drawn the new points become the previous points.
        prevX3, prevY3 = currX3, currY3

    else:
        # If there were no contours detected then make x1,y1 = 0
        prevX3, prevY3 = 0, 0
        x4, y4 = 0, 0
    """-----------------------------------------------------------------BIG CODE 3 (Raspberry Pink) END------------------------------------------------------------------------------------------"""

    """-----------------------------------------------------------------BIG CODE 2 (Yellow) START----------------------------------------------------------------------------------------"""
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    if contours2 and cv2.contourArea(max(contours2,
                                         key=cv2.contourArea)) > noiseth:

        c = max(contours2, key=cv2.contourArea)
        (x22, y22), r = cv2.minEnclosingCircle(c)
        x22 = int(x22)
        y22 = int(y22)
        # x22, y22, w, h = cv2.boundingRect(c)
        x3 = x22
        y3 = y22

        if x12 == 0 and y12 == 0:
            x12, y12 = x22, y22

        else:
            # Draw the line on the canvas
            # circleRadius = int((w**2 + h**2)**0.5 / 2) * 6
            circleRadius = int(r) * 6
            canvas = cv2.line(canvas, (x12, y12), (x22, y22), (0, 255, 255), 4)
            canvas3 = cv2.circle(canvas3, (x22, y22), circleRadius, (0, 255, 255), 2)

            # green sticker
            sticker1InCircle = (x - x22) ** 2 + (y - y22) ** 2 <= circleRadius ** 2
            # yellow sticker
            sticker2InCircle = (x4 - x22) ** 2 + (y4 - y22) ** 2 <= circleRadius ** 2

            if sticker1InCircle and not sticker2InCircle:
                currentStatus2 = 0
            elif not sticker1InCircle and sticker2InCircle:
                currentStatus2 = 1
            else:
                currentStatus2 = -1

            # if x22 > canvasWidth * 3 / 4:
            #     prevStatus2 = currentStatus2
            #     currentStatus2 = 3
            # elif x22 < canvasWidth * 1 / 4:
            #     prevStatus2 = currentStatus2
            #     currentStatus2 = 1
            # else:
            #     prevStatus2 = currentStatus2
            #     currentStatus2 = -1

            # if y22 > canvasHeight * 3 / 4:
            #     prevStatus2 = currentStatus2
            #     currentStatus2 = 2
            # elif y22 < canvasHeight * 1 / 4:
            #     prevStatus2 = currentStatus2
            #     currentStatus2 = 0

        # After the line is drawn the new points become the previous points.
        x12, y12 = x22, y22

    else:
        # If there were no contours detected then make x1,y1 = 0
        x12, y12 = 0, 0
    # -------------------------------------------------------------------TEST----------------------------------------------------------------------------------------------------
    """-----------------------------------------------------------------BIG CODE 2 (Yellow) END-------------------------------------------------------------------------------------------"""

    # Merge the canvas and the frame.
    canvas = cv2.add(canvas, canvas2)
    # frame = cv2.add(frame, canvas)
    frame = cv2.add(frame, canvas3)

    # 1st Sticker (green)
    mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    mask_3 = cv2.drawContours(mask_3, contours, -1, (0, 128, 0), 2)
    # 2nd Sticker (yellow)
    mask_4 = cv2.cvtColor(mask2, cv2.COLOR_GRAY2BGR)
    mask_4 = cv2.drawContours(mask_4, contours2, -1, (0, 255, 255), 1)
    # 3rd Sticker (red)
    mask_5 = cv2.cvtColor(mask3, cv2.COLOR_GRAY2BGR)
    mask_5 = cv2.drawContours(mask_5, contours3, -1, (147, 20, 255), 1)

    mask_3 = cv2.add(mask_3, mask_4)
    mask_3 = cv2.add(mask_3, mask_5)

    # Optionally stack both frames and show it.
    stacked = np.hstack((canvas, frame, mask_3))
    cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=0.6, fy=0.6))
    # cv2.imshow('Trackbars', cv2.resize(frame, None, fx=0.6, fy=0.6))
    # cv2.imshow('DeskGestures', frame)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

    # When c is pressed clear the canvas
    if k == ord('c'):
        canvas = None

    # Clear the canvas after 1 second if the clear variable is true
    if clear == True:
        time.sleep(1)
        canvas = None

        # And then set clear to false
        clear = False

cv2.destroyAllWindows()
cap.release()
sys.exit()
