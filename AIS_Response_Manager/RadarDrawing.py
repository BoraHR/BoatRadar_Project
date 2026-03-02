import turtle
import math
import os
from PIL import Image
import time

t = turtle.Turtle(visible=False)
t.hideturtle()
t.speed(0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ps_loc = os.path.join(BASE_DIR, "Radar/drawing.ps")
img_loc = os.path.join(BASE_DIR, "Radar/img.png")

# KM the amount of lines represent keep in mind it must be an int.
def draw_radar_Custom(KM):
    start = time.time()
    # if int(math.ceil(KM)) == 3:
    #     draw_radar_3KM()
    #     end = time.time()
    #     print(f"ms: {end - start}")
    #     return 
    # if int(math.ceil(KM)) == 6:
    #     draw_radar_6KM()
    #     end = time.time()
    #     print(f"ms: {end - start}")
    #     return
    # if int(math.ceil(KM)) == 10:
    #     draw_radar_10KM()
    #     end = time.time()
    #     print(f"ms: {end - start}")
    #     return
    
    KM = int(math.ceil(KM))

    radius_list = [250]
    multiplier = 0
    multiplier += KM
    while(multiplier >= 1):
        multiplier -= 1
        radius_list.append((250/KM) * multiplier)
    
    radius_list.reverse()
    for r in radius_list:
        t.penup()
        t.goto(0, -r)
        t.pendown()
        t.circle(r)
    draw_crosshair(radius_list[-1])
    t.write(str(KM), align="center", font=("Consolas", 16, "bold"))
    plot_myBoat()
    end = time.time()
    SaveImg()
    return end - start # returns the a time it took to create the img in seconds.

def draw_crosshair(range):
    max_radius = range
    t.penup()
    t.goto(-max_radius, 0)
    t.pendown()
    t.goto(max_radius, 0)  # horizontal line

    t.penup()
    t.goto(0, -max_radius)
    t.pendown()
    t.goto(0, max_radius)  # vertical line

def plot_otherBoat(x_meters, y_meters, scale=0.050):
    px = x_meters * scale
    py = y_meters * scale

    t.penup()
    t.goto(px, py) # px(x): ←→   py(y): ↑↓
    t.dot(8, "red")

def plot_myBoat():
    t.penup()
    t.goto(0, 0) # Your boat is always in center of radar
    t.dot(8, "Green")

def KeepRadarAlive():
    while(True):
        input("Press ENTER to close radar.")
        break
    turtle.done()

def SaveImg():
    # get screents
    ts = turtle.Screen()
    # save as PostScript
    ts.getcanvas().postscript(file=ps_loc)
    img = Image.open(ps_loc)
    img.save(img_loc)
    turtle.done()

draw_radar_Custom(10)
# draw_radar_3KM()
# draw_radar_6KM()
# draw_radar_10KM()
# KeepRadarAlive()
# plot_otherBoat(2960, 2290)   # 1 km east, 2 km north
# plot_otherBoat(3620, 1200)
# plot_otherBoat(1280, 920)
# plot_otherBoat(2180, -4320)
# plot_otherBoat(1480, -3440)