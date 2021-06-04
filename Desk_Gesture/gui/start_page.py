from tkinter import *

class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="MotionInput \n A webcam-based gesture recognition layer for DirectX", font=("Helvetica 15 bold"))
        label.pack(side="top", fill="x", pady=10)

        # Desk Gestures Module
        desk_label = Label(self, text="Desk Gestures Module", font=("Helvetica 12 bold"))
        desk_label.pack(side="top", fill="x", pady=(10,10))

        start_button = Button(self, text="Start",
                            command=lambda: controller.show_frame("ChooseModes"))
        start_button.pack()

        configure_button = Button(self, text="Configure",
                            command=lambda: controller.show_frame("Configure"))
        configure_button.pack()

        disclaimer_label_1 = Label(self, text="\nDisclaimer", font=("Helvetica 10 bold"))
        disclaimer_label_1.pack()

        disclaimer_label_2 = Label(self, text="No warranty is given and this should not be used in any live environments. \n This is not for end users and requires further development. It is a proof of concept prototype and should be treated as such. \n Exercises should not be done with this prototype and no liabilities are given. \n Use at your own risk!")
        disclaimer_label_2.pack()