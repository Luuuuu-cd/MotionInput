import cv2
import numpy as np

class TrackingPoint:
    def __init__(self, point_number, erode, dilate, data):
        self.point_number = point_number
        self.x = 0
        self.y = 0
        self.prev_x = 0
        self.prev_y = 0
        self.x_diff = 0
        self.y_diff = 0
        self.current_status = 0
        self.penval = None
        self.lower_range = None
        self.upper_range = None
        self.contours = None
        self.hierarchy = None
        self.mask = None
        self.contour_mask = None
        self.erode = erode
        self.dilate = dilate
        self.start_time = 0
        self.end_time = 1
        self.data = data

    def initialise_canvas(self, canvas, canvas_width, canvas_height):
        self.canvas = canvas
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def get_penval(self):
        self.penval = np.load("npy-files/point_" + str(self.point_number) + '.npy')

    def set_colour(self):
        self.colour = np.uint8([[self.penval[0] * 0.7 + self.penval[1] * 0.3]])
        self.colour = cv2.cvtColor(self.colour, cv2.COLOR_HSV2RGB)[0][0]
        self.colour = int(self.colour[2]), int(self.colour[1]), int(self.colour[0])

    def load_colour_ranges(self):
        self.lower_range = self.penval[0]
        self.upper_range = self.penval[1]

    def set_mask(self, hsv, kernel):
        self.mask = cv2.inRange(hsv, self.lower_range, self.upper_range)
        self.mask = cv2.erode(self.mask, kernel, iterations=self.erode)
        self.mask = cv2.dilate(self.mask, kernel, iterations=self.dilate)

    def find_contours(self):
        self.contours, self.hierarchy = cv2.findContours(
            self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    def draw_contours(self):
        self.contour_mask = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)
        self.contour_mask = cv2.drawContours(self.contour_mask, self.contours, -1, self.colour, 2)

    def draw_point(self):
        # Draw the line on the canvas
        self.canvas = cv2.line(self.canvas, (self.prev_x, self.prev_y), (self.x, self.y), self.colour, 4)

    def calculate_coordinates(self, c):
        (self.x, self.y), r = cv2.minEnclosingCircle(c)
        self.x = int(self.x)
        self.y = int(self.y)
        self.r = int(r)

    def track_point(self, noiseth):
        if self.contours and cv2.contourArea(max(self.contours,
                                            key=cv2.contourArea)) > noiseth:

            c = max(self.contours, key=cv2.contourArea)

            self.calculate_coordinates(c)
            
            # If there were no previous points then save the detected x2,y2
            # coordinates as x1,y1.
            # This is true when we writing for the first time or when writing
            # again when the pen had disappeared from view.
            if self.prev_x == 0 and self.prev_y == 0:
                self.prev_x, self.prev_y = self.x, self.y
            else:
                self.draw_point()

            # After the line is drawn the new points become the previous points.
            self.y_diff = self.y - self.prev_y
            self.x_diff = self.x - self.prev_x
            self.prev_x, self.prev_y = self.x, self.y

        else:
            # If there were no contours detected then make self.prev_x,self.prev_y = 0
            self.prev_x, self.prev_y = 0, 0
            self.x, self.y = 0, 0

    def run(self, canvas, hsv, kernel, noiseth, canvas_width, canvas_height):
        self.initialise_canvas(canvas, canvas_width, canvas_height)
        self.get_penval()
        self.set_colour()
        self.load_colour_ranges()
        self.find_contours()
        self.set_mask(hsv, kernel)
        self.draw_contours()
        self.track_point(noiseth)

