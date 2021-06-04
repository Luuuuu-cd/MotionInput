import cv2
import time
import os
import glob
from win32api import GetSystemMetrics


class RecordCustomizedMotion:
    def __init__(self, videoSource, motionType):
        self.videoSource = videoSource
        self.motionType = motionType
        self.path = "models/customized/" + self.motionType
        try:
            os.mkdir(self.path)
            os.mkdir(self.path + "/input")
            os.mkdir(self.path + "/input/0")
            os.mkdir(self.path + "/input/1")
            os.mkdir(self.path + "/outputs")
        except OSError:
            print("Creation of the directory %s failed" % self.path)
            return False
        else:
            print("Successfully created the directory %s " % self.path)

    def record(self, label):
        cap = cv2.VideoCapture(self.videoSource)
        count = 0
        backSub = cv2.createBackgroundSubtractorMOG2()

        TIMER = int(10)
        prev = time.time()
        winname = "Record"
        cv2.namedWindow(winname)
        cv2.resizeWindow(winname, 720, 480)
        cv2.moveWindow(winname, int(GetSystemMetrics(0) / 2 - 360), int(GetSystemMetrics(1) / 2 - 240))

        while TIMER >= 0:
            if cv2.getWindowProperty(winname, 1) == -1:
                files = glob.glob(self.path + '/*')
                for f in files:
                    os.remove(f)
                self.cap.release()
                cv2.destroyAllWindows()
                return False
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            img = cv2.resize(frame, (720, 480))
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, "Recording will start in " + str(TIMER) + " seconds",
                        (20, 40), font,
                        1, (0, 255, 255),
                        4, cv2.LINE_AA)
            cv2.waitKey(125)
            cv2.imshow(winname, img)
            cur = time.time()
            if cur - prev >= 1:
                prev = cur
                TIMER = TIMER - 1

        TIMER = int(10)

        prev = time.time()
        frameRate = 0.2
        while TIMER >= 0:
            if cv2.getWindowProperty(winname, 1) == -1:
                files = glob.glob(self.path + '/*')
                for f in files:
                    os.remove(f)
                self.cap.release()
                cv2.destroyAllWindows()
                return False
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            img = cv2.resize(frame, (720, 480))
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, "Recording now..." + str(TIMER),
                        (20, 40), font,
                        1, (0, 255, 255),
                        4, cv2.LINE_AA)

            cv2.waitKey(125)
            cv2.imshow(winname, img)
            cur = time.time()
            if cur - prev >= frameRate:
                fgMask = backSub.apply(frame)
                cv2.imwrite(self.path + "/input/" + str(label) + "/" + str(count) + ".jpg", fgMask)
                count += 1
            if cur - prev >= 1:
                prev = cur
                TIMER = TIMER - 1

        cap.release()
        cv2.destroyAllWindows()
        return True
