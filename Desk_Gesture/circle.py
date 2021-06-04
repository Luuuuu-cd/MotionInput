import cv2
import tracking_point
import time
import json
import numpy as np

class Circle(tracking_point.TrackingPoint):
    def initialise_radius(self):
        self.radius = np.load('npy-files/radius.npy')[0]
    
    def initialise_points(self, point_2):
        self.point_2 = point_2

    def initialise_circle_canvas(self, circle_canvas):
        self.circle_canvas = None
        self.circle_canvas = circle_canvas

    def initialise_has_run_once(self):
        self.has_run_once = True
        self.time_has_run_once = True

    def draw_point(self):
        circle_radius = int(self.r) * int(self.radius)
        self.canvas = cv2.line(self.canvas, (self.prev_x, self.prev_y), (self.x, self.y), self.colour, 4)
        self.circle_canvas = cv2.circle(self.circle_canvas, (self.x, self.y), circle_radius, self.colour, 2)

        # green inside yellow sticker
        sticker2InCircle = (self.point_2.x - self.x) ** 2 + (self.point_2.y - self.y) ** 2 <= circle_radius ** 2

        if sticker2InCircle:
            self.current_status = 0

            self.has_run_once = False

            if not self.time_has_run_once and self.startTime != 0:
                self.endTime = time.time()
                totalTime = self.endTime - self.startTime
                # print(totalTime)
                self.data['time between clicks'].append(
                    {
                        ('between click ' + str(self.data['number of clicks'] - 1) +  " and " + str((self.data['number of clicks']))): totalTime
                    }
                )
                self.time_has_run_once = True

        elif not sticker2InCircle:
            self.current_status = -1

            if not self.has_run_once:
                if 'number of clicks' not in self.data:
                    self.data['number of clicks'] = 1
                else:
                    self.data['number of clicks'] += 1
                self.startTime = time.time()
                self.has_run_once = True
                self.time_has_run_once = False

        # with open('json/data.json', 'w') as outfile:
        #     json.dump(self.data, outfile)