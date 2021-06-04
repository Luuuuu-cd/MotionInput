import exercise_detection_controller
import PIL.Image, PIL.ImageTk
import config
import sys
import record_customized_motion
import train_customized_model
import shutil
import os
from configparser import ConfigParser
from time import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox


class ExerciseGesture:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.keypress = 'w'
        self.window.wm_iconbitmap('imgs/logo.ico')
        self.appStatus = 0
        self.window.protocol("WM_DELETE_WINDOW", self.exit)
        self.motionDetection = None
        self.start_btn_img = PhotoImage(file='imgs/play.png')
        self.stop_btn_img = PhotoImage(file='imgs/stop.png')

        # Create a canvas that can fit the above video source size
        self.canvas = Canvas(window, width=720, height=480)
        self.canvas.pack()

        # Create Player Control Frames
        self.controls_frame = Frame(self.window)
        self.controls_frame.pack(fill=X, side=BOTTOM)

        # Create Player Control Buttons
        self.start_button = Button(self.controls_frame, image=self.start_btn_img, borderwidth=0, command=self.start)
        self.start_button.pack(padx=3, side='left')
        self.stop_button = Button(self.controls_frame, image=self.stop_btn_img, borderwidth=0, command=self.stop)
        self.stop_button.pack(padx=3, side='left')

        # self.test_button = Button(self.controls_frame, text='test', borderwidth=0, command=self.current_time)
        # self.test_button.pack(padx=8, side='left')

        self.instructionLabel1 = Label(text='Press start button to start, press stop button to end the session and save'
                                            ' the data.\nGo to Settings - Profile to change the current inputs.',
                                       font=("Courier", 10))
        self.instructionLabel1.config(anchor=CENTER)
        self.instructionLabel1.pack()
        self.customizedOptions = next(os.walk("models/customized"))[1]

        self.cameraOptions = ["Camera 0", "Camera 1", "Camera 2", "debug"]
        self.cameraOption = StringVar()
        self.cameraOption.set(self.cameraOptions[0])
        self.cameraOption.trace("w", self.camera_changed)
        self.cameraOptionMenu = OptionMenu(self.controls_frame, self.cameraOption,
                                           *self.cameraOptions)
        self.cameraOptionMenu.config(width=10)
        self.cameraOptionMenu.pack(padx=3, side='right')

        # Create Menu
        self.my_menu = Menu(self.window)
        self.window.config(menu=self.my_menu)

        # Add Menu
        self.settings_menu = Menu(self.my_menu)
        self.my_menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Profile", command=self.profile_window)

        self.window.resizable(False, False)
        self.delay = 15
        self.update()
        self.window.mainloop()

    def update(self):
        if (self.appStatus == 1 or self.appStatus == 2):
            try:
                status, ret, frame = self.motionDetection.get_frame()
                if ret:
                    self.photo = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
            except:
                print("Error while trying to get frames.")
                self.stop()

            self.window.after(self.delay, self.update)

        elif (self.appStatus == 0):

            image = PIL.Image.open('imgs/no_camera_big.png')
            self.photo = PIL.ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
            self.window.after(self.delay, self.update)

    def keyboard_map(self, event):
        event.widget['text'] = "???"
        event.widget['background'] = "green"
        event.widget.focus_set()
        event.widget.bind("<Key>", self.keyboard_map_completed)

    def keyboard_map_completed(self, event):
        keypress = event.keysym
        event.widget['text'] = keypress
        event.widget['background'] = 'light grey'

    def profile_window(self):
        self.eventTypes = ["keypress", "mouse", "brightness"]
        self.mouseEvents = ["click", "move-left", "move-right", "move-up", "move-down"]

        if (self.appStatus != 0):
            self.stop()
        self.profileWindow = Toplevel(self.window)
        self.profileWindow.geometry('+100+100')
        self.profileWindow.resizable(False, False)
        profileSettingsFrame = Frame(self.profileWindow)
        profileSettingsFrame.pack(fill=X, side=BOTTOM)

        self.profileNotebook = ttk.Notebook(profileSettingsFrame)
        self.profileNotebook.pack(pady=15)

        self.profileExerciseFrame = Frame(self.profileNotebook, width=500, height=1000)
        self.profileExtremityFrame = Frame(self.profileNotebook, width=500, height=1000)

        self.profileExerciseFrame.pack(fill="both", expand=1)
        self.profileExtremityFrame.pack(fill="both", expand=1)

        self.defaultProfiles = []
        self.customizedProfiles = []
        self.extremityProfiles = []
        config = ConfigParser()
        config.read('config.ini')
        currentInputs = ConfigParser()
        currentInputs.read('current_inputs.ini')
        defaultExercisesDict = dict(config.items('default'))
        currentDefaultInputsDict = dict(currentInputs.items('default'))
        customizedExerciseDict = dict(config.items('customized'))
        currentCustomizedInputsDict = dict(currentInputs.items('customized'))
        extremityTriggersDict = dict(config.items('extremity'))
        extremityTriggerInputsDict = dict(currentInputs.items('extremity'))

        rowCount = 0
        defaultLabel = Label(self.profileExerciseFrame, text="DEFAULT", font=('Helvetica', 18, 'bold'))
        defaultLabel.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1
        for key in defaultExercisesDict:
            checkBoxVar = IntVar()
            if (int(currentDefaultInputsDict.get(key))) == 1:
                checkBoxVar.set(1)
            else:
                checkBoxVar.set(0)
            checkBox = Checkbutton(self.profileExerciseFrame, text=key, variable=checkBoxVar)
            checkBox.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
            if ('+' in defaultExercisesDict.get(key)):
                eventType = defaultExercisesDict.get(key).split('+')[0]
                eventContent = defaultExercisesDict.get(key).split('+')[1]
            else:
                eventType = defaultExercisesDict.get(key)
                eventContent = None

            eventTypeOption = StringVar()
            eventTypeOption.set(eventType)
            eventTypeOption.trace("w", lambda *args, row=rowCount,
                                              eventTypeOptionInstance=eventTypeOption: self.default_event_type_changed(
                eventTypeOptionInstance, row, *args))

            eventTypeOptionMenu = OptionMenu(self.profileExerciseFrame, eventTypeOption,
                                             *self.eventTypes)
            eventTypeOptionMenu.config(width=18)
            eventTypeOptionMenu.grid(row=rowCount, column=1, pady=5, padx=0)

            if eventType == "keypress":
                keyLabel = Label(self.profileExerciseFrame, text=eventContent, background='light grey')
                keyLabel.grid(sticky="W", row=rowCount, column=2, pady=5, padx=5)
                keyLabel.bind("<Button-1>", self.key_map)
                self.defaultProfiles.append((checkBoxVar, checkBox, eventTypeOption, keyLabel))

            elif eventType == "mouse":
                mouseEventOption = StringVar()
                mouseEventOption.set(eventContent)
                mouseEventTypeOptionMenu = OptionMenu(self.profileExerciseFrame, mouseEventOption,
                                                      *self.mouseEvents)
                mouseEventTypeOptionMenu.config(width=18)
                mouseEventTypeOptionMenu.grid(row=rowCount, column=2, pady=5, padx=0)
                self.defaultProfiles.append((checkBoxVar, checkBox, eventTypeOption, mouseEventOption))
            elif eventType == "brightness":
                self.defaultProfiles.append((checkBoxVar, checkBox, eventTypeOption))
            rowCount += 1

        customizedLabel = Label(self.profileExerciseFrame, text="CUSTOMIZED", font=('Helvetica', 18, 'bold'))
        customizedLabel.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1

        for key in customizedExerciseDict:
            checkBoxVar = IntVar()
            if (int(currentCustomizedInputsDict.get(key))) == 1:
                checkBoxVar.set(1)
            else:
                checkBoxVar.set(0)
            checkBox = Checkbutton(self.profileExerciseFrame, text=key, variable=checkBoxVar)
            checkBox.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)

            if ('+' in customizedExerciseDict.get(key)):
                eventType = customizedExerciseDict.get(key).split('+')[0]
                eventContent = customizedExerciseDict.get(key).split('+')[1]
            else:
                eventType = customizedExerciseDict.get(key)
                eventContent = ''

            eventTypeOption = StringVar()
            eventTypeOption.set(eventType)
            eventTypeOption.trace("w", lambda *args, row=rowCount,
                                              eventTypeOptionInstance=eventTypeOption: self.customized_event_type_changed(
                eventTypeOptionInstance, row, *args))

            eventTypeOptionMenu = OptionMenu(self.profileExerciseFrame, eventTypeOption,
                                             *self.eventTypes)
            eventTypeOptionMenu.config(width=18)
            eventTypeOptionMenu.grid(row=rowCount, column=1, pady=5, padx=0)

            if eventType == "keypress":
                keyLabel = Label(self.profileExerciseFrame, text=eventContent, background='light grey')
                keyLabel.grid(sticky="W", row=rowCount, column=2, pady=5, padx=5)
                keyLabel.bind("<Button-1>", self.key_map)
                self.customizedProfiles.append((checkBoxVar, checkBox, eventTypeOption, keyLabel))

            elif eventType == "mouse":
                mouseEventOption = StringVar()
                mouseEventOption.set(eventContent)
                mouseEventTypeOptionMenu = OptionMenu(self.profileExerciseFrame, mouseEventOption,
                                                      *self.mouseEvents)
                mouseEventTypeOptionMenu.config(width=18)
                mouseEventTypeOptionMenu.grid(row=rowCount, column=2, pady=5, padx=0)
                self.customizedProfiles.append((checkBoxVar, checkBox, eventTypeOption, mouseEventOption))

            elif eventType == "brightness":
                self.customizedProfiles.append((checkBoxVar, checkBox, eventTypeOption))
            rowCount += 1

        addNewCustomizedButton = Button(self.profileExerciseFrame, text="Add a new customized exercise",
                                        command=self.add_customized_motion_window)
        addNewCustomizedButton.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1
        removeCustomizedButton = Button(self.profileExerciseFrame, text="Delete existed customized exercise",
                                        command=self.remove_customized_motion_window)
        removeCustomizedButton.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1

        initialConfigtLabel1 = Label(self.profileExerciseFrame, text="INITIAL CONFIGURATION",
                                     font=('Helvetica', 18, 'bold'))
        initialConfigtLabel1.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1

        initialConfigtLabel2 = Label(self.profileExerciseFrame,
                                     text="Initial configuration is necessary if this is your "
                                          "first time using the Exercise Module", wraplengt=400,
                                     justify=LEFT, font=('Helvetica', 10))
        initialConfigtLabel2.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1

        if not config.has_section('roi'):
            initialConfigtLabel3 = Label(self.profileExerciseFrame, text='Initial Config not completed', fg='red',
                                         justify=LEFT
                                         , font=('Helvetica', 10))
        else:
            initialConfigtLabel3 = Label(self.profileExerciseFrame, text='Initial Config completed', fg='green',
                                         justify=LEFT, font=('Helvetica', 10))
        initialConfigtLabel3.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1

        initialConfigButton = Button(self.profileExerciseFrame, text="Initial Configuration",
                                     command=self.initial_config_window)
        initialConfigButton.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)

        rowCount = 0
        extremityLabel = Label(self.profileExtremityFrame, text="DEFAULT", font=('Helvetica', 18, 'bold'))
        extremityLabel.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1
        for key in extremityTriggersDict:
            checkBoxVar = IntVar()
            if (int(extremityTriggerInputsDict.get(key))) == 1:
                checkBoxVar.set(1)
            else:
                checkBoxVar.set(0)
            checkBox = Checkbutton(self.profileExtremityFrame, text=key, variable=checkBoxVar)
            checkBox.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)

            if (len(extremityTriggersDict.get(key).split('+')) == 3):
                pos = extremityTriggersDict.get(key).split('+')[0]
                eventType = extremityTriggersDict.get(key).split('+')[1]
                eventContent = extremityTriggersDict.get(key).split('+')[2]
            else:
                pos = extremityTriggersDict.get(key).split('+')[0]
                eventType = extremityTriggersDict.get(key).split('+')[1]
                eventContent = ''

            posLabel = Label(self.profileExtremityFrame, text=pos, background='light grey')
            posLabel.grid(sticky="W", row=rowCount, column=1, pady=5, padx=5)
            posLabel.bind("<Button-1>", self.change_trigger_pos_window)

            eventTypeOption = StringVar()
            eventTypeOption.set(eventType)
            eventTypeOption.trace("w", lambda *args, row=rowCount,
                                              eventTypeOptionInstance=eventTypeOption: self.extremity_event_type_changed(
                eventTypeOptionInstance, row, *args))

            eventTypeOptionMenu = OptionMenu(self.profileExtremityFrame, eventTypeOption,
                                             *self.eventTypes)
            eventTypeOptionMenu.config(width=18)
            eventTypeOptionMenu.grid(row=rowCount, column=2, pady=5, padx=0)

            if eventType == "keypress":
                keyLabel = Label(self.profileExtremityFrame, text=eventContent, background='light grey')
                keyLabel.grid(sticky="W", row=rowCount, column=3, pady=5, padx=5)
                keyLabel.bind("<Button-1>", self.key_map)
                self.extremityProfiles.append((checkBoxVar, checkBox, posLabel, eventTypeOption, keyLabel))
            elif eventType == "mouse":
                mouseEventOption = StringVar()
                mouseEventOption.set(eventContent)
                mouseEventTypeOptionMenu = OptionMenu(self.profileExtremityFrame, mouseEventOption,
                                                      *self.mouseEvents)
                mouseEventTypeOptionMenu.config(width=18)
                mouseEventTypeOptionMenu.grid(row=rowCount, column=3, pady=5, padx=0)
                self.extremityProfiles.append((checkBoxVar, checkBox, posLabel, eventTypeOption, mouseEventOption))
            elif eventType == "brightness":
                self.extremityProfiles.append((checkBoxVar, checkBox, posLabel, eventTypeOption))
            rowCount += 1

        addNewExtremityButton = Button(self.profileExtremityFrame, text="Add a new extremity trigger",
                                       command=self.add_extremity_window)
        addNewExtremityButton.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)
        rowCount += 1
        removeExtremityButton = Button(self.profileExtremityFrame, text="Delete existed extremity triggers",
                                       command=self.remove_extremity_window)
        removeExtremityButton.grid(sticky="W", row=rowCount, column=0, pady=5, padx=5)

        self.profileNotebook.add(self.profileExerciseFrame, text="Exercise")
        self.profileNotebook.add(self.profileExtremityFrame, text="Extremity")

        self.instructionLabel2 = Label(profileSettingsFrame,
                                       text='Click APPLY to save the settings.\nClick \'X\' on the upper right corner to close'
                                            ' the page.', font=("Courier", 10))
        self.instructionLabel2.config(anchor=CENTER)
        self.instructionLabel2.pack()
        apply_button = Button(profileSettingsFrame, text="APPLY", command=self.apply_profile).pack()

    def default_event_type_changed(self, eventTypeOptionInstance, row, *args):
        index = 0
        count = 0
        for profile in self.defaultProfiles:
            if profile[2] == eventTypeOptionInstance:
                if eventTypeOptionInstance.get() == "mouse":
                    mouseEventOption = StringVar()
                    mouseEventOption.set(self.mouseEvents[0])
                    newProfile = (profile[0], profile[1], profile[2], mouseEventOption)
                else:
                    keyLabel = Label(self.profileExerciseFrame, text="w", background='light grey')
                    keyLabel.grid(sticky="W", row=row, column=2, pady=5, padx=5)
                    keyLabel.bind("<Button-1>", self.key_map)
                    newProfile = (profile[0], profile[1], profile[2], keyLabel)
                index = count
                break
            count += 1
        self.defaultProfiles[index] = newProfile
        self.apply_profile()

    def customized_event_type_changed(self, eventTypeOptionInstance, row, *args):
        index = 0
        count = 0
        # print(self.customizedProfiles)
        for profile in self.customizedProfiles:
            if profile[2] == eventTypeOptionInstance:
                if eventTypeOptionInstance.get() == "mouse":
                    mouseEventOption = StringVar()
                    mouseEventOption.set(self.mouseEvents[0])
                    newProfile = (profile[0], profile[1], profile[2], mouseEventOption)
                else:
                    keyLabel = Label(self.profileExerciseFrame, text="w", background='light grey')
                    keyLabel.grid(sticky="W", row=row, column=2, pady=5, padx=5)
                    keyLabel.bind("<Button-1>", self.key_map)
                    newProfile = (profile[0], profile[1], profile[2], keyLabel)
                index = count
                break
            count += 1
        self.customizedProfiles[index] = newProfile
        self.apply_profile()

    def extremity_event_type_changed(self, eventTypeOptionInstance, row, *args):
        index = 0
        count = 0
        for profile in self.extremityProfiles:
            if profile[3] == eventTypeOptionInstance:
                if eventTypeOptionInstance.get() == "mouse":
                    mouseEventOption = StringVar()
                    mouseEventOption.set(self.mouseEvents[0])
                    newProfile = (profile[0], profile[1], profile[2], profile[3], mouseEventOption)
                elif eventTypeOptionInstance.get() == "keypress":
                    keyLabel = Label(self.profileExtremityFrame, text="w", background='light grey')
                    keyLabel.grid(sticky="W", row=row, column=2, pady=5, padx=5)
                    keyLabel.bind("<Button-1>", self.key_map)
                    newProfile = (profile[0], profile[1], profile[2], profile[3], keyLabel)
                else:
                    newProfile = (profile[0], profile[1], profile[2], profile[3])
                index = count
                break
            count += 1
        self.extremityProfiles[index] = newProfile
        self.apply_profile()
        self.profileNotebook.select(1)

    def add_extremity_window(self):
        self.addExtremityWindow = Toplevel(self.window)
        self.addExtremityWindow.geometry("420x360+100+100")
        self.addExtremityWindow.resizable(False, False)
        self.addExtremityTextLabel = Label(self.addExtremityWindow,
                                           text="Please enter the trigger name",
                                           wraplengt=330, justify=LEFT)
        self.addExtremityTextLabel.pack()
        self.addExtremityEntry = Entry(self.addExtremityWindow)
        self.addExtremityEntry.pack()
        self.addExtremityButton = Button(self.addExtremityWindow, text="Add",
                                         command=self.add_extremity)
        self.addExtremityButton.pack(padx=10)

    def add_extremity(self):
        config = ConfigParser()
        config.read('config.ini')
        config.set('extremity', self.addExtremityEntry.get(), '(0,0)+keypress+w')
        with open('config.ini', 'w') as f:
            config.write(f)

        inputs = ConfigParser()
        inputs.read('current_inputs.ini')
        inputs.set('extremity', self.addExtremityEntry.get(), '0')
        with open('current_inputs.ini', 'w') as f:
            inputs.write(f)

        self.addExtremityWindow.destroy()
        self.profileWindow.destroy()
        self.profile_window()
        self.profileNotebook.select(1)

    def remove_extremity_window(self):
        self.removeExtremityWindow = Toplevel(self.window)
        self.removeExtremityWindow.geometry("420x360+100+100")
        self.removeExtremityWindow.resizable(False, False)
        label = Label(self.removeExtremityWindow,
                      text="Caution: Once you delete a trigger, it is gone forever.", )
        label.grid(sticky="W", row=0, column=0, pady=5, padx=5)
        config = ConfigParser()
        config.read('config.ini')
        extremityDict = dict(config.items('extremity'))
        extremities = list(extremityDict.keys())

        self.extremityOption = StringVar()
        self.extremityOption.set(extremities[0])
        extremityOptionMenu = OptionMenu(self.removeExtremityWindow, self.extremityOption,
                                         *extremities)

        extremityOptionMenu.config(width=18)
        extremityOptionMenu.grid(row=1, column=0, pady=5, padx=0)
        deleteButton = Button(self.removeExtremityWindow, text="Delete", command=self.delete_extremity)
        deleteButton.grid(row=1, column=1, pady=5, padx=0)

    def delete_extremity(self):
        config = ConfigParser()
        config.read('config.ini')
        for item in config.items('extremity'):
            if item[0] == self.extremityOption.get():
                config.remove_option('extremity', item[0])
                config.write(open('config.ini', 'w'))
        inputs = ConfigParser()
        inputs.read('current_inputs.ini')
        for item in inputs.items('extremity'):
            if item[0] == self.extremityOption.get():
                inputs.remove_option('extremity', item[0])
                inputs.write(open('current_inputs.ini', 'w'))
        self.removeExtremityWindow.destroy()
        self.profileWindow.destroy()
        self.profile_window()
        self.profileNotebook.select(1)

    def remove_customized_motion_window(self):
        self.removeCustomizedMotionWindow = Toplevel(self.window)
        self.removeCustomizedMotionWindow.geometry("420x360+100+100")
        self.removeCustomizedMotionWindow.resizable(False, False)
        label = Label(self.removeCustomizedMotionWindow,
                      text="Caution: Once you delete an exercise, it is gone forever.", )
        label.grid(sticky="W", row=0, column=0, pady=5, padx=5)

        config = ConfigParser()
        config.read('config.ini')
        customizedExercisesDict = dict(config.items('customized'))
        customizedExercises = list(customizedExercisesDict.keys())

        self.customizedExercisesOption = StringVar()
        self.customizedExercisesOption.set(customizedExercises[0])
        customizedExercisesOptionMenu = OptionMenu(self.removeCustomizedMotionWindow, self.customizedExercisesOption,
                                                   *customizedExercises)

        customizedExercisesOptionMenu.config(width=18)
        customizedExercisesOptionMenu.grid(row=1, column=0, pady=5, padx=0)
        deleteButton = Button(self.removeCustomizedMotionWindow, text="Delete", command=self.delete_customized_exercise)
        deleteButton.grid(row=1, column=1, pady=5, padx=0)

    def delete_customized_exercise(self):
        config = ConfigParser()
        config.read('config.ini')
        for item in config.items('customized'):
            if item[0] == self.customizedExercisesOption.get():
                config.remove_option('customized', item[0])
                config.write(open('config.ini', 'w'))

        inputs = ConfigParser()
        inputs.read('current_inputs.ini')
        for item in inputs.items('customized'):
            print(item[0])
            if item[0] == self.customizedExercisesOption.get():
                inputs.remove_option('customized', item[0])
                inputs.write(open('current_inputs.ini', 'w'))

        dirpath = "models/customized/" + self.customizedExercisesOption.get()
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        self.removeCustomizedMotionWindow.destroy()
        self.profileWindow.destroy()
        self.profile_window()

    def apply_profile(self):
        config = ConfigParser()
        config.read('config.ini')
        currentInputs = ConfigParser()
        currentInputs.read('current_inputs.ini')

        for profile in self.defaultProfiles:
            if profile[2].get() == "mouse":
                config.set('default', profile[1]['text'], profile[2].get() + '+' + profile[3].get())
                config.write(open('config.ini', 'w'))
            elif profile[2].get() == "keypress":
                config.set('default', profile[1]['text'], profile[2].get() + '+' + profile[3]['text'])
                config.write(open('config.ini', 'w'))
            else:
                config.set('default', profile[1]['text'], profile[2].get())
                config.write(open('config.ini', 'w'))

            if profile[0].get() == 1:
                currentInputs.set('default', profile[1]['text'], str(1))
            else:
                currentInputs.set('default', profile[1]['text'], str(0))
            currentInputs.write(open('current_inputs.ini', 'w'))

        for profile in self.customizedProfiles:
            if profile[2].get() == "mouse":
                config.set('customized', profile[1]['text'], profile[2].get() + '+' + profile[3].get())
                config.write(open('config.ini', 'w'))
            elif profile[2].get() == "keypress":
                # print(profile)
                config.set('customized', profile[1]['text'], profile[2].get() + '+' + profile[3]['text'])
                config.write(open('config.ini', 'w'))
            else:
                config.set('customized', profile[1]['text'], profile[2].get())
                config.write(open('config.ini', 'w'))

            if profile[0].get() == 1:
                currentInputs.set('customized', profile[1]['text'], str(1))
            else:
                currentInputs.set('customized', profile[1]['text'], str(0))
            currentInputs.write(open('current_inputs.ini', 'w'))
        for profile in self.extremityProfiles:
            if profile[3].get() == "mouse":
                option = profile[2]['text'] + '+' + profile[3].get() + '+' + profile[4].get()
                config.set('extremity', profile[1]['text'], option)
                config.write(open('config.ini', 'w'))
            elif profile[3].get() == "keypress":
                option = profile[2]['text'] + '+' + profile[3].get() + '+' + profile[4]['text']
                config.set('extremity', profile[1]['text'], option)
                config.write(open('config.ini', 'w'))
            else:
                option = profile[2]['text'] + '+' + profile[3].get()
                config.set('extremity', profile[1]['text'], option)
                config.write(open('config.ini', 'w'))

            if profile[0].get() == 1:
                currentInputs.set('extremity', profile[1]['text'], str(1))
            else:
                currentInputs.set('extremity', profile[1]['text'], str(0))
            currentInputs.write(open('current_inputs.ini', 'w'))

        self.profileWindow.destroy()
        self.profile_window()

    def key_map(self, event):
        event.widget['text'] = "???"
        event.widget['background'] = "green"
        event.widget.focus_set()
        event.widget.bind("<Key>", lambda event: self.key_map_completed(event, True))
        event.widget.bind("<Button-1>", lambda event: self.key_map_completed(event, False))

    def key_map_completed(self, event, isKeyboardEvent):
        if (isKeyboardEvent):
            keypress = event.keysym
            event.widget.bind("<Button-1>", self.key_map)
        else:
            keypress = "Left-Click"
            event.widget.bind("<Button-1>", self.key_map)
        event.widget['text'] = keypress
        event.widget['background'] = 'light grey'

    def change_trigger_pos_window(self, event):
        change_trigger_pos_window = Toplevel(self.window)
        change_trigger_pos_window.resizable(False, False)
        change_trigger_pos_window.geometry("720x480+100+100")
        pos = tuple(map(int, event.widget['text'][1:-1].split(',')))
        x = pos[0]
        y = pos[1]
        canvas = Canvas(change_trigger_pos_window)
        canvas.config(width=720, height=480, bg='black')
        canvas.create_oval(x - 30, y - 30, x + 30, y + 30, outline="#f11",
                           fill="#1f1", width=0)
        canvas.pack()
        newpos = event.widget
        canvas.bind("<Button-1>", lambda event: self.change_trigger_pos(event, newpos))

    def change_trigger_pos(self, event, newpos):
        event.widget.delete("all")
        event.widget.create_oval(event.x - 30, event.y - 30, event.x + 30, event.y + 30, outline="#f11",
                                 fill="#1f1", width=0)
        newpos['text'] = '(' + str(event.x) + ',' + str(event.y) + ')'

    def initial_config_window(self):
        self.configWindow = Toplevel(self.window)
        self.configWindow.resizable(False, False)

        self.configFrame = Frame(self.configWindow)
        self.configFrame.pack(fill=X, side=BOTTOM)

        self.configLabel = Label(self.configWindow,
                                 text="For better motion tracking, before you start your training, a photo of you performing your chosen motion will be taken in 10 seconds. Press Start Initial Configuration when you are ready.",
                                 wraplengt=330, justify=LEFT)
        self.configLabel.pack()

        self.configButton = Button(self.configFrame, text="Start Initial Configuration",
                                   command=self.start_initial_configuration)
        self.configButton.pack(padx=3)

    def start_initial_configuration(self):
        self.configWindow.destroy()
        config.takePhoto(0)
        self.roiWindow = Toplevel(self.window)
        self.roiWindow.geometry("420x360+100+100")
        self.roiWindow.resizable(False, False)

        self.imageLabel = PhotoImage(file='imgs/roi_big.png')
        self.roiImageLabel = Label(self.roiWindow, image=self.imageLabel)
        self.roiImageLabel.pack()

        self.roiTextLabel = Label(self.roiWindow,
                                  text="Now please use your mouse to select the area of your entire body. Press SPACE or ENTER to confirm your selection",
                                  wraplengt=330, justify=LEFT)
        self.roiTextLabel.pack()
        self.roiButton = Button(self.roiWindow, text="Start ROI Selection", command=self.start_ROI_selection)
        self.roiButton.pack(padx=10)

    def start_ROI_selection(self):
        config.selectROI()
        self.roiTextLabel['text'] = "Initial Configuration is successful! You can close this window now."
        self.roiWindow.destroy()
        self.profileWindow.destroy()
        self.profile_window()

    def add_customized_motion_window(self):
        self.customizedMotionWindow = Toplevel(self.window)
        self.customizedMotionWindow.geometry("420x260+100+100")
        self.customizedMotionWindow.resizable(False, False)
        self.customizedMotionTextLabel1 = Label(self.customizedMotionWindow,
                                                text="Please enter the exercise name, note the name should not contain space.",
                                                wraplengt=330, justify=LEFT)
        self.customizedMotionTextLabel1.pack()
        self.customizedMotionEntry = Entry(self.customizedMotionWindow)
        self.customizedMotionEntry.pack()
        self.customizedMotionButton = Button(self.customizedMotionWindow, text="Start Creating",
                                             command=self.create_customized_motion_1)
        self.customizedMotionButton.pack(padx=10)
        self.customizedMotionTextLabel2 = Label(self.customizedMotionWindow,
                                                text="Note: A video of you doing the exercise will be taken first, followed by a second video of you not doing the exercise.",
                                                wraplengt=330, justify=LEFT)
        self.customizedMotionTextLabel2.pack(pady=10)

    def create_customized_motion_1(self):
        self.newCustomizedMotion = record_customized_motion.RecordCustomizedMotion(int(self.cameraOption.get()[-1]),
                                                                                   self.customizedMotionEntry.get())
        if (self.newCustomizedMotion.record(1)):
            self.customizedMotionTextLabel1["text"] = "Now record a video of you not doing the exercise"
            self.customizedMotionEntry.destroy()
            self.customizedMotionButton["text"] = "Next step"
            self.customizedMotionButton["command"] = self.create_customized_motion_0

    def create_customized_motion_0(self):
        if (self.newCustomizedMotion.record(0)):
            self.customizedMotionTextLabel1[
                "text"] = "Motion recorded successfully! Training might take a couple of minutes." \
                          "Please reopen the profile page after the training is completed."
            self.customizedMotionButton["text"] = "Start training your model! "
            self.customizedMotionButton["command"] = self.train_model

    def train_model(self):
        self.newCustomizedModel = train_customized_model.CustomizedModel(self.newCustomizedMotion.motionType)
        self.newCustomizedModel.train()

        config = ConfigParser()
        config.read('config.ini')
        config.set('customized', self.newCustomizedMotion.motionType, 'keypress+w')
        with open('config.ini', 'w') as f:
            config.write(f)

        inputs = ConfigParser()
        inputs.read('current_inputs.ini')
        inputs.set('customized', self.newCustomizedMotion.motionType, '0')
        with open('current_inputs.ini', 'w') as f:
            inputs.write(f)
        self.customizedMotionWindow.destroy()
        self.profileWindow.destroy()
        self.profile_window()

    def start(self):
        self.timerLabel = Label(self.controls_frame, text='3', font=('Helvetica', 18, 'bold'))
        self.timerLabel.pack()
        self.timerLabel.after(1000, self.timer_count_down)

    def count_down_complete(self):
        if (self.motionDetection == None):
            self.motionDetection = exercise_detection_controller.ExerciseDetectionController(self.cameraOption.get())
            self.motionDetection.isDetecting = True
            if not self.motionDetection.get_config_settings():
                messagebox.showinfo("No Initial Configuratio Detected",
                                    "Please complete the initial configuration first")
                self.stop()
                return
        self.appStatus = 1

    def create_target_coordinates(self, event):
        self.motionDetection.targets.append((event.x, event.y))

    def stop(self):
        # self.motionDetection.testingLog.close()
        self.appStatus = 0
        if self.motionDetection != None:
            self.motionDetection.__del__()
            self.motionDetection = None
        self.isDetecting = False
        self.start_button['image'] = self.start_btn_img
        self.start_button['command'] = self.start

    def motion_type_changed(self, *args):
        if (self.appStatus == 1 or self.appStatus == 2):
            self.stop()

    def timer_count_down(self):
        if int(self.timerLabel['text']) > 0:
            self.timerLabel.config(text=str(int(self.timerLabel['text']) - 1))
            self.timerLabel.after(1000, self.timer_count_down)
        else:
            self.timerLabel.destroy()
            self.count_down_complete()

    def camera_changed(self, *args):
        if (self.appStatus == 1 or self.appStatus == 2):
            self.stop()

    def exit(self):
        self.cleanup_mei()
        self.window.destroy()
        sys.exit()

    def cleanup_mei(self):
        # Code from https://github.com/pyinstaller/pyinstaller/issues/2379
        from shutil import rmtree

        mei_bundle = getattr(sys, "_MEIPASS", False)

        if mei_bundle:
            dir_mei, current_mei = mei_bundle.split("_MEI")
            for file in os.listdir(dir_mei):
                if file.startswith("_MEI") and not file.endswith(current_mei):
                    try:
                        rmtree(os.path.join(dir_mei, file))
                    except PermissionError:  # mainly to allow simultaneous pyinstaller instances
                        pass


ExerciseGesture(Tk(), "ExerciseModule")
