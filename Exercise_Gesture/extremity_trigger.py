import cv2


class ExtremityTrigger():
    def __init__(self, triggerName, pos):
        self.triggerName = triggerName
        self.status = 0
        self.backSub = cv2.createBackgroundSubtractorMOG2()
        self.pos = tuple(map(int, pos[1:-1].split(',')))
        self.flags = []
        self.isPressed = False

    def detect(self, frame):
        fgMask_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        for x in range(self.pos[0] - 30, self.pos[0] + 30):
            for y in range(self.pos[1] - 30, self.pos[1] + 30):
                if fgMask_bgr[y, x, 0] == 255:
                    self.status = 1
                    break
                else:
                    self.status = 0
        return self.status
