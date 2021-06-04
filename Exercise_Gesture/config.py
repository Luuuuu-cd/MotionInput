import cv2
import time
from configparser import ConfigParser
from win32api import GetSystemMetrics


def takePhoto(video_source):
    isPhotoTaken = False

    TIMER = int(3)

    winname = "Config"
    cv2.namedWindow(winname)
    cv2.resizeWindow(winname, 720, 480)
    cv2.moveWindow(winname, int(GetSystemMetrics(0) / 2 - 360), int(GetSystemMetrics(1) / 2 - 240))

    cap = cv2.VideoCapture(video_source)

    prev = time.time()

    while TIMER >= 0:
        if cv2.getWindowProperty(winname, 1) == -1:
            cap.release()
            cv2.destroyAllWindows()
            return isPhotoTaken
        ret, img = cap.read()
        img = cv2.resize(img, (720, 480))

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(TIMER),
                    (300, 200), font,
                    7, (0, 255, 255),
                    4, cv2.LINE_AA)
        cv2.imshow(winname, img)
        cv2.waitKey(125)

        cur = time.time()

        if cur - prev >= 1:
            prev = cur
            TIMER = TIMER - 1

    ret, img = cap.read()
    img = cv2.resize(img, (720, 480))

    cv2.imshow(winname, img)

    cv2.waitKey(2000)

    cv2.imwrite("imgs/config.jpg", img)
    cap.release()
    cv2.destroyAllWindows()
    isPhotoTaken = True
    return isPhotoTaken

def selectROI():
    config = ConfigParser()

    config.read('config.ini')
    if not config.has_section('roi'):
        config.add_section('roi')

    winname = "SelectROI"
    cv2.namedWindow(winname)
    cv2.resizeWindow(winname, 720, 480)
    cv2.moveWindow(winname, int(GetSystemMetrics(0) / 2 - 360), int(GetSystemMetrics(1) / 2 - 240))

    im = cv2.imread("imgs/config.jpg")

    roiMotion = cv2.selectROI(winname, im)

    config.set('roi', 'region', str(roiMotion))
    with open('config.ini', 'w') as f:
        config.write(f)

    cv2.destroyAllWindows()
