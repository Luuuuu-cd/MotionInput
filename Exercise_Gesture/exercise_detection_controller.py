import cv2
import pydirectinput
import threading
import json
import default_exercise_detection
import customized_exercise_detection
import extremity_trigger
import screen_brightness_control as sbc
from datetime import datetime
from configparser import ConfigParser


def most_frequent(List):
    return max(set(List), key=List.count)


class ExerciseDetectionController:
    def __init__(self, videoSource):
        self.backSub = cv2.createBackgroundSubtractorMOG2()
        self.initialBrightness = sbc.get_brightness()
        self.isDetecting = False
        self.status = 0
        if videoSource == "debug":
            self.videoSource = -1
        else:
            self.videoSource = int(videoSource[-1])
        self.cap = cv2.VideoCapture(self.videoSource, cv2.CAP_DSHOW)
        if self.cap.isOpened() == False:
            print('Error while trying to open camera.')
        self.ret, self.frame1 = self.cap.read()
        self.ret, self.frame2 = self.cap.read()
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.motionDetected = []
        self.isMoving = False

        self.config = ConfigParser()
        self.config.read('config.ini')
        self.inputs = ConfigParser()
        self.inputs.read('current_inputs.ini')

        self.defaultExercisesDict = dict(self.config.items('default'))
        self.customizedExerciseDict = dict(self.config.items('customized'))
        self.extremityTriggersDict = dict(self.config.items('extremity'))

        # self.timerFlag=0
        # self.t0=0
        # self.t1=1

        currentDefaultInputsDict = dict(self.inputs.items('default'))
        currentCustomizedInputsDict = dict(self.inputs.items('customized'))
        extremityTriggerInputsDict = dict(self.inputs.items('extremity'))

        for key in currentDefaultInputsDict:
            if (int(currentDefaultInputsDict.get(key))) == 0:
                self.defaultExercisesDict.pop(key, None)

        for key in currentCustomizedInputsDict:
            if (int(currentCustomizedInputsDict.get(key))) == 0:
                self.customizedExerciseDict.pop(key, None)

        for key in extremityTriggerInputsDict:
            if (int(extremityTriggerInputsDict.get(key))) == 0:
                self.extremityTriggersDict.pop(key, None)

        self.currentDetectors = {}
        for key in self.defaultExercisesDict:
            eventType = self.defaultExercisesDict.get(key).split('+')[0]
            if len(self.defaultExercisesDict.get(key).split('+')) == 2:
                eventContent = self.defaultExercisesDict.get(key).split('+')[1]
            else:
                eventContent = None
            detector = default_exercise_detection.DefaultExerciseDetection(key)
            self.currentDetectors[detector] = (eventType, eventContent)

        for key in self.customizedExerciseDict:
            eventType = self.customizedExerciseDict.get(key).split('+')[0]
            if len(self.customizedExerciseDict.get(key).split('+')) == 2:
                eventContent = self.customizedExerciseDict.get(key).split('+')[1]
            else:
                eventContent = None
            detector = customized_exercise_detection.CustomizedExerciseDetection(key)
            self.currentDetectors[detector] = (eventType, eventContent)

        for key in self.extremityTriggersDict:
            pos = self.extremityTriggersDict.get(key).split('+')[0]
            eventType = self.extremityTriggersDict.get(key).split('+')[1]
            if len(self.extremityTriggersDict.get(key).split('+')) == 3:
                eventContent = self.extremityTriggersDict.get(key).split('+')[2]
            else:
                eventContent = None
            detector = extremity_trigger.ExtremityTrigger(key, pos)
            self.currentDetectors[detector] = (pos, eventType, eventContent)

        self.exercisesRecords = dict(self.defaultExercisesDict, **self.customizedExerciseDict)
        for key in self.exercisesRecords:
            self.exercisesRecords[key] = 0

        self.extremityRecords = self.extremityTriggersDict
        for key in self.extremityTriggersDict:
            self.extremityRecords[key] = (self.extremityTriggersDict.get(key).split('+')[0], 0)

        self.records = (self.exercisesRecords, self.extremityRecords)

        self.check_status()

    def __del__(self):
        if (self.isDetecting):
            self.statusThread.cancel()
            self.isDetecting = False
            self.status = 0
            sbc.set_brightness(self.initialBrightness)
            if self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
            for key in self.records[0]:
                self.records[0][key] = str(format(self.records[0][key], '.2f')) + ' seconds'
            for key in self.records[1]:
                self.records[1][key] = (
                    self.records[1][key][0], str(format(self.records[1][key][1], '.2f')) + ' seconds')
            recordName = datetime.now().strftime("%Y-%m-%d_self%H-%M")
            with open('usage_records/' + recordName + '.json', 'w') as f:
                json.dump(self.records, f)

    def get_config_settings(self):
        config = ConfigParser()
        config.read('config.ini')
        if config.has_section('roi'):
            self.roiMotion = list(config.get('roi', 'region')[1:-1].split(","))
            self.roiMotion = [int(i) for i in self.roiMotion]
            return True
        else:
            return False

    def check_status(self):
        self.statusThread = threading.Timer(0.2, self.check_status)
        self.statusThread.start()
        for key in self.currentDetectors:
            if isinstance(key, extremity_trigger.ExtremityTrigger):
                eventType = self.currentDetectors.get(key)[1]
                eventContent = self.currentDetectors.get(key)[2]
                if key.status == 1:
                    self.records[1][key.triggerName] = (key.pos, self.records[1][key.triggerName][1] + 0.2)
                    if eventType == "keypress":
                        pydirectinput.keyDown(eventContent)
                        key.isPressed = True
                    elif eventType == "mouse":
                        if eventContent == "click":
                            pydirectinput.click()
                        elif eventContent == "move-left":
                            pydirectinput.move(-1, None)
                        elif eventContent == "move-right":
                            pydirectinput.move(1, None)
                        elif eventContent == "move-up":
                            pydirectinput.move(None, -1)
                        elif eventContent == "move-down":
                            pydirectinput.move(None, 1)
                    elif eventType == "brightness":
                        sbc.set_brightness(100)
                elif key.status == 0 and key.isPressed == True:
                    if eventType == "keypress":
                        pydirectinput.keyUp(eventContent)
                        key.isPressed = False
                else:
                    if eventType == "brightness":
                        sbc.set_brightness(-25)
            else:
                eventType = self.currentDetectors.get(key)[0]
                eventContent = self.currentDetectors.get(key)[1]
                if key.status == 1 and self.isMoving:
                    self.records[0][key.motionType] = self.records[0][key.motionType] + 0.2
                    if eventType == "keypress":
                        pydirectinput.keyDown(eventContent)
                        key.isPressed = True
                        # self.t0 = round(time()*1000)
                        # self.testingLog.write("KeyPressed:"+str(self.t0) + "\n")
                    elif eventType == "mouse":
                        if eventContent == "click":
                            pydirectinput.click()
                        elif eventContent == "move-left":
                            pydirectinput.move(-1, None)
                        elif eventContent == "move-right":
                            pydirectinput.move(1, None)
                        elif eventContent == "move-up":
                            pydirectinput.move(None, -1)
                        elif eventContent == "move-down":
                            pydirectinput.move(None, 1)
                    elif eventType == "brightness":
                        sbc.set_brightness(100)
                elif (not self.isMoving or key.status == 0) and key.isPressed == True:
                    # self.t0=round(time()*1000)
                    # self.testingLog.write("KeyReleased:" + str(self.t0) + "\n")
                    if eventType == "keypress":
                        pydirectinput.keyUp(eventContent)
                        key.isPressed = False
                else:
                    if eventType == "brightness":
                        sbc.set_brightness(-25)

    def get_frame(self):
        if self.cap.isOpened():
            if self.isDetecting:
                # if(self.timerFlag==0):
                # self.testingLog = open('testing.txt', 'w')
                # self.timerFlag=1
                # self.t0=round(time()*1000)
                frame1 = cv2.resize(self.frame1, (720, 480))
                frame2 = cv2.resize(self.frame2, (720, 480))
                frame1 = cv2.flip(frame1, 1)
                frame2 = cv2.flip(frame2, 1)

                croppedMotion1 = frame1[self.roiMotion[1]:self.roiMotion[1] + self.roiMotion[3],
                                 self.roiMotion[0]:self.roiMotion[0] + self.roiMotion[2]]
                croppedMotion2 = frame2[self.roiMotion[1]:self.roiMotion[1] + self.roiMotion[3],
                                 self.roiMotion[0]:self.roiMotion[0] + self.roiMotion[2]]

                diff = cv2.absdiff(croppedMotion1, croppedMotion2)
                gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                _, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
                dilated = cv2.dilate(thresh, None, iterations=3)
                contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]

                if len(contours) != 0:
                    contour = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(contour)
                    if area > 500:
                        (x, y, w, h) = cv2.boundingRect(contour)
                        cv2.rectangle(frame1, (self.roiMotion[0] + x, self.roiMotion[1] + y),
                                      (self.roiMotion[0] + x + w, self.roiMotion[1] + y + h), (0, 255, 0), 2)
                        self.motionDetected.append(1)
                    else:
                        self.motionDetected.append(0)
                else:
                    self.motionDetected.append(0)

                if len(self.motionDetected) == 6:
                    if most_frequent(self.motionDetected) == 1:
                        self.isMoving = True
                    else:
                        self.isMoving = False
                    self.motionDetected.pop(0)

                image = croppedMotion1.copy()

                for key in self.currentDetectors:
                    if isinstance(key, customized_exercise_detection.CustomizedExerciseDetection):
                        image = self.backSub.apply(image)
                        key.detect(image)
                    elif isinstance(key, extremity_trigger.ExtremityTrigger):
                        pos = self.currentDetectors.get(key)[0]
                        pos = tuple(map(int, pos[1:-1].split(',')))
                        if key.status == 1:
                            cv2.circle(frame1, (pos), 30, (0, 255, 0), -1)
                        else:
                            cv2.circle(frame1, (pos), 30, (0, 0, 255), -1)
                        blur = cv2.GaussianBlur(image, (7, 7), 0)
                        fgMask = self.backSub.apply(blur)
                        key.detect(fgMask)
                    else:
                        key.detect(image)

                cv2.rectangle(frame1, (self.roiMotion[0], self.roiMotion[1]),
                              (self.roiMotion[0] + self.roiMotion[2], self.roiMotion[1] + self.roiMotion[3]),
                              (255, 0, 0), 4)
                frame1 = cv2.resize(frame1, (720, 480))

                self.frame1 = self.frame2
                self.ret, self.frame2 = self.cap.read()
                return self.status, self.ret, cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)

            else:
                image = self.frame1.copy()
                image = cv2.resize(image, (720, 480))
                image = cv2.flip(image, 1)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.frame1 = self.frame2
                self.ret, self.frame2 = self.cap.read()
                return 0, self.ret, image
