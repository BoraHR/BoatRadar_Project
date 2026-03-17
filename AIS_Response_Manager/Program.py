from RadarConsole import RadarConsole
from tkinter import *

if __name__ == "__main__":
    # ---- start app ----
    try:
        window = Tk()
        app = RadarConsole(window)
        window.mainloop()
    except Exception as e:
        print("TERMINAL HAS BEEN KILLED")
        print("TERMINATING PROGRAM")
        print(e)
        