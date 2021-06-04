import pydirectinput
import pyautogui
import numpy as np


class Mode2:
    def __init__(self, point, canvas_width, canvas_height):
        self.width, self.height = pyautogui.size()
        self.mouse_mapping = np.load('npy-files/mouse.npy')[0]
        self.point = point
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.start_time = 0
        self.end_time = 0

    def move_mouse(self):
        mouseX = round(self.width * (self.point.x) / self.canvas_width)
        mouseY = round(self.height * self.point.y / self.canvas_height)
        pydirectinput.moveTo(mouseX, mouseY)

    def move_player(self):
        if self.point.current_status == 0:
            if self.mouse_mapping == "Hold Mouse Down":
                pydirectinput.mouseDown()
                # pydirectinput.keyDown('m')
            elif self.mouse_mapping == "Click":
                pydirectinput.click()
            elif self.mouse_mapping == "Double Click":
                pydirectinput.doubleClick()
            else:
                print(self.mouse_mapping, " is not recognized")
        else:
            pydirectinput.mouseUp()
        

