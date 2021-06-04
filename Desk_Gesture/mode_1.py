import numpy as np
import pydirectinput

class Mode1:
    def __init__(self, point):
        self.point = point
        self.keyboard_parameters = np.load("npy-files/keyboard.npy")
        # print(self.keyboard_parameters)

    def move_player(self):
        if self.point.current_status != -1:
            key = chr(int(self.keyboard_parameters[self.point.current_status]))
            pydirectinput.keyDown(key)
        else:
            for elem in self.keyboard_parameters:
                pydirectinput.keyUp(chr(int(elem)))
