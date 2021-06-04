from tkinter import *
import subprocess


def main():
    window = Tk()
    window.title("Welcome to MotionInput app")
    window.geometry('600x450+100+100')
    window.resizable(False,False)

    lbl1 = Label(window, bg="#BB3096",fg="white",text="MotionInput", font=("Arial Bold", 50)).grid(
        column=0, row=0,sticky="nsew")


    authorLabel = Label(window, text="\nAuthors", font=("Arial Bold", 15)).grid(column=0,row=1)

    nameLabel1=Label(window, text="Emil Almazov\nLu Han").grid(column=0,row=2)


    supervisorLabel=Label(window, text="Supervisors", font=("Arial Bold", 15)).grid(column=0,row=3)

    nameLabel2=Label(window, text="Dr Dean Mohamedally\nMrs Sheena Visram\n").grid(column=0,row=4)



    btn1 = Button(window, text="Desk Gesture",command=btn1clicked,height = 2,width = 20).grid(
        column=0, row=5)
    btn2 = Button(window, text="Exercise Gesture",command=btn2clicked,height=2,width=20).grid(
        column=0, row=6,padx=10, pady=5)

    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.mainloop()
def btn1clicked():
    subprocess.Popen(["python", "desk_gesture.py"], cwd="Desk_Gesture")


def btn2clicked():
    subprocess.Popen(["python", "exercise_gesture.py"], cwd="Exercise_Gesture")



if __name__ == "__main__":
    main()