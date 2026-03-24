# https://www.geeksforgeeks.org/python/python-gui-tkinter/
from tkinter import *
import tkinter as tk
from tkinter import ttk
from functools import partial
from RadarPlotter import RadarPlotter
import os, shutil
from PIL import Image, ImageTk
import time

class RadarConsole:
    # https://www.adobe.com/creativecloud/design/discover/secondary-colors.html
    
    # -- SET Primary Colors -- #
    # -- RED --
    def set_R_primary(self, R):
        self.RGB_Pri[0] = R
    # -- GREEN --
    def set_G_primary(self, G):
        self.RGB_Pri[1] = G
    # -- BLUE --
    def set_B_primary(self, B):
        self.RGB_Pri[2] = B

    # -- SET Secondary Colors -- #
    def set_R_secondary(self, R):
        self.RGB_Sec[0] = R
    def set_G_secondary(self, G):
        self.RGB_Sec[1] = G
    def set_B_secondary(self, B):
        self.RGB_Sec[2] = B

    # -- SET Tertiary Colors -- #
    def set_R_tertiary(self, R):
        self.RGB_Ter[0] = R
    def set_G_tertiary(self, G):
        self.RGB_Ter[1] = G
    def set_B_tertiary(self, B):
        self.RGB_Ter[2] = B
    
    # -- Helpers -- #    
    def from_rgb(self, rgb):
        # https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
        """translates an rgb tuple of int to a tkinter friendly color code"""
        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def set_2digit(self, value):
        strValue = str(value)
        if len(strValue) == 1:
            return "0"+strValue
        return strValue
    
    # -- Main Console Controller -- #
    def __init__(self, window):
        self.plotter = RadarPlotter()
        
        # RED == self.RGB_{Pri/Sec/Ter}[0]
        # GREEN == self.RGB_{Pri/Sec/Ter}[1]
        # BLUE == self.RGB_{Pri/Sec/Ter}[2]
        # MIN 0, MAX 255

        # -- Primary Colors -- #
        self.RGB_Pri = [144,144,144]#R=[0],#G=[1],
        
        # -- Secondary Colors -- #
        self.RGB_Sec = [141,199,130]

        # -- Tertiary Colors -- #
        self.RGB_Ter = [127,158,128]

        
        self.plotter.draw.setBGColor_RGB(self.RGB_Pri[0], self.RGB_Pri[1], self.RGB_Pri[2])

        # -- Name Conversion for thinker colorscheme -- #
        self.primary_color = self.from_rgb(tuple(self.RGB_Pri))
        self.secondary_color = self.from_rgb(tuple(self.RGB_Sec))
        self.tertiary_color = self.from_rgb(tuple(self.RGB_Ter))

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.killswitch = False
        self.myBoat = None
        
        self.window = window
        self.window.title("AIS Radar Console")
        # self.window.attributes('-fullscreen', True)

        # ---- state ----
        self.boat_id = 1
        self.km_range = 3
        self.time_window = 10
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img_{self.km_range}.png")
        self.img_compas = os.path.join(self.BASE_DIR, f"Radar/Compas/Current/360_Rotation-TranparantCenter (3).png")

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
        self.range_var = StringVar(self.window)
        
        # ---- MENU BAR ----
        menu_bar = tk.Menu(self.window)

        # File menu - TEMPLATE
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open...")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.Quit)

        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help menu - TEMPLATE
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About")

        menu_bar.add_cascade(label="Help", menu=help_menu)

        setting_menu  = tk.Menu(menu_bar, tearoff=0)
        setting_menu.add_command(label="Color Settings", command=self.open_color_window)
        
        menu_bar.add_cascade(label="settings", menu=setting_menu)

        # Attach menu bar to window
        self.window.config(menu=menu_bar)

        # -- UI layer system -- #
        left_frame = Frame(window)
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.pack(side=LEFT, fill=Y)

        center_frame = Frame(window)
        center_frame.rowconfigure(1, weight=1)
        center_frame.columnconfigure(0, weight=1)
        center_frame.pack(fill=Y)

        right_frame = Frame(window)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.pack(side=RIGHT, fill=Y)

        # display
        Label(left_frame,
              text="Radar Range",
              font=("Consolas", 14)).pack(pady=(10, 0))

        Label(left_frame,
              textvariable=self.range_var,
              font=("Consolas", 20, "bold"),
              fg="#00FF00").pack()

        # buttons frame
        btn_frame = Frame(window)
        btn_frame.pack(pady=10)

        Button(left_frame,
               text="<",
               width=5,
               font=("Consolas", 16),
               command=lambda: self.change_range(-1)
               ).pack(side=LEFT, padx=5)

        Button(left_frame,
               text=">",
               width=5,
               font=("Consolas", 16),
               command=lambda: self.change_range(+1)
               ).pack(side=LEFT, padx=5)

        Button(center_frame,
               text="HIDE DRAWER",
               font=("Consolas", 14),
               bg="silver",
               command=self.plotter.draw.screen_toggle,
               ).pack(pady=10)

        
        self.table = ttk.Treeview(right_frame, columns=("ID", "Range", "CPA", "TCPA"), show="headings", height=10)

        self.table.heading("ID", text="ID")
        self.table.heading("Range", text="KM")
        self.table.heading("CPA", text="CPA (m)")
        self.table.heading("TCPA", text="TCPA (s)")

        # Set column widths and prevent resizing
        self.table.column("ID", width=50, stretch=False)
        self.table.column("Range", width=60, stretch=False)
        self.table.column("CPA", width=80, stretch=False)
        self.table.column("TCPA", width=80, stretch=False)

        # self.table.configure(height=10)

        # self.table.pack(side=TOP, padx=20, pady=20)
        
        # Create a Combobox widget for option selection
        self.combo_box = ttk.Combobox(
            right_frame,
            values=["RANGE", "CPA", "TCPA"],
            state="readonly"
        )

        # self.combo_box.pack(side=BOTTOM, padx=5, pady=2)
        self.combo_box.set("RANGE")
                    
        local_DT= time.localtime()

        # hh:mm:ss  DD-MM-YYYY
        self.time = Label(right_frame,
              text=f"{self.set_2digit(local_DT.tm_hour)}:{self.set_2digit(local_DT.tm_min)}:{self.set_2digit(local_DT.tm_sec)} | {self.set_2digit(local_DT.tm_mday)}-{self.set_2digit(local_DT.tm_mon)}-{self.set_2digit(local_DT.tm_year)}",
              font=("Consolas", 20, "bold"),
              bg=self.secondary_color)
        # self.time.pack(side=TOP, padx=5, pady=2)

        # pack the items of rightframe
        # self.time.pack(side=TOP, padx=5, pady=2)
        # self.table.pack(side=TOP, padx=20, pady=20, fill=BOTH, expand=True)
        # self.combo_box.pack(side=TOP, padx=5, pady=10)
        
        self.table.grid(row=1, column=0, sticky="nsew", padx=10)
        self.combo_box.grid(row=2, column=0, pady=5)
        self.time.grid(row=3, column=0, pady=5)
        
        self.style = ttk.Style(window)
        self.radar_loop()

    # -- Radar loop updates plotting device every second -- #
    def radar_loop(self):
        if self.killswitch == True:
            self.window.quit()
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
        self.update_table()

        # run again after 1000 ms (1 second)
        if self.window.winfo_exists():
            self.window.after(500, self.radar_loop)
        end = time.time()
        print(f"Loop performance: {end - start}")

    def Quit(self):
        self.killswitch = True
        print("Closing program...")
        self.window.after(100, self._shutdown)

    def _shutdown(self):
        self.plotter.draw.CloseDrawer()
        self.CleanFiles()
        self.window.destroy()
            
    def CleanFiles(self, attempt = 1):
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
                
        else:
            print("OS Dirrectory seems to be wrong")
            print("ensure BASE_DIR is setup properly")
        
        if retry and attempt <= 10:
            print("Retrying...")
            time.sleep(1)
            self.CleanFiles(attempt+1)
        elif retry:
            print("Max deletion attemts reached.")
            print("terminating task.")
            return

    def update_table(self):
        # Clear old data
        for row in self.table.get_children():
            self.table.delete(row)
        
        # Insert new data
        for entry in self.plotter.RadarConsoleData:
            boat, number, distance, cpa, tcpa = entry

            self.table.insert("", "end", values=(
                number,
                f"{distance:.2f}",
                f"{cpa:.1f}",
                f"{tcpa:.1f}" 
            ))

        # Fill remaining rows with empty placeholders
        remaining = 10 - len(self.plotter.RadarConsoleData)
        for _ in range(max(0, remaining)):
            self.table.insert("", "end", values=("", "", "", ""))

    def get_boat_data(self, id):
        return self.plotter.GetBoat(id)
    
    def open_color_window(self):
        color_win = tk.Toplevel(self.window)
        color_win.title("Radar Background Color")

        # buttons frame
        btn_frame = Frame(color_win)
        btn_frame.pack(pady=10)

        color_button = Button(btn_frame,
                text="UPDATE RGB",
                font=("Consolas", 14),
                bg=self.primary_color,
                command=lambda: self.plotter.draw.setBGColor_RGB(self.RGB_Pri[0], self.RGB_Pri[1], self.RGB_Pri[2])
            )
        color_button.pack(pady=10)
        
        # self.plotter.draw
        r = tk.IntVar(value=self.plotter.draw.RGB[0])
        g = tk.IntVar(value=self.plotter.draw.RGB[1])
        b = tk.IntVar(value=self.plotter.draw.RGB[2])

        rLabel = tk.Label(color_win, text=f"Red | Current: {self.RGB_Pri[0]}")
        rLabel.pack()
        tk.Scale(color_win, from_=0, to=255, orient="horizontal", variable=r, command=lambda val: 
            (
                self.set_R_primary(int(val)), 
                color_button.config(bg=self.from_rgb(tuple(self.RGB_Pri))),
                rLabel.config(text=f"RED | Current: {val}")
            )
        ).pack()

        gLabel = tk.Label(color_win, text=f"GREEN | Current: {self.RGB_Pri[1]}")
        gLabel.pack()
        tk.Scale(color_win, from_=0, to=255, orient="horizontal", variable=g, command=lambda val: 
            (
                self.set_G_primary(int(val)), 
                color_button.config(bg=self.from_rgb(tuple(self.RGB_Pri))),
                gLabel.config(text=f"GREEN | Current: {val}")
            )
        ).pack()

        bLabel = tk.Label(color_win, text=f"BLUE | Current: {self.RGB_Pri[2]}")
        bLabel.pack()
        tk.Scale(color_win, from_=0, to=255, orient="horizontal", variable=b, command=lambda val: 
            (
                self.set_B_primary(int(val)), 
                color_button.config(bg=self.from_rgb((tuple(self.RGB_Pri)))),
                bLabel.config(text=f"BLUE | Current: {val}")
            )
        ).pack()

    def update_label(self):
            self.range_var.set(f"{self.km_range} KM")
            self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img_{self.km_range}.png")
            if os.path.isfile(self.img_compas):
                self.overlay = Image.open(self.img_compas).convert("RGBA")
            
            # hh:mm:ss  DD-MM-YYYY
            local_DT = time.localtime()

            self.time.config(
                text=f"{self.set_2digit(local_DT.tm_hour)}:"
                    f"{self.set_2digit(local_DT.tm_min)}:"
                    f"{self.set_2digit(local_DT.tm_sec)} | "
                    f"{self.set_2digit(local_DT.tm_mday)}-"
                    f"{self.set_2digit(local_DT.tm_mon)}-"
                    f"{self.set_2digit(local_DT.tm_year)}",
                bg=self.secondary_color
            )
        
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
        self.window.after(0, self.update_image)
    
    def update_image(self):

        if not os.path.isfile(self.img_loc):
            return

        try:
            base = Image.open(self.img_loc).convert("RGBA")
            # if os.path.isfile(self.img_compas):
            #     overlay = Image.open(self.img_compas).convert("RGBA")
            if self.overlay is not None:
                if self.overlay.size != base.size:
                    self.overlay = self.overlay.resize(base.size, Image.Resampling.LANCZOS)
                
                base = Image.alpha_composite(base, self.overlay)

            # Convert to Tk image
            img = ImageTk.PhotoImage(base, master=self.window)

            # Save reference
            self.composite = img

            # Update label
            self.image_label.configure(image=self.composite, relief='solid')
        except Exception as e:
            print("Radar reload failed:")
            print(e)

    def style_manager(self):
        pass