import tracking_point
import cv2

class Wasd(tracking_point.TrackingPoint):
    def initialise_rect_canvas(self, rect_canvas):
        self.rect_canvas = None
        self.rect_canvas = rect_canvas

    def initialise_rect_coordinates(self, bottom_left, top_right):
        self.bottom_left = bottom_left
        self.top_right = top_right

    def draw_point(self):
        # Draw the line on the canvas
        self.canvas = cv2.line(self.canvas, (self.prev_x, self.prev_y), (self.x, self.y), self.colour, 4)

        # rect_bottom_left_corner = (int(self.canvas_width * 1 / 4), int(self.canvas_height * 1 / 4))
        # rect_top_right_corner = (int(self.canvas_width * 3 / 4), int(self.canvas_height * 3 / 4))
        self.rect_canvas = cv2.rectangle(self.rect_canvas, self.bottom_left, self.top_right, self.colour, 2)


        # print(self.current_status)
        if self.x < self.bottom_left[0]:
            self.current_status = 1
        elif self.x > self.top_right[0]:
            self.current_status = 3
        else:
            self.current_status = -1

        if self.y > self.bottom_left[1]:
            self.current_status = 2
        elif self.y < self.top_right[1]:
            self.current_status = 0
