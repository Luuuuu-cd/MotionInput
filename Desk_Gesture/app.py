import sys

import cv2
import numpy as np

import tracking_point
import circle
import wasd
import multithreading
import mode_1
import mode_2
import get_application_name

import time
import json

class DeskGesturesModule:
    def __init__(self, mode):
        # https://stackoverflow.com/questions/40219946/python-save-dictionaries-through-numpy-save
        self.rect_info = dict(np.load('npy-files/rectangle.npz'))
        self.canvas_info = dict(np.load('npy-files/canvas.npz'))
        self.data = {}
        self.data['applications used'] = []
        self.data['time between clicks'] = []

        self.canvas_width, self.canvas_height = int(self.canvas_info['width'][0]), int(self.canvas_info['height'][0])
        self.canvas = None
        self.rect_canvas = None
        self.circle_canvas = None
        self.contour_mask = None

        # Rectangle Info
        self.rect_x = int(self.rect_info['x'][0])
        self.rect_y = int(self.canvas_info['height']) - int(self.rect_info['y'][0])
        self.rect_width = int(self.rect_info['width'][0])
        self.rect_height = int(self.rect_info['height'][0])

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.canvas_width)
        self.cap.set(4, self.canvas_height)

        self.kernel = np.ones((5, 5), np.uint8)

        # Threshold for noise
        self.noiseth = 10

        self.mode = mode

    def activate_mode_1(self):
        self.point_1 = wasd.Wasd(point_number=1, erode=1, dilate=3, data=self.data)
    
        bottom_left = (self.rect_x, self.rect_y)
        top_right = (self.rect_x + self.rect_width, self.rect_y - self.rect_height)
        
        self.point_1.initialise_rect_coordinates(bottom_left, top_right)
        self.mode_wasd = mode_1.Mode1(self.point_1)
        self.threads_1 = multithreading.MultiThreading()
        self.threads_1.check_status(self.point_1, self.mode_wasd)

    def activate_mode_2(self):
        self.point_2 = tracking_point.TrackingPoint(point_number=2, erode=1, dilate=3, data=self.data)
        self.point_3 = circle.Circle(point_number=3, erode=1, dilate=3, data=self.data)
        self.point_3.initialise_points(self.point_2)
        self.point_3.initialise_has_run_once()
        self.point_3.initialise_radius()
        self.mode_mouse = mode_2.Mode2(self.point_3, self.canvas_width, self.canvas_height)
        self.threads_2 = multithreading.MultiThreading()
        self.threads_2.check_status(self.point_2, self.point_3, self.mode_mouse)

    def run_mode_1(self, hsv):
        self.point_1.run(self.canvas, hsv, self.kernel, self.noiseth, self.canvas_width, self.canvas_height)
    
    def contour_mode_1(self):
        self.contour_mask = cv2.add(self.point_1.contour_mask, self.point_1.contour_mask)

    def run_mode_2(self, hsv):
        self.point_2.run(self.canvas, hsv, self.kernel, self.noiseth, self.canvas_width, self.canvas_height)
        self.point_3.run(self.canvas, hsv, self.kernel, self.noiseth, self.canvas_width, self.canvas_height)

    def contour_mode_2(self):
        self.contour_mask = cv2.add(self.point_2.contour_mask, self.point_3.contour_mask)

    def contour_both(self):
        self.contour_mask = cv2.add(self.point_1.contour_mask, self.point_2.contour_mask)
        self.contour_mask = cv2.add(self.contour_mask, self.point_3.contour_mask)


    def main(self):
        start_time = time.time()
        if self.mode == "Mode 1":
            self.activate_mode_1()
        elif self.mode == "Mode 2":
            self.activate_mode_2()
        elif self.mode == "Both":
            self.activate_mode_1()
            self.activate_mode_2()

        while (1):
            application_name = get_application_name.get_application_name()
            if application_name != None and application_name not in self.data['applications used']:
                self.data['applications used'].append(application_name)

            self.circle_canvas = None

            _, frame = self.cap.read()
            frame = cv2.flip(frame, 1)

            if self.canvas is None:
                self.canvas = np.zeros_like(frame)

            if self.mode == "Mode 1" or self.mode == "Both":
                if self.rect_canvas is None:
                    self.rect_canvas = np.zeros_like(frame)
                
                self.point_1.initialise_rect_canvas(self.rect_canvas)

            if self.mode == "Mode 2" or self.mode == "Both":
                if self.circle_canvas is None:
                    self.circle_canvas = np.zeros_like(frame)
            
                self.point_3.initialise_circle_canvas(self.circle_canvas)

            # Convert BGR to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            if self.mode == "Mode 1":
                self.run_mode_1(hsv)
                self.contour_mode_1()
            elif self.mode == "Mode 2":
                self.run_mode_2(hsv)
                self.contour_mode_2()
            elif self.mode == "Both":
                self.run_mode_1(hsv)
                self.run_mode_2(hsv)
                self.contour_both()
            else:
                print("Unrecognized mode: error inside while loop")

            if self.mode == "Mode 1" or self.mode == "Both":
                frame = cv2.add(frame, self.rect_canvas)
            if self.mode == "Mode 2" or self.mode == "Both":
                frame = cv2.add(frame, self.circle_canvas)
            
            
            # FOR DEBUGGING - Optionally stack both frames and show it.
            # stacked = np.hstack((self.canvas, frame, self.contour_mask))
            # cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=1/3, fy=1/3))
            
            cv2.imshow('Desk Gestures Module [PRESS ESC TO END THE PROGRAM]', frame)

            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break

            # When c is pressed clear the canvas
            if k == ord('c'):
                self.canvas = None

        end_time = time.time()
        total_time = end_time - start_time
        # print(total_time)
        self.data['usage time'] = total_time 

        with open('json/data.json', 'w') as outfile:
            json.dump(self.data, outfile)

        cv2.destroyAllWindows()
        self.cap.release()
        sys.exit()

if __name__ == "__main__":
    # IF you want to run this script without GUI (Graphical User Interface, i.e., without running main.py) use code below (arguments for DeskGesturesModule are either "Mode 1", "Mode 2" or "Both")
    app = DeskGesturesModule("Both")
    app.main()