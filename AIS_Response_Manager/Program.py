from RadarConsole import RadarConsole
from tkinter import *
import shutil

if __name__ == "__main__":
    # ---- start app ----
    # https://en.bioerrorlog.work/entry/get-memory-disk-in-python
    total, used, free = shutil.disk_usage('/')
    if free / (2**30) < 1.00:
        print("!!! WARNING !!!")
        print(f'CurrentDiskSpace: {free / (2**30)} GB')
        print("Aplication might crash do to low DiskMemory for the renderer")
        print("Consider freeing up memory to atleast 1 GB of DiskSpace")
        print()

    # try:
    window = Tk()
    app = RadarConsole(window)
    window.mainloop()
    # except Exception as e:
    #     print("TERMINAL HAS BEEN KILLED")
    #     print("TERMINATING PROGRAM")
    #     print(e)
        