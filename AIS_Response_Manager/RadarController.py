from tkinter import *

def test_button():
    print("Succes")

window = Tk()

button = Button(window,
                text="Button",
                command=test_button,
                font=("Consolas, 16"),
                fg="#00FF00",
                bg="Green",
                activebackground="#00FF00")

button.pack()

window.mainloop()