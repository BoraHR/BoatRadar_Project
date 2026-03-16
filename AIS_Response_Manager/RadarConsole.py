from tkinter import *
import tkinter as tk
from tkinter import ttk
from functools import partial
from RadarPloter import RadarPlotter
import os
from PIL import Image, ImageTk

class RadarConsole:
    def __init__(self, window):
        self.myBoat = None
        self.plotter = RadarPlotter()
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.window = window
        self.window.title("AIS Radar Console")
        # self.window.attributes('-fullscreen', True)

        # ---- state ----
        self.boat_id = 1
        self.km_range = 3
        self.time_window = 10
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img_{self.km_range}.png")
        self.img_compas = os.path.join(self.BASE_DIR, f"Radar/Compas/Current/360_Rotation-TranparantCenter.png")

        # ---- radar image ----
        # Create a placeholder label now; we'll populate it (and keep a reference to
        # the PhotoImage) later in `update_image`.
        self.image = None
        self.composite = None
        self.image_label = tk.Label(self.window)
        self.image_label.pack()

        # Load any existing images immediately (transparent overlay is handled)
        self.update_image()

        # ---- UI ----
        self.range_var = StringVar(self.window)

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
               command=window.destroy,
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
            

    def update_label(self):
        self.range_var.set(f"{self.km_range} KM")
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img_{self.km_range}.png")
        self.img_compas = os.path.join(self.BASE_DIR, f"Radar/Compas/Current/360_Rotation-TranparantCenter.png")

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
            

            if os.path.isfile(self.img_compas):
                overlay = Image.open(self.img_compas).convert("RGBA")

                if overlay.size != base.size:
                    overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)
                    
                base = Image.alpha_composite(base, overlay)

            # Convert to Tk image
            img = ImageTk.PhotoImage(base, master=self.window)

            # Save reference
            self.composite = img

            # Update label
            self.image_label.configure(image=self.composite)
        except Exception as e:
            print("Radar reload failed:")
            print(e)

    # def update_image(self):
    
    #     if os.path.isfile(self.img_loc):
    #         try:
    #             self.image = tk.PhotoImage(master=self.window, file=self.img_loc)
    #             self.image_label.configure(image=self.image)
    #         except Exception as e:
    #             print("Radar reload failed:")
    #             print(e)
    #             print("at update_image")

    def radar_loop(self):
        self.update_label()

        self.plotter.InRangeHelper(
            self.boat_id,
            self.km_range,
            self.time_window
        )

        self.update_image()

        # run again after 1000 ms (1 second)
        if self.window.winfo_exists():
            self.window.after(1000, self.radar_loop)

    def get_boat_data(self, id):
        return self.plotter.GetBoat(id)