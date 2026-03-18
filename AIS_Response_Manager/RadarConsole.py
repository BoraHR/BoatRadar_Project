# https://www.geeksforgeeks.org/python/python-gui-tkinter/
from tkinter import *
import tkinter as tk
from tkinter import ttk
from functools import partial
from RadarPloter import RadarPlotter
import os, shutil
from PIL import Image, ImageTk
import time

class RadarConsole:
    def __init__(self, window):
        self.killswitch = False
        self.myBoat = None
        self.plotter = RadarPlotter()
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.window = window
        self.window.title("AIS Radar Console")
        self.window.attributes('-fullscreen', True)

        # ---- state ----
        self.boat_id = 1
        self.km_range = 3
        self.time_window = 10
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img_{self.km_range}.png")
        self.img_compas = os.path.join(self.BASE_DIR, f"Radar/Compas/Current/360_Rotation-TranparantCenter (1).png")

        # ---- radar image ----
        # Create a placeholder label now; we'll populate it (and keep a reference to
        # the PhotoImage) later in `update_image`.
        self.image = None
        self.overlay = None
        self.composite = None
        self.image_label = tk.Label(self.window)
        self.image_label.pack()

        # Load any existing images immediately (transparent overlay is handled)
        self.update_image()

        # ---- UI ----

        # menu
        self.range_var = StringVar(self.window)
        
        # window = tk.Menu(root)
        # window.config(menu=menu)

        # window.add_cascade(label="File", menu=filemenu)
        # window.add_command(label="New")
        # window.add_command(label="Open...")
        # window.add_separator()
        # window.add_command(label="Exit", command=root.quit)

        # helpmenu = tk.Menu(menu)
        # menu.add_cascade(label="Help", menu=helpmenu)
        # helpmenu.add_command(label="About")

        # display
        Label(window,
              text="Radar Range",
              font=("Consolas", 14)).pack(pady=(10, 0))

        Label(window,
              textvariable=self.range_var,
              font=("Consolas", 20, "bold"),
              fg="#00FF00").pack()

        # buttons frame
        btn_frame = Frame(window)
        btn_frame.pack(pady=10)

        Button(btn_frame,
               text="<",
               width=5,
               font=("Consolas", 16),
               command=lambda: self.change_range(-1)
               ).pack(side=LEFT, padx=5)

        Button(btn_frame,
               text=">",
               width=5,
               font=("Consolas", 16),
               command=lambda: self.change_range(+1)
               ).pack(side=LEFT, padx=5)

        Button(window,
               text="KILL TERMINAL",
               font=("Consolas", 14),
               bg="red",
               command=self.Detroy,
               ).pack(pady=10)
        
        # Create a Combobox widget for option selection
        # Create a Combobox widget for option selection
        self.combo_box = ttk.Combobox(
            window,
            values=["RANGE", "CPA", "TCPA"],
            state="readonly"
        )

        self.combo_box.pack(side=RIGHT)
        self.combo_box.set("RANGE")
                    
        self.radar_loop()

    def Detroy(self):
        self.killswitch = True
        print("Clossing program please wait...")
        time.sleep(2.1) # give self.radarloop time to register killswitch command, to ensure all files are closed before deletion.
        self.CleanFiles()
            
    def CleanFiles(self):
        retry = False
        if self.BASE_DIR.endswith("AIS_Response_Manager"):
            toDelete = [os.path.join(self.BASE_DIR, f"Radar/PostScript/"), os.path.join(self.BASE_DIR, f"Radar/Renders/")]
            for folder in toDelete:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
                        retry = True
                        print("Retrying...")
        else:
            print("OS Dirrectory seems to be wrong")
            print("ensure BASE_DIR is setup properly")
        
        if retry:
            time.sleep(1)
            self.CleanFiles()

    def update_label(self):
        self.range_var.set(f"{self.km_range} KM")
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img_{self.km_range}.png")
        if os.path.isfile(self.img_compas):
            self.overlay = Image.open(self.img_compas).convert("RGBA")
        
    def change_range(self, delta):
        self.km_range += delta

        if self.km_range < 1:
            self.km_range = 1
        if self.km_range > 50:
            self.km_range = 50

        self.update_label()
        self.update_image()

    def scan(self):
        print(f"Scanning at {self.km_range} KM...")
        self.range_var.set("Scanning...")
        self.window.update()  # keep UI responsive

        self.plotter.InRangeHelper(
            self.boat_id,
            self.km_range,
            self.time_window
        )

        self.update_label()
        self.update_image()

    def _run_scan(self):
        self.plotter.InRangeHelper(
            self.boat_id,
            self.km_range,
            self.time_window
        )
        self.window.after(0, self.update_label)
   
    def update_image(self):

        if not os.path.isfile(self.img_loc):
            return

        try:
            base = Image.open(self.img_loc).convert("RGBA")
            # if os.path.isfile(self.img_compas):
            #     overlay = Image.open(self.img_compas).convert("RGBA")

            if self.overlay.size != base.size:
                self.overlay = self.overlay.resize(base.size, Image.Resampling.LANCZOS)
                
            base = Image.alpha_composite(base, self.overlay)

            # Convert to Tk image
            img = ImageTk.PhotoImage(base, master=self.window)

            # Save reference
            self.composite = img

            # Update label
            self.image_label.configure(image=self.composite)
        except Exception as e:
            print("Radar reload failed:")
            print(e)

    def radar_loop(self):
        if self.killswitch == True:
            self.window.destroy()
            self.plotter.draw.CloseDrawer()
            return
        
        start = time.time()
        self.update_label()

        self.plotter.InRangeHelper(
            self.boat_id,
            self.km_range,
            self.time_window
        )

        self.update_image()

        # run again after 1000 ms (1 second)
        if self.window.winfo_exists():
            self.window.after(500, self.radar_loop)
        end = time.time()
        print(f"Loop performance: {end - start}")

    def get_boat_data(self, id):
        return self.plotter.GetBoat(id)