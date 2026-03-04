from RadarController import *
from tkinter import *
import asyncio

if __name__ == "__main__":
    # ---- start app ----
    window = Tk()
    app = RadarConsole(window)
    window.mainloop()
    app.UpdateIMG()