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

# radar_built = False
KM_build = -1
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ps_loc = os.path.join(BASE_DIR, f"Radar/drawing_{KM_build}.ps")
img_loc = os.path.join(BASE_DIR, f"Radar/img_{KM_build}.png")



# KM the amount of lines represent keep in mind it must be an int.
def draw_radar_Custom(KM):
    start = time.time()
    if KM < 1:
        KM = 1
    global KM_build
    if KM_build == KM:
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
    draw_crosshair(radius_list[-1])
    radar_t.write(str(KM), align="center", font=("Consolas", 16, "bold"))
    plot_myBoat()
    end = time.time()
    KM_build = KM
    return end - start # returns the a time it took to create the img in seconds.

def draw_crosshair(range):
    max_radius = range
    radar_t.penup()
    radar_t.goto(-max_radius, 0)
    radar_t.pendown()
    radar_t.goto(max_radius, 0)  # horizontal line

    radar_t.penup()
    radar_t.goto(0, -max_radius)
    radar_t.pendown()
    radar_t.goto(0, max_radius)  # vertical line

def clear_otherBoats():
    # if the canvas has already been closed (e.g. after a SaveImg() call)
    # the turtle module will raise a TclError/TurtleGraphicsError.
    # We catch it here and simply ignore it – the next draw operation will
    # either recreate the screen or fail later if not recreated.
    try:
        boats_t.clear()
    except Exception:
        # screen or turtle may have been destroyed; nothing we can do now
        pass

def plot_otherBoat_dot(x_meters, y_meters, scale=0.050):
    px = x_meters * scale
    py = y_meters * scale

    boats_t.penup()
    boats_t.goto(px, py) # px(x): ←→  py(y): ↑↓
    boats_t.dot(8, "red")

def plot_otherBoat(x_meters, y_meters, scale=0.050, heading=0.00):
    px = x_meters * scale
    py = y_meters * scale
    if heading is None or heading >= 360 or heading < 0:
        plot_otherBoat_dot(x_meters, y_meters, scale)
        return
    heading += 90
    heading = heading % 360 # fail save 
    
    boats_t.penup()
    boats_t.goto(px, py) # px(x): ←→  py(y): ↑↓
    boats_t.shape("arrow")
    boats_t.shapesize(0.25, 1)
    boats_t.color("red")
    boats_t.setheading(heading)
    boats_t.stamp()

def plot_myBoat():
    radar_t.penup()
    radar_t.goto(0, 0) # Your boat is always in center of radar
    radar_t.dot(8, "Green")

def KeepRadarAlive():
    while(True):
        input("Press ENTER to close radar.")
        break
    # turtle.done()

def SaveImg(close=False):
    ps_loc = os.path.join(BASE_DIR, f"Radar/drawing_{KM_build}.ps")
    img_loc = os.path.join(BASE_DIR, f"Radar/img_{KM_build}.png")
    """Write the current turtle screen to disk.

    By default the window is left open so that subsequent plotting calls
    can continue.  Pass ``close=True`` if you want the canvas to be torn
    down (for example at the very end of a batch of drawings).
    """
    ts = turtle.Screen()
    # save as PostScript
    ts.getcanvas().postscript(file=ps_loc)
    img = Image.open(ps_loc)
    img.save(img_loc)
    
    screen.update()
    if close:
        screen.bye()


    
# plot_otherBoat(0,0,0.0)
# draw_radar_Custom(10)
# draw_radar_3KM()
# draw_radar_6KM()
# draw_radar_10KM()
# KeepRadarAlive()
# plot_otherBoat(2960, 2290)   # 1 km east, 2 km north
# plot_otherBoat(3620, 1200)
# plot_otherBoat(1280, 920)
# plot_otherBoat(2180, -4320)
# plot_otherBoat(1480, -3440)