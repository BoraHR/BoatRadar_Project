import turtle
import math
import os
# https://www.geeksforgeeks.org/python/python-pillow-colors-on-an-image/
from PIL import Image
import time
import threading
from Algorithm import calculate_cpa_tcpa, miles_to_km

screen = turtle.Screen()
resulotionScale = 612
screen.setup(width=resulotionScale, height=resulotionScale)
# turtle.bgpic(os.path.dirname(os.path.abspath(__file__)) + "/WorldWideMap_big.png")

screen.tracer(0)

radar_t = turtle.Turtle(visible=False)
radar_t.speed(0)

boats_t = turtle.Turtle(visible=False)
boats_t.speed(0)

class RadarDrawing:
    def __init__(self):
        # radar_built = False
        
        self.hideScreen = False
        self.KM_build = -1
        self.plotedBoats = []
        self.RGB = (255,255,255)
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.bg_loc = os.path.join(self.BASE_DIR, f"Radar/Background/R={self.RGB[0]},G={self.RGB[1]},B={self.RGB[2]}")
        self.ps_loc = os.path.join(self.BASE_DIR, f"Radar/PostScript/drawing.ps")
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img.png")
        self.ps_RAM = None
        self.img_RAM = None
        # Threading for async image saves
        self._save_thread = None
        self._save_lock = threading.Lock()

    def set_reselution(self, res):
        try:
            resulotionScale = int(res)
            screen.setup(width=resulotionScale, height=resulotionScale)
        except (TypeError, ValueError):
            print(f"Invalid resolution value: {res}")
            return
        
        
    # KM the amount of lines represent keep in mind it must be an int.
    def draw_radar_Custom(self, KM, heading, speed, IsKM=True):
        # screen.bgcolor(float(self.RGB[0]/255), float(self.RGB[1]/255), float(self.RGB[2]/255))
        start = time.time()
        if not IsKM:
            KM = round(miles_to_km(KM)) # round to prefent float in-accuracy       
        if KM < 1:
            KM = 1
        self.KM_build
        if self.KM_build == KM:
            end = time.time()
            return end - start

        radar_t.clear()
        KM = int(math.ceil(KM))

        radius_list = [250]

        multiplier = 0
        multiplier += KM
        while(multiplier >= 1):
            multiplier -= 1
            radius_list.append((250/KM) * multiplier)
        
        radius_list.reverse()
        radar_t.color("darkgray")
        for r in radius_list:
            radar_t.penup()
            radar_t.goto(0, -r)
            radar_t.pendown()
            radar_t.circle(r)
        self.draw_crosshair(radius_list[-1])
        # radar_t.write(str(KM), align="center", font=("Consolas", 16, "bold"))
        self.plot_myBoat(heading, speed, KM)
        end = time.time()
        self.KM_build = KM
        return end - start # returns the a time it took to create the img in seconds.
    
    def setBGColor_RGB(self, R, G, B):
        R = self.hexRangeCheck(R) 
        G = self.hexRangeCheck(G)
        B = self.hexRangeCheck(B)
        screen.update()
        # store it memory for config settings
        try:
            self.RGB = (R, G, B)
            screen.bgcolor(float(R/255), float(G/255), float(B/255))
        except Exception as e:
            print("Error setting render color:")
            print(e)

    def hexRangeCheck(self, hex):
        if hex < 0:
            return 0
        if hex > 255:
            return 255 
        return hex

    def draw_crosshair(self, range):
        max_radius = range
        radar_t.penup()
        radar_t.goto(-max_radius, 0)
        radar_t.pendown()
        radar_t.goto(max_radius, 0)  # horizontal line

        radar_t.penup()
        radar_t.goto(0, -max_radius)
        radar_t.pendown()
        radar_t.goto(0, max_radius)  # vertical line

    def clear_otherBoats(self):
        # if the canvas has already been closed (e.g. after a SaveImg() call)
        # the turtle module will raise a TclError/TurtleGraphicsError.
        # We catch it here and simply ignore it – the next draw operation will
        # either recreate the screen or fail later if not recreated.
        try:
            boats_t.clear()
        except Exception:
            # screen or turtle may have been destroyed; nothing we can do now
            pass

    def plot_otherBoat_dot(self, x_meters, y_meters, scale=0.050, IsTarget = False):
        px = x_meters * scale
        py = y_meters * scale

        boats_t.penup()
        boats_t.goto(px, py) # px(x): ←→  py(y): ↑↓
        if(IsTarget):
            boats_t.color("orange")
        else:
            boats_t.color("red")

    def plot_otherBoat(self, myBoat, boatToSave, x_meters, y_meters, number, scale=0.050, heading=0.00, IsTarget = False):
        cpa, tcpa = calculate_cpa_tcpa(
            0, 0, myBoat[7], myBoat[12],
            x_meters, y_meters, boatToSave[7], boatToSave[12]
        )
        px = x_meters * scale
        py = y_meters * scale
        self.plotedBoats.append((boatToSave, x_meters, y_meters))
        if heading is None or heading >= 360 or heading < 0:
            self.plot_otherBoat_dot(x_meters, y_meters, scale, IsTarget)
            return
        # heading += 90
        heading = heading % 360 # fail save 
        
        boats_t.penup()
        boats_t.goto(px, py) # px(x): ←→  py(y): ↑↓
        boats_t.shape("arrow")
        W_L = 0.50
        boats_t.shapesize(W_L, W_L*4.0)
        if(IsTarget):
            boats_t.color("aqua")
        elif tcpa > -0.5 and tcpa < 0.5:
            boats_t.color("red")
        else:
            boats_t.color("black")
        boats_t.setheading(90 - heading)
        boats_t.back(10)
        boats_t.stamp()
        boats_t.forward(10)
        boats_t.color("yellow")
        boats_t.penup()
        vector_length = 0
        try:
            if boatToSave[7] > 0.00:
                speed = boatToSave[7]
                vector_length = (speed * 1000) * scale   # meters → pixels

                # minimum visible length
                vector_length = max(10, vector_length)

                boats_t.forward(vector_length)
            else:
                vector_length += 10
                boats_t.forward(vector_length)
        except Exception as e:
            print(f"ERROR DRAWING VECTOR OF {boatToSave[0]}:")
            print(e)
        boats_t.pendown()
        boats_t.back(vector_length)
        boats_t.color("yellow")
        boats_t.write(number, align="center", font=("Consolas", 16, "bold"))
        boats_t.color("black")
        

    def plot_myBoat(self, heading=0.00, speed=0.00, vectorRange=1.00):
        # heading += 90
        range_meters =  vectorRange * 1000
        radar_radius_pixels = 250
        scale = radar_radius_pixels / range_meters 

        heading = heading % 360 # fail save 
        radar_t.shape("arrow")
        
        radar_t.goto(0, 0) # Your boat is always in center of radar
        radar_t.setheading(90 - heading)
        radar_t.pendown()
        radar_t.color("green")
        W_L = 1.00
        radar_t.shapesize(W_L, W_L*4.0)
        radar_t.back(10)
        radar_t.stamp()
        radar_t.forward(10)
        radar_t.color("yellow")
        radar_t.pendown()
        try:
            if speed > 0.00:
                vector_length = (speed * 1000) * scale   # meters → pixels

                # minimum visible length
                vector_length = max(10, vector_length)
                radar_t.forward(vector_length)
            else:
                vector_length = 0
                vector_length += 10
                radar_t.forward(vector_length)
        except Exception as e:
            print(f"ERROR DRAWING VECTOR OF MyBoat:")
            print(e)
        radar_t.setheading(0)
        radar_t.penup()
        radar_t.goto(0, 0)
        radar_t.color("black")
        

    def KeepRadarAlive(self):
        while(True):
            input("Press ENTER to close radar.")
            break

    def SaveImg(self, close=False):
        """
        Non-blocking image save. Captures PostScript immediately and processes
        image in background thread to avoid freezing the GUI.
        """
        try:
            import time as time_module
            self.ps_loc = os.path.join(self.BASE_DIR, f"Radar/PostScript/drawing.ps")
            self.img_loc = os.path.join(self.BASE_DIR, f"Radar/Renders/img.png")
            
            ts = turtle.Screen()
            ts.bgcolor(self.get_bgcolor())
            
            # Fast: Save PostScript (minimal blocking)
            ts.getcanvas().postscript(file=self.ps_loc)
            
            # CRITICAL: Ensure file is flushed to disk before background thread reads it
            # This prevents race condition where thread tries to open incomplete file
            time_module.sleep(0.05)  # Small delay to ensure OS has flushed the file
            
            screen.update()
            
            # Defer heavy image processing to background thread
            if self._save_thread and self._save_thread.is_alive():
                # Wait for previous save to complete before starting a new one
                self._save_thread.join(timeout=2.0)
            
            self._save_thread = threading.Thread(
                target=self._process_image_async,
                kwargs={'close': close},
                daemon=True
            )
            self._save_thread.start()
            
        except Exception as e:
            print(f"Error in SaveImg: {e}")
            if close:
                screen.bye()

    def _process_image_async(self, close=False):
        """
        Background thread function for heavy image processing.
        Runs asynchronously so GUI doesn't freeze.
        Includes retry logic to handle race conditions.
        """
        import time as time_module
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self._save_lock:
                    # Retry logic: wait a bit if file isn't ready
                    if not os.path.exists(self.ps_loc):
                        if retry_count < max_retries - 1:
                            time_module.sleep(0.05)
                            retry_count += 1
                            continue
                        else:
                            raise FileNotFoundError(f"PostScript file not found: {self.ps_loc}")
                    
                    img = Image.open(self.ps_loc).convert("RGBA")

                    if self.RGB[0] > 25 or self.RGB[1] > 25 or self.RGB[2] > 25:
                        # Create background
                        bg = Image.new("RGBA", img.size, (
                            self.RGB[0],
                            self.RGB[1],
                            self.RGB[2],
                            255
                        ))

                        # Combine background + drawing
                        final = Image.alpha_composite(bg, img)
                    
                        # Process pixels - convert iterator to list first
                        img_data = list(img.getdata())
                        new_data = []
                        for item in img_data:
                            # Detect white (or near white)
                            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                                # Make transparent
                                new_data.append((255, 255, 255, 0))
                            else:
                                new_data.append(item)

                        img.putdata(new_data)

                        # Now create background
                        bg = Image.new("RGBA", img.size, (
                            self.RGB[0],
                            self.RGB[1],
                            self.RGB[2],
                            255
                        ))

                        # Composite works NOW
                        final = Image.alpha_composite(bg, img)

                        # final.save(self.img_loc)
                        self.img_RAM = final
                    else:
                        final = Image.open(self.ps_loc).convert("RGBA")
                        # final.save(self.img_loc)
                        self.img_RAM = final
                    
                    break  # Success - exit retry loop
                    
            except (FileNotFoundError, IOError, Exception) as e:
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time_module.sleep(0.05)
                else:
                    print(f"Error in background image processing (attempt {retry_count + 1}/{max_retries}): {e}")
                    break
            finally:
                if close and retry_count >= max_retries - 1:
                    screen.bye()

    def CloseDrawer(self):
        screen.bye()

    def get_bgcolor(self):
        return (self.RGB[0]/255, self.RGB[1]/255, self.RGB[2]/255)
    
    def screen_toggle(self):
        if self.hideScreen:
            self.hideScreen = False
            screen.setup(width=resulotionScale, height=resulotionScale)
        else:
            self.hideScreen = True
            screen.setup(width=resulotionScale, height=resulotionScale, startx=1800)
            
    def color_bg(self):
        # https://www.geeksforgeeks.org/python/python-pillow-colors-on-an-image/
        self.bg_loc = os.path.join(self.BASE_DIR, f"Radar/Background/R={self.RGB[0]},G={self.RGB[1]},B={self.RGB[2]}.png")
        # reuse color if already created
        if os.path.exists(self.bg_loc) == False:
            # try:
            img = Image.open(os.path.join(self.BASE_DIR, f"Radar/Background/template/WhiteBG_1x1.png"))
            img = img.convert("RGB")

            d = img.getdata()

            new_image = []
            for item in d:

                # change the white pixel to current set RGB color
                img = Image.new("RGB", (1, 1), self.RGB)
                img = img.resize((resulotionScale, resulotionScale), Image.LANCZOS)

            # update image data
            img.putdata(new_image)

            # save new image
            img.save(self.bg_loc)
