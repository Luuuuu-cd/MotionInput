class Mode3:
    def __init__(self, point):
        self.point = point

    def movePlayer(self):
        mouse.wheel(self.point.diff)