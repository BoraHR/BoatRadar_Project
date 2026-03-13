import turtle
import math
import os
from PIL import Image
import time

# t = turtle.Turtle(visible=False)
# t.hideturtle()
# t.speed(0)

screen = turtle.Screen()
screen.tracer(0)

radar_t = turtle.Turtle(visible=False)
radar_t.speed(0)

boats_t = turtle.Turtle(visible=False)
boats_t.speed(0)

class RadarDrawing:
    def __init__(self):
        # radar_built = False
        self.KM_build = -1
        self.plotedBoats = []
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ps_loc = os.path.join(self.BASE_DIR, f"Radar/drawing_{self.KM_build}.ps")
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/img_{self.KM_build}.png")

    # KM the amount of lines represent keep in mind it must be an int.
    def draw_radar_Custom(self, KM):
        start = time.time()
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
        for r in radius_list:
            radar_t.penup()
            radar_t.goto(0, -r)
            radar_t.pendown()
            radar_t.circle(r)
        self.draw_crosshair(radius_list[-1])
        radar_t.write(str(KM), align="center", font=("Consolas", 16, "bold"))
        self.plot_myBoat()
        end = time.time()
        self.KM_build = KM
        return end - start # returns the a time it took to create the img in seconds.

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

    def plot_otherBoat(self, boatToSave, x_meters, y_meters, scale=0.050, heading=0.00, IsTarget = False):
        px = x_meters * scale
        py = y_meters * scale
        self.plotedBoats.append((boatToSave, x_meters, y_meters))
        if heading is None or heading >= 360 or heading < 0:
            self.plot_otherBoat_dot(x_meters, y_meters, scale, IsTarget)
            return
        heading += 90
        heading = heading % 360 # fail save 
        
        boats_t.penup()
        boats_t.goto(px, py) # px(x): ←→  py(y): ↑↓
        boats_t.shape("arrow")
        boats_t.shapesize(0.25, 1)
        if(IsTarget):
            boats_t.color("orange")
        else:
            boats_t.color("red")
        boats_t.setheading(heading)
        boats_t.stamp()
        

    def plot_myBoat(self):
        radar_t.penup()
        radar_t.goto(0, 0) # Your boat is always in center of radar
        radar_t.dot(8, "Green")

    def KeepRadarAlive(self):
        while(True):
            input("Press ENTER to close radar.")
            break
        # turtle.done()

    def SaveImg(self, close=False):
        self.ps_loc = os.path.join(self.BASE_DIR, f"Radar/drawing_{self.KM_build}.ps")
        self.img_loc = os.path.join(self.BASE_DIR, f"Radar/img_{self.KM_build}.png")
        """Write the current turtle screen to disk.

        By default the window is left open so that subsequent plotting calls
        can continue.  Pass ``close=True`` if you want the canvas to be torn
        down (for example at the very end of a batch of drawings).
        """
        ts = turtle.Screen()
        # save as PostScript
        ts.getcanvas().postscript(file=self.ps_loc)
        img = Image.open(self.ps_loc)
        img.save(self. img_loc)
        
        screen.update()
        if close:
            screen.bye()