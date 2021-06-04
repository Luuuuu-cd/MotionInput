from tkinter import *
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import app


class ChooseModes(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        #  Opening Sentence
        go_back_button = Button(self, text="<-- go back", 
                            command=lambda: controller.show_frame("StartPage"))
        go_back_button.pack(side=TOP, anchor=NW)
        label = Label(self, text="Choose Modes")
        label.pack(side=TOP, fill="x")

        # Dropdown Menu
        options = [
            "Mode 1",
            "Mode 2",
            "Both"
        ]

        option = StringVar()
        option.set(options[2])

        dropdown = OptionMenu(self, option, *options)
        dropdown.pack()

        # Next Button
        next_button = Button(self, text="Choose mode",
                            command=lambda: self.launch_mode(option.get()))
        next_button.pack()
        
        warning_label = Label(self, text="Press ESC key on keyboard to exit the program!", font=('Helvetica 8 bold'))
        warning_label_2 = Label(self, text="(closing the window will NOT end the program!)", font=('Helvetica 8 bold'))   
        warning_label.pack()
        warning_label_2.pack()

    def launch_mode(self, mode):
        mainApp = app.DeskGesturesModule(mode)
        mainApp.main()