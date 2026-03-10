from tkinter import *
import tkinter as tk
from functools import partial
import threading
from RadarPloter import InRangeHelper  # adjust import!
import os
import asyncio

class RadarConsole:
    def __init__(self, window):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.window = window
        self.window.title("AIS Radar Console")

        # ---- state ----
        self.boat_id = 1
        self.km_range = 3
        self.time_window = 10
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/img_{self.km_range}.png")

        # ---- radar image ----
        # load radar snapshot if it exists; associate image with our window
        # so the TK interpreter doesn't complain later about a missing
        # ``pyimageX`` handle.  ``PhotoImage`` must be created after the root
        # window is instantiated, and we keep ``self.image`` alive to prevent
        # garbage collection.
        if os.path.isfile(self.img_loc):
            try:
                self.image = tk.PhotoImage(master=self.window, file=self.img_loc)
                self.image_label = tk.Label(self.window, image=self.image)
                self.image_label.pack()
            except Exception as e:
                print("Radar load failed:")
                print(e)
                print("at __init__ (loading)")
        else:
            # file isn't there yet; create an empty placeholder label and fill
            # it later when the PNG appears
            self.image = None
            self.image_label = tk.Label(self.window)
            self.image_label.pack()

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
               text="SCAN",
               font=("Consolas", 14),
               bg="green",
               command=self.scan
               ).pack(pady=10)
        
        self.radar_loop()
            

    def update_label(self):
        self.range_var.set(f"{self.km_range} KM")
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/img_{self.km_range}.png")

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

        InRangeHelper(
            self.boat_id,
            self.km_range,
            self.time_window
        )

        self.update_label()
        self.update_image()

    def _run_scan(self):
        InRangeHelper(
            self.boat_id,
            self.km_range,
            self.time_window
        )
        self.window.after(0, self.update_label)

    def update_image(self):
        # only reload if the image file actually exists
        if os.path.isfile(self.img_loc):
            try:
                self.image = tk.PhotoImage(master=self.window, file=self.img_loc)
                self.image_label.configure(image=self.image)
            except Exception as e:
                print("Radar reload failed:")
                print(e)
                print("at update_image")
        # otherwise do nothing; the new image hasn't been generated yet

    def radar_loop(self):
        self.update_label()

        InRangeHelper(
            self.boat_id,
            self.km_range,
            self.time_window
        )

        self.update_image()

        # run again after 1000 ms (1 second)
        self.window.after(1000, self.radar_loop)