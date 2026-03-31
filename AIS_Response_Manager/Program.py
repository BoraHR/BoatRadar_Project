from RadarConsole import RadarConsole
from tkinter import *
import shutil
import traceback
from pyais_decoder import Save_DecodedData, Create_AIS_Render_History
import os

if __name__ == "__main__":
    # ---- start app ----
    # https://en.bioerrorlog.work/entry/get-memory-disk-in-python
    total, used, free = shutil.disk_usage('/')
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
    ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
    if free / (2**30) < 1.00:
        print("!!! WARNING !!!")
        print(f'CurrentDiskSpace: {free / (2**30)} GB')
        print("Aplication might crash do to low DiskMemory for the renderer")
        print("Consider freeing up memory to atleast 1 GB of DiskSpace")
        print()

    try:
        # Save_DecodedData(ais_file1)
        # Save_DecodedData(ais_file2)
        Create_AIS_Render_History()
        window = Tk()
        app = RadarConsole(window)
        window.mainloop()
    except Exception as e:
        print()
        print("AN ERROR HAS BEING CAUGHT BY MAIN:")
        print(traceback.format_exc())
        print("CONTINUEING OPERATION...")
        print()