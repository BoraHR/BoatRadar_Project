# https://www.geeksforgeeks.org/python/python-gui-tkinter/
from tkinter import *
import tkinter as tk
from tkinter import ttk
from functools import partial

import numpy as np
from RadarPlotter import RadarPlotter
import os, shutil
from PIL import Image, ImageTk, ImageDraw
import time
import winsound
from Algorithm import km_to_miles, decimal_to_ddm

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
    def __init__(self, window, testMode = False):
        self.IsDark = False
        self.plotter = RadarPlotter()
        if testMode:
            self.plotter = RadarPlotter(True)
        
        # RED == self.RGB_{Pri/Sec/Ter}[0]
        # GREEN == self.RGB_{Pri/Sec/Ter}[1]
        # BLUE == self.RGB_{Pri/Sec/Ter}[2]
        # MIN 0, MAX 255

        # -- Primary Colors -- #
        self.RGB_Pri = [144,144,144]
        
        # -- Secondary Colors -- #
        self.RGB_Sec = [141,199,130]

        # -- Tertiary Colors -- #
        self.RGB_Ter = [127,158,128]
        
        self.plotter.draw.setBGColor_RGB(self.RGB_Pri[0], self.RGB_Pri[1], self.RGB_Pri[2])

        self.IsRelativeHeading = False
        self.IsFullscreen = True

        # -- Name Conversion for thinker colorscheme -- #
        self.primary_color = self.from_rgb(tuple(self.RGB_Pri))
        self.secondary_color = self.from_rgb(tuple(self.RGB_Sec))
        self.tertiary_color = self.from_rgb(tuple(self.RGB_Ter))

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.killswitch = False
        self.myBoat = self.get_boat_data(self.plotter.ID)
        self.Rotation = self.myBoat[7]
        
        self.window = window
        self.testMode = testMode
        if not testMode:
            self.window.title("AIS Radar Console")
            self.window.attributes('-fullscreen', True)

            # ---- STARTNG STATES ---- #
            self.boat_id = self.plotter.ID # Boat ID is assinged ID of your boat.
            self.km_range = 3 # Startig Unit for Radar generation.
            self.time_window = 10 # The window of time to consider plotting to be valid.

            # ---- Directories for image loading and saving ----
            self.img_guide = os.path.join(self.BASE_DIR, f"Radar/Guide/Console_Guide.png")
            self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img.png") # updates in update_image()
            self.img_compas = os.path.join(self.BASE_DIR, f"Radar/Compas/Current/360_Rotation-TranparantCenter.png")
            self.alarm = os.path.join(self.BASE_DIR, f"Sounds/Alarm.WAV")
            self.help_image = None
            try:
                self.help_image = ImageTk.PhotoImage(Image.open(self.img_guide))
            except Exception as e:
                print(f"Error loading HelpGuideImg:\n{e}")

            # https://www.tutorialspoint.com/article/keyboard-shortcuts-with-tkinter-in-python-3#:~:text=Tkinter%20provides%20built-in%20functionality,when%20the%20shortcut%20is%20triggered.
            self.window.bind('<F1>', self.open_help_window)

            # ---- UI ----
            self.range_var = StringVar(self.window)
            
            # ---- MENU BAR ----
            self.menu_bar = tk.Menu(self.window)
            # self.conf_Menubar()

            # -- UI layer system -- #
            self.window.columnconfigure(0, weight=1)  # left
            self.window.columnconfigure(1, weight=1)  # center
            self.window.columnconfigure(2, weight=1)  # right
            self.window.rowconfigure(0, weight=1)

            # LEFT
            self.left_frame = Frame(window)
            self.left_frame.grid(row=0, column=0, sticky="nsew")
            self.left_frame.rowconfigure(1, weight=1)
            self.left_frame.columnconfigure(0, weight=1)
            self.left_frame.columnconfigure(1, weight=1)
            self.left_frame.columnconfigure(2, weight=1)
            self.left_frame.columnconfigure(3, weight=1)
            # CENTER
            self.center_frame = Frame(window)
            self.center_frame.grid(row=0, column=1, sticky="nsew")
            self.center_frame.rowconfigure(0, weight=1)
            self.center_frame.columnconfigure(0, weight=1)
            # RIGHT
            self.right_frame = Frame(window)
            self.right_frame.grid(row=0, column=2, sticky="nsew")
            self.right_frame.rowconfigure(1, weight=1)
            self.right_frame.columnconfigure(0, weight=1)
            self.top_frame = Frame(self.right_frame)
            # RIGHT NESTED
            self.top_frame.grid(row=0, column=0, sticky="ew")
            self.top_frame.columnconfigure(0, weight=1)
            self.top_frame.columnconfigure(1, weight=1)
            self.top_frame.columnconfigure(2, weight=1)
            self.top_frame.columnconfigure(3, weight=1)

            # ---- radar image ----
            # Create a canvas that can display the rendered radar image and clickable
            # hotspots for each plotted target.
            self.image = None
            self.overlay = None
            self.composite = None
            self.image_label = tk.Canvas(self.center_frame, width=750, height=750, highlightthickness=0, bd=0)
            self.image_help = tk.Label()
            self.image_item_id = None
            self.image_label.bind("<Button-1>", self.on_radar_click)

            # display
            self.unitInfo = Label(self.left_frame,
                text="Radar Range",
                font=("Consolas", 14))#.pack(pady=(10, 0))

            self.unit = Button(self.left_frame,
                textvariable=self.range_var,
                font=("Consolas", 16, "bold"),
                command=self.plotter.toggleUnit,
                bg=self.primary_color,
                relief=RAISED
            )#.pack(pady=(10, 0))

            self.KM_prev = Button(self.left_frame,
                text="<",
                width=3,
                font=("Consolas", 16),
                command=lambda: self.change_range(-1),
                bg=self.secondary_color
            )#.pack(side=LEFT, padx=5)

            self.KM_next = Button(self.left_frame,
                text=">",
                width=3,
                font=("Consolas", 16),
                command=lambda: self.change_range(+1),
                bg=self.secondary_color
            )#.pack(side=LEFT, padx=5)

            self.Theme = Button(self.left_frame,
                text="SUN",
                width=3,
                font=("Consolas", 16),
                command=self.toggle_theme,
                bg=self.secondary_color
            )

            self.Help = Button(self.left_frame,
                text="HELP",
                width=3,
                font=("Consolas", 16),
                command=self.open_help_window,
                bg=self.secondary_color
            )

            self.turtle_togle = Button(self.center_frame,
                text="HIDE DRAWER",
                font=("Consolas", 14),
                bg=self.secondary_color,
                command=self.plotter.draw.screen_toggle,
            )#.pack(pady=10)

            self.myLat = self.myBoat[9]
            self.myLon = self.myBoat[10]
            self.mySpeed = self.myBoat[7]
            self.myHeading = self.myBoat[12]

            self.latLabel = Label(self.top_frame,
                text=f"LAT",
                font=("Consolas", 20, "bold"),
                bg=self.tertiary_color,
                relief=RAISED
            )
            self.latDisplay = Label(self.top_frame,
                text=f"{decimal_to_ddm(self.myLat, "lat")}",
                font=("Consolas", 20, "bold"),
                bg=self.secondary_color,
                relief=RAISED
            )

            self.lonLabel = Label(self.top_frame,
                text=f"LON",
                font=("Consolas", 20, "bold"),
                bg=self.tertiary_color,
                relief=RAISED
            )
            self.lonDisplay = Label(self.top_frame,
                text=f"{decimal_to_ddm(self.myLon, "lon")}",
                font=("Consolas", 20, "bold"),
                bg=self.secondary_color,
                relief=RAISED
            )

            

            self.speedLabel = Label(self.top_frame,
                text=f"STW",
                font=("Consolas", 20, "bold"),
                bg=self.tertiary_color,
                relief=RAISED
            )
            self.speedDisplay = Label(self.top_frame,
                text=f"{self.mySpeed} kn",
                font=("Consolas", 20, "bold"),
                bg=self.secondary_color,
                relief=RAISED
            )

            self.headingLabel = Label(self.top_frame,
                text=f"HDG",
                font=("Consolas", 20, "bold"),
                bg=self.tertiary_color,
                relief=RAISED
            )
            self.headingDisplay = Label(self.top_frame,
                text=f"{self.heading_string_format()}",
                font=("Consolas", 20, "bold"),
                bg=self.secondary_color,
                relief=RAISED
            )
            self.table = ttk.Treeview(self.right_frame, columns=("ID", "Mmsi", "Range", "CPA", "TCPA", "BRG", "BoatID"), show="headings", height=10)

            self.table.heading("ID", text="ID")
            self.table.heading("Mmsi", text="Mmsi")
            self.table.heading("Range", text="KM")
            self.table.heading("CPA", text="CPA (m)")
            self.table.heading("TCPA", text="TCPA (s)")
            self.table.heading("BRG", text="T_BRG")
            self.table.heading("BoatID", text="BoatID")
            # Set column widths and prevent resizing
            self.table.column("ID", width=50, stretch=False)
            self.table.column("Mmsi", width=80, stretch=False)
            self.table.column("Range", width=60, stretch=False)
            self.table.column("CPA", width=80, stretch=False)
            self.table.column("TCPA", width=80, stretch=False)
            self.table.column("BRG", width=80, stretch=False)
            self.table.column("BRG", width=80, stretch=False)

            self.table.bind("<<TreeviewSelect>>", self.setTarget)

            # details tree for selected target
            self.details_tree = ttk.Treeview(
                self.right_frame,
                columns=("field", "value"),
                show="headings",
                height=1
            )
            self.details_tree.heading("field", text="Field")
            self.details_tree.heading("value", text="Value")
            self.details_tree.column("field", width=120, stretch=False)
            self.details_tree.column("value", width=220, stretch=True)

            # self.table.configure(height=10)

            # self.table.pack(side=TOP, padx=20, pady=20)
            
            # Create a Combobox widget for option selection
            self.combo_box = ttk.Combobox(
                self.right_frame,
                values=["RANGE", "CPA", "TCPA"],
                state="readonly"
            )

            self.combo_box.bind("<<ComboboxSelected>>", self.on_select)

            # self.combo_box.pack(side=BOTTOM, padx=5, pady=2)
            self.combo_box.set("RANGE")
                        
            local_DT = time.localtime()

            # hh:mm:ss  DD-MM-YYYY
            self.time = Label(self.right_frame,
                text=f"{self.set_2digit(local_DT.tm_hour)}:{self.set_2digit(local_DT.tm_min)}:{self.set_2digit(local_DT.tm_sec)}|{self.set_2digit(local_DT.tm_mday)}-{self.set_2digit(local_DT.tm_mon)}-{self.set_2digit(local_DT.tm_year)}",
                font=("Consolas", 20, "bold"),
                bg=self.secondary_color,
                relief=SUNKEN
            )
        
            self.style = ttk.Style(window)
            # -- generate UI -- #
            self.conf_Menubar()
            self.update_image()
            self.conf_LeftFrame()
            self.conf_CenterFrame()
            self.conf_RightFrame()
            self.apply_light_theme()
            self.radar_loop()
            self.Rot = 0

    def current_range_km(self):
        return self.km_range if self.plotter.IsKM else self.km_range * 1.609344

    def current_unit_label(self):
        return f"{self.km_range}KM" if self.plotter.IsKM else f"{self.km_range}MI"

    def convert_display_distance(self, km_distance):
        return km_distance if self.plotter.IsKM else km_distance * 0.621371

    def conf_Menubar(self):
        # File menu - TEMPLATE
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Hide/Show Turtle", command=self.plotter.draw.screen_toggle)
        file_menu.add_command(label="Render Reselution Config", command=self.open_resulotion_window)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.Quit)

        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Help menu - TEMPLATE
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.open_help_window)

        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        setting_menu  = tk.Menu(self.menu_bar, tearoff=0)
        setting_menu.add_command(label="Color Settings", command=self.open_color_window)
        setting_menu.add_command(label="DEBUG_mode (DEV Only)", command=self.toggle_print)
        setting_menu.add_command(label="Fullscreen toggle", command=self.toggle_fullscreen)
        
        self.menu_bar.add_cascade(label="settings", menu=setting_menu)

        # Attach menu bar to window
        self.window.config(menu=self.menu_bar)

    def conf_LeftFrame(self):
        # self.unitInfo.grid(row=0, column=0)
        self.KM_prev.grid(row=0, column=0, sticky="e", padx= (10,0), pady=(20,0))
        self.unit.grid(row=0, column=1, sticky="ew", pady=(20,0))
        self.KM_next.grid(row=0, column=2, sticky="w", pady=(20,0))
        self.Theme.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(10,0)
        )
        self.Help.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(10,10)
        )

    def conf_CenterFrame(self):
        self.image_label.config(width=780, height=755)
        self.image_label.grid(row=0, column=0, sticky="n", padx=10)

    def conf_RightFrame(self):
        # Top frame for speed + heading
        self.right_frame.rowconfigure(1, weight=1)  # table expands
        self.right_frame.columnconfigure(0, weight=1)

        # Speed
        self.speedLabel.grid(row=0, column=0, sticky="ew", padx=(10,0), pady=(10,0))
        self.speedDisplay.grid(row=0, column=1, sticky="ew", padx=(0,0), pady=(10,0))

        # Heading
        self.headingLabel.grid(row=1, column=0, sticky="ew", padx=(10,0), pady=(0,10))
        self.headingDisplay.grid(row=1, column=1, sticky="ew", padx=(0,0), pady=(0,10))

        # Latitude
        self.latLabel.grid(row=0, column=2, sticky="ew", padx=(0,0), pady=(10,0))
        self.latDisplay.grid(row=0, column=3, sticky="ew", padx=(0,10), pady=(10,0))

        # Longitude
        self.lonLabel.grid(row=1, column=2, sticky="ew", padx=(0,0), pady=(0,10))
        self.lonDisplay.grid(row=1, column=3, sticky="ew", padx=(0,10), pady=(0,10))

        # Table (takes all remaining space)
        self.table.grid(row=1, column=0, sticky="nsew", padx=10)
        self.right_frame.rowconfigure(2, weight=0)

        # Detailed target data
        self.details_tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 0))

        # Bottom controls
        self.combo_box.grid(row=3, column=0, pady=5)
        self.time.grid(row=4, column=0, pady=5)


    # -- Radar loop updates plotting device every second -- #
    # NOTE: Image saving is now asynchronous - SaveImg() returns immediately
    # and processes heavy image operations in a background thread.
    # This keeps the GUI responsive while data refreshes.
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

        # run again after 100 ms'
        if self.window.winfo_exists():
            self.window.after(100, self.radar_loop)
        end = time.time()
        print(f"Loop performance: {end - start}")
        
    def Quit(self):
        self.killswitch = True
        print("Closing program...")
        self.plotter.conn.close()
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
                if "." not in folder:
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
            boat, number, distance, cpa, tcpa, consoleData, brg = entry
            if tcpa > -0.5 and tcpa < 0.5:
                winsound.PlaySound(self.alarm, winsound.SND_FILENAME | winsound.SND_ASYNC)
            string_distance = f"{distance:.2f} km"
            if not self.plotter.IsKM:
                string_distance = f"{km_to_miles(distance):.2f} mi"

            self.table.insert("", "end", values=(
                number,
                boat[4], # Mmsi
                f"{string_distance}",
                f"{cpa:.1f}",
                f"{tcpa:.1f}",
                f"{brg:.0f}°",
                boat[0]  # BoatId
            ))

        # Fill remaining rows with empty placeholders
        remaining = 10 - len(self.plotter.RadarConsoleData)
        for _ in range(max(0, remaining)):
            self.table.insert("", "end", values=("", "", "", "", "", ""))

        # Update target detail display after table refresh
        self.update_target_details()

    def get_boat_data(self, id):
        return self.plotter.GetBoat(id)

    def update_target_details(self):
        # Clear the previous details
        for row in self.details_tree.get_children():
            self.details_tree.delete(row)

        target_id = self.plotter.targetId
        if target_id == -1:
            self.details_tree.config(height=1)
            self.details_tree.insert("", "end", values=("Target", "No target selected"))
            return

        # Find the selected target in the current radar data
        target_entry = next(
            (entry for entry in self.plotter.RadarConsoleData if entry[0][0] == target_id),
            None
        )

        if target_entry is None:
            self.details_tree.config(height=1)
            self.details_tree.insert("", "end", values=("Target", "Selected target not in current range"))
            return

        
        self.details_tree.config(height=13)
        boat, number, distance, cpa, tcpa, consoleData, brg = target_entry
        string_distance = f"{distance:.2f} km"
        if not self.plotter.IsKM:
            string_distance = f"{km_to_miles(distance):.2f} mi"
        details = [
            ("Boat ID", boat[0]),
            ("MMSI", boat[4]),
            ("Status", boat[5]),
            ("Latitude", f"{decimal_to_ddm(boat[10], "lat")}" if boat[10] is not None else ""),
            ("Longitude", f"{decimal_to_ddm(boat[9], "lon")}" if boat[9] is not None else ""),
            ("Speed", f"{boat[7]:.2f}"),
            ("Course", f"{boat[11]:.1f}"),
            ("Heading", f"{boat[12]:.1f}"),
            ("Distance", f"{string_distance}"),
            ("CPA", f"{cpa:.1f} m"),
            ("TCPA", f"{tcpa:.1f} s"),
            ("T_BRG", f"{brg:.0f}°"),
            ("Last AIS", boat[1])
        ]

        for field, value in details:
            self.details_tree.insert("", "end", values=(field, value))

    def open_help_window(self, event=None):
        help_win = tk.Toplevel(self.window)
        help_win.title("Help")
        try:
            image = Image.open(self.img_guide)
            

            screen_w = help_win.winfo_screenwidth()
            screen_h = help_win.winfo_screenheight()

            max_w = int(screen_w * 0.5)   # 80% of screen width
            max_h = int(screen_h * 0.5)   # 80% of screen height

            image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image, master=help_win)
            guide = tk.Label(help_win, image=photo)
            guide.image = photo # keep reference
            guide.pack()

            guide_text = tk.Label(
                help_win, 
                text = "1. Lower radar range by 1 (MIN 1)\n2. Unit display pressing it will toggle between KM and Mile\n3. extend radar range by 1 (MAX 12)\n4. Toggle between SUN and DARK theme ussefull setting depending on time of day\n5. Opens this guide\n6. Radar displays the fellowing:\n\t○ Green arrow is your own boat always located in center of the radar\n\t○ Red arrow indicates dengerously low TCPA between the marked target and your boat\n\t○ aqua (violet for dark) arrows is the selected target for for detailed overview, this will override the danger indicator so be allert when hearing alarms\n\t○ Black arrows are the boats caught in your configured radar range\n\t○ Each boat has assinged ID this can change depending on selected ENUM order, the assigned ID can get shuffled during order changes so you might want to track boat in detail target overview to preffent confusion\n\t○ The line drawn per plotted ellement (including self) will show the direction and predicted positioning depending on speed, it can be served aa helper for predicting CPA/TCPA overtime for mannual planning\n7. Current speed of your boat and latitude position \n8. Current heading of your boat and lonitude position\n9. Boats caugth in configured range, you can sellect, deselect or swith target by clicking on a row\n10. detailed information of selected target it will remain tracked if target is outside configured range until unselected or switched on the radar taget apears in aqua color (violet in darkmode)\n11. an ENUM config it will change the order depending on selected type to order\n12. Systemtime might not appear if hardware bugs are pressent or no time tracking in system",
                justify="left",
                anchor="w"  
            )
            guide_text.pack()
        except Exception as e:
            print(f"Error in 'Help' top level window:\n{e}\n")

    def open_resulotion_window(self):
        resulotion_win = tk.Toplevel(self.window)
        resulotion_win.title("Thinker resolution config")

        # Label (optional)
        tk.Label(resulotion_win, text="Enter resolution:").pack()

        # Input field
        entry = tk.Entry(resulotion_win)
        entry.pack()
        tk.Button(resulotion_win, text="Confirm", command=lambda: self.plotter.draw.set_reselution(entry.get())).pack()

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
        self.range_var.set(self.current_unit_label())
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img.png")
        if os.path.isfile(self.img_compas):
            self.overlay = Image.open(self.img_compas).convert("RGBA")
        
        # hh:mm:ss  DD-MM-YYYY
        local_DT = time.localtime()

        if self.km_range <= 1:
            self.KM_prev.config(
                bg="gray",
                relief=SUNKEN,
                state=DISABLED
            )
        else:
            self.KM_prev.config(
                bg=self.secondary_color,
                relief=RAISED,
                state=NORMAL
            )

        if self.km_range >= 12:
            self.KM_next.config(
                bg="gray",
                relief=SUNKEN,
                state=DISABLED
            )
        else:
            self.KM_next.config(
                bg=self.secondary_color,
                relief=RAISED,
                state=NORMAL
            )


        self.time.config(
            text=f"{self.set_2digit(local_DT.tm_hour)}:"
                f"{self.set_2digit(local_DT.tm_min)}:"
                f"{self.set_2digit(local_DT.tm_sec)}|"
                f"{self.set_2digit(local_DT.tm_mday)}-"
                f"{self.set_2digit(local_DT.tm_mon)}-"
                f"{self.set_2digit(local_DT.tm_year)}",
            bg=self.secondary_color
        )


    def heading_string_format(self):
        strHeading = str(round(self.myHeading))
        while len(strHeading) < 3:
            strHeading = "0" + strHeading
        return strHeading + "°"
        
    def change_range(self, delta):
        self.km_range += delta

        if self.km_range < 1:
            self.km_range = 1
        if self.km_range > 12:
            self.km_range = 12

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

        if not self.plotter.draw.img_RAM:
            print("Image load failed: Image is NONE refrence. Aboarting img reading")
            print()
            return

        try:
            base = self.plotter.draw.img_RAM.convert("RGBA")
            base = base.resize((750, 750), Image.Resampling.LANCZOS)
            # self.Rotation = (self.Rotation + 1) % 360
            # if os.path.isfile(self.img_compas):
            #     overlay = Image.open(self.img_compas).convert("RGBA")
            if self.overlay is not None:
                if self.overlay.size != base.size:
                    if self.IsRelativeHeading:
                        # THIS CONDITION IS NOT IMPLEMENTED YET
                        self.overlay = self.overlay.rotate(self.myHeading)
                    self.overlay = self.overlay.resize(base.size, Image.Resampling.LANCZOS)

                offset_x = 0 # to allign with compas
                offset_y = -2 # to allign with compas
                shifted_base = Image.new("RGBA", base.size, (0, 0, 0, 0))
                shifted_base.paste(base, (offset_x, offset_y), base)

                base = Image.alpha_composite(shifted_base, self.overlay)

                # Create a circular alpha mask so the image appears round.
                mask = Image.new("L", base.size, 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, base.size[0], base.size[1]], fill=255)
                base.putalpha(mask)

            # Convert to Tk image
            img = ImageTk.PhotoImage(base, master=self.window)
            
            # Save reference
            self.composite = img
            # self.image_label.configure(image=self.composite, relief='solid')
            if self.image_item_id is None:
                self.image_item_id = self.image_label.create_image(0, 0, anchor="nw")
            self.image_label.itemconfigure(self.image_item_id, image=self.composite)
            self.image_label.coords(self.image_item_id, 0, 0)
            self.image_label.delete("radar_hotspot")
            self._draw_radar_hotspots()
        except Exception as e:
            print("Radar reload failed:")
            print(e)

    def _draw_radar_hotspots(self):
        for entry in self.plotter.RadarConsoleData:
            boat, number, distance, cpa, tcpa, consoleData, brg = entry
            if not consoleData:
                continue

            boat_id = boat[0]
            x_meters = consoleData[1]
            y_meters = consoleData[2]
            scale = consoleData[4]

            if scale is None or scale <= 0:
                continue

            x_px = x_meters * scale
            y_px = y_meters * scale

            # Note: devide might need to be ajusted when changing resulotion of the image, 
            # 300 for image of 750x750 might need to use calculation for consistency.
            devide = 300 
            display_x = 375 + (x_px / devide) * 375
            display_y = 375 - (y_px / devide) * 375

            # HS_radius:
            # the hotspot size bigger values has more coverage but bigger chance targets overlap each other when very close together, 
            # small values makes it harder to predict where tatget can be clicked on the radar but minimizes overlapping with other targets.
            # a middle ground between 15 - 20 recomended, use outline and/or fill see hotspot location and size, use empty ("") to make the invisible.
            # overlapping prioritizes highest id.
            HS_radius = 20
            hotspot = self.image_label.create_oval(
                display_x - HS_radius,
                display_y - HS_radius,
                display_x + HS_radius,
                display_y + HS_radius,
                outline="", # give color of choice for debugging ("pink" recomended) 
                fill="", # give color of choice for debuggin ("gold" recomended) 
                tags=("radar_hotspot", str(boat_id))
            )
            self.image_label.tag_bind(hotspot, "<Button-1>", lambda event, boat_id=boat_id: self.select_target(boat_id))

    def on_radar_click(self, event):
        return

    def on_select(self, event):
        selected_value = self.combo_box.get()
        print(f"Selected: {selected_value}")
        self.plotter.setEnum(selected_value)

    def select_target(self, boat_id):
        try:
            self.plotter.setTarget(int(boat_id))
            self.refresh_selection_visuals()
        except Exception as e:
            print("Error selecting radar target:")
            print(e)

    def refresh_selection_visuals(self):
        try:
            self.plotter.draw.clear_otherBoats()
            self.plotter.plot_boats(self.plotter.GetBoat(self.boat_id))
            self.plotter.draw.SaveImg()
        except Exception as e:
            print("Failed to redraw radar selection:")
            print(e)

        self.update_target_details()
        self.update_image()

    def setTarget(self, event):
        boats = self.table.selection()
        if boats == None or len(boats) == 0:
            return
        
        boat = boats[0]
        values = self.table.item(boat, "values")
        
        if not values[0]:  # skip empty placeholder rows
            return
        
        boat_id = int(values[6])
        self.select_target(int(boat_id))
        # if self.plotter.targetId == int(boat_id):
        #     self.plotter.targetId = -1
        #     return
        # self.plotter.targetId = int(boat_id)
        
    def clearTarget(self):
        self.plotter.targetId = -1
        
    def style_manager(self):
        pass

    def toggle_print(self):
        self.plotter.toglePrint()

    def toggle_theme(self):
        if self.IsDark:
            self.Theme.configure(text="SUN")
            self.set_R_primary(144)
            self.set_G_primary(144)
            self.set_B_primary(144)

            self.set_R_secondary(141)
            self.set_G_secondary(199)
            self.set_B_secondary(130)

            self.set_R_tertiary(127)
            self.set_G_tertiary(158)
            self.set_B_tertiary(128)
            self.plotter.draw.setBGColor_RGB(self.RGB_Pri[0], self.RGB_Pri[1], self.RGB_Pri[2])
            self.IsDark = False
            self.plotter.draw.IsDark = False # to indentify drawer to change cirkel lines and crosshair style
            self.img_compas = os.path.join(self.BASE_DIR, f"Radar/Compas/Current/360_Rotation-TranparantCenter.png")
            self.update_UI_colorscheme()
            self.apply_light_theme()
        
        else:
            self.Theme.configure(text="DARK")
            self.set_R_primary(0)
            self.set_G_primary(23)
            self.set_B_primary(68)

            self.set_R_secondary(91)
            self.set_G_secondary(149)
            self.set_B_secondary(70)

            self.set_R_tertiary(77)
            self.set_G_tertiary(108)
            self.set_B_tertiary(78)
            self.plotter.draw.setBGColor_RGB(self.RGB_Pri[0], self.RGB_Pri[1], self.RGB_Pri[2])
            self.IsDark = True
            self.plotter.draw.IsDark = True
            self.img_compas = os.path.join(self.BASE_DIR, f"Radar/Compas/Current/360_Rotation-TranparantCenter_Dark.png")
            self.update_UI_colorscheme()
            self.apply_dark_theme()

        self.sync_draw_background()
        self.plotter.draw.KM_build = -1 # ensures clearing radar cache to redraw for theme switch

    def sync_draw_background(self):
        self.plotter.draw.setBGColor_RGB(
            self.RGB_Pri[0],
            self.RGB_Pri[1],
            self.RGB_Pri[2]
        )
        self.plotter.draw.SaveImg()
        self.update_image()

    def toggle_fullscreen(self):
        if self.IsFullscreen:
            self.window.attributes('-fullscreen', False)
            self.IsFullscreen = False
        else:
            self.window.attributes('-fullscreen', True)
            self.IsFullscreen = True

    def update_UI_colorscheme(self):
        self.primary_color = self.from_rgb(tuple(self.RGB_Pri))
        self.secondary_color = self.from_rgb(tuple(self.RGB_Sec))
        self.tertiary_color = self.from_rgb(tuple(self.RGB_Ter))
        # --- Primary update --
        if self.IsDark:
            self.unit.configure(bg=self.primary_color, fg="Silver")
        else:
            self.unit.configure(bg=self.primary_color, fg="black")

        # --- Secondary update --
        sec_set = [self.Theme, self.Help, self.headingDisplay, self.speedDisplay, self.latDisplay, self.lonDisplay, self.KM_prev, self.KM_next]
        for secVar in sec_set:
            secVar.configure(bg=self.secondary_color)

        # --- tertialy update --
        ter_set = [self.speedLabel, self.headingLabel, self.latLabel, self.lonLabel]
        for terVar in ter_set:
            terVar.configure(bg=self.tertiary_color)
        
    def apply_dark_theme(self):
        self.style.theme_use("clam")
        self.style.configure(
            "Dark.Treeview",
            background="#262626",
            fieldbackground="#262626",
            foreground="limegreen",
            rowheight=25,
            bordercolor="#262626",
            borderwidth=0
        )
        self.style.configure(
            "Dark.Treeview.Heading",
            background="#333333",
            foreground="limegreen",
            relief="flat"
        )
        self.style.map(
            "Dark.Treeview.Heading",
            background=[
                ("active", "#3a3a3a"),   # hover
                ("pressed", "#1f1f1f")   # click
            ],
            foreground=[
                ("active", "green"),
                ("pressed", "#66ff66")
            ],
            relief=[
                ("pressed", "sunken"),
                ("active", "flat")
            ]
        )
        self.style.map(
            "Dark.Treeview",
            background=[("selected", "#226723")],
            bordercolor="#262626",
            foreground=[("selected", "black")]

        )

        self.style.configure(
            "TCombobox",
            fieldbackground="#262626",   # inside text area
            background="#262626",
            bordercolor="#2A2A2A",        # button area
            foreground="black",
            arrowcolor="white",
        )

        set1=[self.left_frame, self.center_frame, self.right_frame, self.top_frame]
        for widget in set1:
            widget.configure(bg='#1e1e1e')

        set2=[self.details_tree, self.table]
        for tree in set2:
            tree.configure(style="Dark.Treeview")
        
        self.menu_bar.configure(bg="#262626")
        self.image_label.configure(bg=self.tertiary_color)
        self.combo_box.configure(style="TCombobox")

    def apply_light_theme(self):
        self.style.theme_use("clam")
        self.style.configure(
            "Light.Treeview",
            background='#FFFFFF',
            fieldbackground='#FFFFFF',
            foreground="black",
            rowheight=25,
            bordercolor="#d9d9d9",
            borderwidth=0
        )
        self.style.configure(
            "Light.Treeview.Heading",
            background="#f0f0f0",
            foreground="black",
            relief="flat"
        )
        self.style.map(
            "Light.Treeview",
            background=[("selected", "#cce4ff")],
            foreground=[("selected", "black")]
        )

        self.style.configure(
            "TCombobox",
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            boardercolor="#d9d9d9",
            foreground="black",
            arrowcolor="black"
        )

        set1=[self.left_frame, self.center_frame, self.right_frame, self.top_frame]
        for widget in set1:
            widget.configure(bg='#F0F0F0')

        set2=[self.details_tree, self.table]
        for tree in set2:
            tree.configure(style="Light.Treeview")
        
        self.menu_bar.configure(bg='#FFFFFF')
        self.image_label.configure(bg=self.tertiary_color)
        self.combo_box.configure(style="TCombobox")