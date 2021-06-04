from tkinter import *
from tkinter import font
from PIL import Image
import pyautogui
import color_hsv_detection
import numpy as np
import cv2

class Configure(Frame):
    # General Helper Methods
    def underline(self, label):
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)

    def configure_colour(self, point_number):
        app = color_hsv_detection.ColorHSVDetection(point_number=point_number)
        app.main()
        if point_number == 1:
            self.point_1_colour = self.set_colour(np.load("npy-files/point_1.npy"))
            self.point_1_button.configure(bg=self.point_1_colour)
        elif point_number == 2:
            self.point_2_colour = self.set_colour(np.load("npy-files/point_2.npy"))
            self.point_2_button.configure(bg=self.point_2_colour)
        elif point_number == 3:
            self.point_3_colour = self.set_colour(np.load("npy-files/point_3.npy"))
            self.point_3_button.configure(bg=self.point_3_colour)
    
    def set_colour(self, point_colour):
        colour = np.uint8([[point_colour[0] * 0.7 + point_colour[1] * 0.3]])
        colour = cv2.cvtColor(colour, cv2.COLOR_HSV2RGB)[0][0]
        # https://stackoverflow.com/questions/3380726/converting-a-rgb-color-tuple-to-a-six-digit-code-in-python
        colour = '#%02x%02x%02x' % (int(colour[0]), int(colour[1]), int(colour[2]))
        return colour

    # Mode 1 - Helper Methods --------------------------------------------------------------------------------------------------------------
    def save_keyboard_mappings(self):
        self.keyboard_parameters[0] = ord(self.up_entry.get()) if ord(self.up_entry.get()) != '' else self.keyboard_parameters[0]
        self.keyboard_parameters[1] = ord(self.left_entry.get()) if ord(self.left_entry.get()) != '' else self.keyboard_parameters[1]
        self.keyboard_parameters[2] = ord(self.down_entry.get()) if ord(self.down_entry.get()) != '' else self.keyboard_parameters[2]
        self.keyboard_parameters[3] = ord(self.right_entry.get()) if ord(self.right_entry.get()) != '' else self.keyboard_parameters[3]
        np.save('npy-files/keyboard', self.keyboard_parameters)

    # X Concerned Helper Methods --------------------------------------------------------------------------------------------------------------
    def save_canvas_width_info(self, selection):
        # width is an array rather than a value so need to index into 0th to change the value
        self.canvas_info['width'][0] = selection if selection != '' else self.canvas_info['width'][0]
        self.width_scale.configure(to=selection)
        
        self.update_x_scale()

        np.savez('npy-files/canvas.npz', width=self.canvas_info['width'], height=self.canvas_info['height'])
        if int(self.width_scale.get()) > int(selection):
            self.width_scale.set(selection)
            self.save_rectangle_width_info(selection)

    def save_rectangle_width_info(self, selection):
        self.rect_info['width'][0] = selection if selection != '' else self.rect_info['width'][0]
        np.savez('npy-files/rectangle.npz', width=self.rect_info['width'], height=self.rect_info['height'], x=self.rect_info['x'] , y=self.rect_info['y'])

        self.canvas_info = dict(np.load("npy-files/canvas.npz"))
        self.update_x_scale()

    def update_x_scale(self):
        x_scale_max = str(int(self.canvas_info['width'][0]) - int(self.rect_info['width'][0]))
        self.x_scale.configure(to=x_scale_max)
        if int(self.x_scale.get()) > int(x_scale_max):
            self.x_scale.set(x_scale_max)
            self.save_rectangle_x_info(x_scale_max)
    
    def save_rectangle_x_info(self, selection):
        self.rect_info['x'][0] = selection if selection != '' else self.rect_info['x'][0]
        np.savez('npy-files/rectangle.npz', width=self.rect_info['width'], height=self.rect_info['height'], x=self.rect_info['x'] , y=self.rect_info['y'])


    # Y Concerned Helper Methods --------------------------------------------------------------------------------------------------------------
    def save_canvas_height_info(self, selection):
        self.canvas_info['height'][0] = selection if selection != '' else self.canvas_info['height'][0]
        self.height_scale.configure(to=selection)

        self.update_y_scale()

        np.savez('npy-files/canvas.npz', width=self.canvas_info['width'], height=self.canvas_info['height'])
        if int(self.height_scale.get()) > int(selection):
            self.height_scale.set(selection)
            self.save_rectangle_height_info(selection)

    def save_rectangle_height_info(self, selection):
        self.rect_info['height'][0] = selection if selection != '' else self.rect_info['height'][0]
        np.savez('npy-files/rectangle.npz', width=self.rect_info['width'], height=self.rect_info['height'], x=self.rect_info['x'] , y=self.rect_info['y'])

        self.canvas_info = dict(np.load("npy-files/canvas.npz"))
        self.update_y_scale()

    def update_y_scale(self):
        y_scale_max = str(int(self.canvas_info['height'][0]) - int(self.rect_info['height'][0]))
        self.y_scale.configure(to=y_scale_max)
        if int(self.y_scale.get()) > int(y_scale_max):
            self.y_scale.set(y_scale_max)
            self.save_rectangle_y_info(y_scale_max)

    def save_rectangle_y_info(self, selection):
        self.rect_info['y'][0] = selection if selection != '' else self.rect_info['y'][0]
        np.savez('npy-files/rectangle.npz', width=self.rect_info['width'], height=self.rect_info['height'], x=self.rect_info['x'] , y=self.rect_info['y'])

    # Mode 2 Helper Methods --------------------------------------------------------------------------------------------------------------
    def save_mouse_mapping(self, selection):
        self.mouse_mapping = [selection]
        np.save('npy-files/mouse', self.mouse_mapping)
    
    def save_radius(self, selection):
        self.radius = [selection]
        np.save('npy-files/radius', self.radius)



    # ---------------------------------------------------------------------- MAIN GUI SETUP CODE ----------------------------------------------------------------------
    def __init__(self, parent, controller):
        self.screen_width, self.screen_height = pyautogui.size()
        self.point_1_colour = self.set_colour(np.load("npy-files/point_1.npy"))
        self.point_2_colour = self.set_colour(np.load("npy-files/point_2.npy"))
        self.point_3_colour = self.set_colour(np.load("npy-files/point_3.npy"))
        try:
            self.canvas_info = dict(np.load("npy-files/canvas.npz"))
        except:
            canvas_width = np.array([0])
            canvas_height = np.array([0])
            np.savez("npy-files/canvas.npz", width=canvas_width, height=canvas_height)
            self.canvas_info = dict(np.load("npy-files/canvas.npz"))
        try:
            self.rect_info = dict(np.load("npy-files/rectangle.npz"))
        except:
            canvas_width = np.array([0])
            canvas_height = np.array([0])
            canvas_x = np.array([0])
            canvas_y = np.array([0])
            np.savez("npy-files/rectangle.npz", width=canvas_width, height=canvas_height, x=canvas_x, y=canvas_y)
            self.rect_info = dict(np.load("npy-files/rectangle.npz"))

        self.keyboard_parameters = np.load("npy-files/keyboard.npy")
        self.mouse_mapping = np.load("npy-files/mouse.npy")[0]
        self.radius = np.load("npy-files/radius.npy")[0]
        

        Frame.__init__(self, parent)
        self.controller = controller

        #  Opening Sentence
        go_back_button = Button(self, text="<-- save and go back", 
                            command=lambda: controller.show_frame("StartPage"))
        go_back_button.pack(side=TOP, anchor=NW)

        # Canvas Width + Height LABEL
        canvas_label = Label(self, text="Canvas Mappings")
        canvas_label.pack()
        self.underline(canvas_label)

        # Canvas Width + Height FRAME
        canvas_frame = Frame(self)
        canvas_frame.pack(side=TOP)

        # Canvas Width
        canvas_width_label = Label(self, text="Canvas width")
        canvas_width_label.pack(in_=canvas_frame, side=LEFT)
        
        self.canvas_width_scale = Scale(self, from_=0, to=self.screen_width, orient=HORIZONTAL, command=self.save_canvas_width_info)
        self.canvas_width_scale.set(self.canvas_info['width'][0]) if 'width' in self.canvas_info else 0
        self.canvas_width_scale.pack(in_=canvas_frame, side=LEFT)
        
        # Canvas Height
        canvas_height_label = Label(self, text="Canvas height")
        canvas_height_label.pack(in_=canvas_frame, side=LEFT)

        self.canvas_height_scale = Scale(self, from_=0, to=self.screen_height, orient=HORIZONTAL, command=self.save_canvas_height_info)
        self.canvas_height_scale.set(self.canvas_info['height'][0]) if 'height' in self.canvas_info else 0
        self.canvas_height_scale.pack(in_=canvas_frame, side=LEFT)


        # --------------------------------------------------------------------- MODE 1 STARTS ---------------------------------------------------------------------
        label = Label(self, text="Mode 1 - Virtual Rectangle", font=('Helvetica 15 bold'))
        label.pack(side=TOP, pady=(25,0))

        # Mode 1 Explanation
        mode_1_explanation_label = Label(self, text="Virtual Rectangle is a mode for subdividing your screen into quadrants for enabling hit-entry points", font=("Helvetica 12"))
        mode_1_explanation_label.pack(side=TOP, pady=(0,7))

        # Colour 1
        colour_1_frame = Frame(self)
        colour_1_frame.pack(side=TOP)
        point_1_label = Label(self, text="Point 1 (left hand index finger)")
        point_1_label.pack(in_=colour_1_frame, side=LEFT)
        
        self.point_1_button = Button(self, text="configure colour", command=lambda: self.configure_colour(1))
        self.point_1_button.configure(bg=self.point_1_colour)
        self.point_1_button.pack(in_=colour_1_frame, side=LEFT)

        # Press S to save instruction
        save_colour_1_label = Label(self, text="Press 's' key on the keyboard to save colour configuration", font=('Helvetica 10 bold'))
        save_colour_1_label.pack()

        # Keyboard Mappings
        keyboard_label = Label(self, text="Keyboard Mappings")
        keyboard_label.pack()
        self.underline(keyboard_label)

        # UP
        up_frame = Frame(self)
        up_frame.pack(side=TOP)
        up_label = Label(self, text="UP")
        up_label.pack(in_=up_frame, side=LEFT)
        
        self.up_entry = Entry(self)
        self.up_entry.insert(0, chr(self.keyboard_parameters[0]))
        self.up_entry.pack(in_=up_frame, side=LEFT)

        # LEFT
        left_frame = Frame(self)
        left_frame.pack(side=TOP)
        left_label = Label(self, text="LEFT")
        left_label.pack(in_=left_frame, side=LEFT)
        
        self.left_entry = Entry(self)
        self.left_entry.insert(0, chr(self.keyboard_parameters[1]))
        self.left_entry.pack(in_=left_frame, side=LEFT)

        # DOWN
        down_frame = Frame(self)
        down_frame.pack(side=TOP)
        down_label = Label(self, text="DOWN")
        down_label.pack(in_=down_frame, side=LEFT)
        
        self.down_entry = Entry(self)
        self.down_entry.insert(0, chr(self.keyboard_parameters[2]))
        self.down_entry.pack(in_=down_frame, side=LEFT)

        # RIGHT
        right_frame = Frame(self)
        right_frame.pack(side=TOP)
        right_label = Label(self, text="RIGHT")
        right_label.pack(in_=right_frame, side=LEFT)
        
        self.right_entry = Entry(self)
        self.right_entry.insert(0, chr(self.keyboard_parameters[3]))
        self.right_entry.pack(in_=right_frame, side=LEFT)

        # SAVE KEYBOARD MAPPINGS
        keyboard_save_button = Button(self, text="Save Keyboard Mappings", command=lambda: self.save_keyboard_mappings())
        keyboard_save_button.pack(pady=(5,10))

        # Rectangle Size + Position
        rectangle_label = Label(self, text="Rectangle Size and Position Adjustment")
        rectangle_label.pack()
        self.underline(rectangle_label)

        # WIDTH & HEIGHT
        width_and_height_frame = Frame(self)
        width_and_height_frame.pack(side=TOP)

        size_label = Label(self, text="Size: ")
        size_label.pack(in_=width_and_height_frame, side=LEFT)

        # WIDTH
        width_label = Label(self, text="width")
        width_label.pack(in_=width_and_height_frame, side=LEFT)
        
        # self.width_entry = Entry(self)
        # self.width_entry.insert(0, self.rect_info['width'][0])
        # self.width_entry.pack(in_=width_and_height_frame, side=LEFT)

        self.width_scale = Scale(self, from_=0, to=self.canvas_info['width'][0], orient=HORIZONTAL, command=self.save_rectangle_width_info)
        self.width_scale.set(self.rect_info['width'][0])
        self.width_scale.pack(in_=width_and_height_frame, side=LEFT)

        # HEIGHT
        height_label = Label(self, text="height")
        height_label.pack(in_=width_and_height_frame, side=LEFT)
        
        # self.height_entry = Entry(self)
        # self.height_entry.insert(0, self.rect_info['height'][0])
        # self.height_entry.pack(in_=width_and_height_frame, side=LEFT)

        self.height_scale = Scale(self, from_=0, to=self.canvas_info['height'][0], orient=HORIZONTAL, command=self.save_rectangle_height_info)
        self.height_scale.set(self.rect_info['height'][0])
        self.height_scale.pack(in_=width_and_height_frame, side=LEFT)

        # LEFT CORNER POSITION
        x_and_y_frame = Frame(self)
        x_and_y_frame.pack(side=TOP)

        rectangle_lower_left_corner_coordinates_label = Label(self, text="Rectangle Lower Left Corner Coordinates: ")
        rectangle_lower_left_corner_coordinates_label.pack(in_=x_and_y_frame, side=LEFT)

        # X
        x_label = Label(self, text="x")
        x_label.pack(in_=x_and_y_frame, side=LEFT)
        
        # self.x_entry = Entry(self)
        # self.x_entry.insert(0, self.rect_info['x'][0])
        # self.x_entry.pack(in_=x_and_y_frame, side=LEFT)

        self.x_scale = Scale(self, from_=0, to=str(int(self.canvas_info['width'][0]) - int(self.rect_info['width'][0])), orient=HORIZONTAL, command=self.save_rectangle_x_info)
        self.x_scale.set(self.rect_info['x'][0])
        self.x_scale.pack(in_=x_and_y_frame, side=LEFT)

        # Y
        y_label = Label(self, text="y")
        y_label.pack(in_=x_and_y_frame, side=LEFT)
        
        # self.y_entry = Entry(self)
        # self.y_entry.insert(0, self.rect_info['y'][0])
        # self.y_entry.pack(in_=x_and_y_frame, side=LEFT)

        self.y_scale = Scale(self, from_=0, to=str(int(self.rect_info['y'][0])), orient=HORIZONTAL, command=self.save_rectangle_y_info)
        self.y_scale.set(str(int(self.canvas_info['height'][0]) - int(self.rect_info['y'][0])))
        self.y_scale.pack(in_=x_and_y_frame, side=LEFT)

        # SAVE RECTANGLE INFO
        # rectangle_save_button = Button(self, text="Save Rectangle Info", command=self.save_rectangle_width_height_info)
        # rectangle_save_button.pack(pady=(5,10))
        # --------------------------------------------------------------------- MODE 1 ENDS ---------------------------------------------------------------------


        # --------------------------------------------------------------------- MODE 2 STARTS ---------------------------------------------------------------------
        mode_2_frame = Frame(self)
        mode_2_frame.pack(side=TOP)
        label = Label(self, text="Mode 2 - Virtual Circle", font=('Helvetica 15 bold'))
        label.pack(in_=mode_2_frame, side=TOP, pady=(25,0))

        # Mode 2 Explanation
        mode_2_explanation_label = Label(self, text="Virtual Circle is a mode for tracking a moving point like a cursor attached to a finger or moving \n object, and enabling clicks by entering the virtual circle with a set distance from its centre", font=('Helvetica 12'))
        mode_2_explanation_label.pack(in_=mode_2_frame, side=TOP, pady=(0,7))

        # Colour 2
        colour_2_frame = Frame(self)
        colour_2_frame.pack(side=TOP)
        point_2_label = Label(self, text="Point 2 (right hand index finger)")
        point_2_label.pack(in_=colour_2_frame, side=LEFT)
        
        self.point_2_button = Button(self, text="configure colour", command=lambda: self.configure_colour(2))
        self.point_2_button.configure(bg=self.point_2_colour)
        self.point_2_button.pack(in_=colour_2_frame, side=LEFT)

        # Press S to save instruction
        save_colour_2_label = Label(self, text="Press 's' key on the keyboard to save colour configuration", font=('Helvetica 10 bold'))
        save_colour_2_label.pack()

        # Colour 3
        colour_3_frame = Frame(self)
        colour_3_frame.pack(side=TOP)
        point_3_label = Label(self, text="Point 3 (right hand thumb)")
        point_3_label.pack(in_=colour_3_frame, side=LEFT)
        
        self.point_3_button = Button(self, text="configure colour", command=lambda: self.configure_colour(3))
        self.point_3_button.configure(bg=self.point_3_colour)
        self.point_3_button.pack(in_=colour_3_frame, side=LEFT)

        # Press S to save instruction
        save_colour_3_label = Label(self, text="Press 's' key on the keyboard to save colour configuration", font=('Helvetica 10 bold'))
        save_colour_3_label.pack()

        # Mouse Mapping
        mouse_mapping_frame = Frame(self)
        mouse_mapping_frame.pack(side=TOP)
        mouse_mapping_label = Label(self, text="Mouse Event Mapping")
        mouse_mapping_label.pack(in_=mouse_mapping_frame, side=LEFT)

        # Dropdown Menu
        options = [
            "Hold Mouse Down",
            "Click",
            "Double Click"
        ]

        option = StringVar()
        option.set(self.mouse_mapping)

        dropdown = OptionMenu(self, option, *options, command=self.save_mouse_mapping)
        dropdown.pack(in_=mouse_mapping_frame, side=LEFT)

        # Virtual Circle
        virtual_circle_label = Label(self, text="Virtual Circle radius adjustment")
        virtual_circle_label.pack()
        self.underline(virtual_circle_label)

        # Radius
        radius_frame = Frame(self)
        radius_frame.pack(side=TOP)
        radius_label = Label(self, text="Radius")
        radius_label.pack(in_=radius_frame, side=LEFT)

        radius_scale = Scale(self, from_=0, to=15, orient=HORIZONTAL, command=self.save_radius)
        radius_scale.set(self.radius)
        radius_scale.pack(in_=radius_frame, side=LEFT)
        # --------------------------------------------------------------------- MODE 2 ENDS ---------------------------------------------------------------------
