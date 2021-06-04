import tracking_point
import cv2

import mouse

class Scroll(tracking_point.TrackingPoint):
    def initialisePoint(self, point1):
        self.point1 = point1

    def initialiseDistance(self):
        self.distance = None
        self.prevDistance = None
        self.diff = 0

    def drawPoint(self):
        xDiff = abs(self.point1.x - self.x)
        yDiff = abs(self.point1.y - self.y)
        if self.distance == None:
            self.prevDistance = (xDiff**2 + yDiff**2)**0.5
        else:
            self.prevDistance = self.distance

        self.distance = (xDiff**2 + yDiff**2)**0.5
        self.diff = self.distance - self.prevDistance
        print(xDiff, "\t", yDiff, "\t", self.diff)
