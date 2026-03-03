import os
import sqlite3
from pyais import decode
from pyais.stream import FileReaderStream
import time
from RadarDrawing import SaveImg, draw_radar_Custom, plot_otherBoat, clear_otherBoats
from datetime import datetime, timedelta
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder_DB.db")

def km_to_lat_deg(km):
    return km / 111.0

def km_to_lon_deg(km, lat):
    return km / (111.0 * math.cos(math.radians(lat)))
    
def ValidateDate(strDate, isDebug = False) -> bool:
    # https://docs.python.org/3/library/datetime.html
    try:
        if "T" not in strDate:
            return False

        date = datetime.fromisoformat(strDate)
        Y = date.year
        M = date.month
        D = date.day
        h = date.hour
        m = date.minute
        s = date.second
        ms = date.microsecond
        if(isDebug is True):
            if len(str(D)) == 1:
                D = "0" + str(D)
            if len(str(M)) == 1:
                M = "0" + str(M)
            if len(str(h)) == 1:
                h = "0" + str(h)
            if len(str(m)) == 1:
                m = "0" + str(m)
            if len(str(s)) == 1:
                s = "0" + str(s)
            print(f"{D}-{M}-{Y} | {h}:{m}:{s}:{ms}")
            print("Passed validation")
        return True
    except Exception as e:
        print("Date vaidation failed do to exception:")
        print(e)
        return False
    return True

def bearing_deg(lat1, lon1, lat2, lon2):
    # convert to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    dLon = math.radians(lon2 - lon1)

    x = math.sin(dLon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2) -
         math.sin(lat1) * math.cos(lat2) * math.cos(dLon))

    bearing = math.degrees(math.atan2(x, y))

    # normalize to 0–360
    return (bearing + 360) % 360


# https://www.geeksforgeeks.org/dsa/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
# ----------------------------------------------------------------------------------------------------
# Python 3 program for the
# haversine formula
def haversine(lat1, lon1, lat2, lon2):
    
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0

    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0

    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) + 
         pow(math.sin(dLon / 2), 2) * 
             math.cos(lat1) * math.cos(lat2));
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return rad * c

def ConvertToX_Y(lat1, lon1, lat2, lon2, debug=False):
    aardstraal = 6371000
    X1 = math.pi * lat1/180
    Y1 = math.pi * lon1/180
    X2 = math.pi * lat2/180
    Y2 = math.pi * lon2/180
    DeltaPhi = X1 - X2
    DeltaL = Y1 - Y2
    average = (X1 + X2) / 2
    Y = DeltaPhi * aardstraal
    X = DeltaL * aardstraal * math.cos(average)
    distance = math.sqrt(X*X+Y*Y)
    mesurements = (X, Y, distance)
    if(debug):
        print(f"X = {X}")
        print(f"Y = {Y}")
        print(f"Afstand = {distance}")
        print(f"return value: {mesurements}")
    
    return mesurements
    
# range = distance between your boat and other boat in both Lad and long
# timeWindow = how far appart the received message is allowed to be shown in the list of other Boats
def InRangeHelper(boat_id, range=0.009, timeWindow = 10.00):
    clear_otherBoats()
    start = time.time()
    performance = draw_radar_Custom(range)
    print(f"Radar generated in {performance} seconds")
    
    dataTuple = "(id, Date, MsgType, Repeat, Mmsi, Status, Turn, Speed, Accuracy, Longitude, Latitude, Course, Heading, Second, Manuever, Spare_1, Raim, Radio)"
    conn = sqlite3.connect(FileRoute_sql3)
    c = conn.cursor()

    myBoat = c.execute('''
        SELECT *
        FROM AIS_Decoder
        WHERE id = ?
    ''', (boat_id,)).fetchone()

    if myBoat == None:
        print("Boat not found")
        return
    
    # mmsi = 4
    # lon = 9
    # lat = 10
    mmsi = myBoat[4]
    lon = myBoat[9]
    lat = myBoat[10]

    # 🔥 CONVERT KM → DEGREE BOUNDING BOX
    lat_range = km_to_lat_deg(range)
    lon_range = km_to_lon_deg(range, lat)
    
    try:
        dateOfPosition = datetime.fromisoformat(myBoat[1])
    except Exception as e:
        print("Failed datetime operation (MyBoat):")
        print(myBoat)
        print(e)
        return
    otherBoatsNoTime = c.execute('''
        SELECT *
        FROM AIS_Decoder
        WHERE Mmsi != ?
        AND ABS(Longitude - ?) <= ?
        AND ABS(Latitude - ?) <= ?
    ''', 
    (mmsi, lon, lon_range, lat, lat_range)).fetchall()
    otherBoats = []
    for boat in otherBoatsNoTime:
        try:
            otherDate = datetime.fromisoformat(boat[1])
            minDateTime = otherDate + timedelta(seconds=-timeWindow)
            maxDateTime = otherDate + timedelta(seconds=timeWindow)
            if (timeWindow <= 0.0):
                otherBoats.append(boat)
            elif(dateOfPosition > minDateTime and dateOfPosition < maxDateTime):
                otherBoats.append(boat)
        except Exception as e:
            print("Boat: ", otherBoatsNoTime)
            print("Failed datetime operation:")
            print(e)

            
    print("YourBoat:")
    print(dataTuple)
    print(myBoat)
    print(f"lon: {myBoat[9]}, lat: {myBoat[10]}")
    print()
    if len(otherBoats) == 0:
        print(f"NO BOATS IN RANGE OF {range}KM CONTACT YOUR AIS PROVIDER FOR ANY UPDATES")
        return
    
    print(f"Other boats in range of {range} lon and lat:")
    print(dataTuple)
    for boat in otherBoats:
        distance = haversine(lat, lon, boat[10], boat[9])
        if distance <= range:
            heading_to_target = bearing_deg(lat, lon, boat[10], boat[9])
            print(boat)
            print(f"lon: {boat[9]}, lat: {boat[10]}")
            print(f"Distance from myBoat in KM: {distance:.2f}")
            print(f"Bearing to boat: {heading_to_target:.1f}°")
            print("-" * 50)
            X_Y = ConvertToX_Y(lat, lon, boat[10], boat[9]) # tuple(X, Y, Distance)
            range_meters = range * 1000
            radar_radius_pixels = 250

            scale = radar_radius_pixels / range_meters
            plot_otherBoat(X_Y[0], X_Y[1], scale)

    end = time.time()
    fin_performance = end - start
    print(f"Radar data trasmited in {fin_performance} seconds")
    print()
    conn.close()
    # saving the image does not close the turtle window by default;
    # we may call ``SaveImg(close=True)`` at the very end of the
    # program if we want to tear the canvas down.
    SaveImg()


# time.sleep(1)
InRangeHelper(1, 5, 5)
InRangeHelper(1, 4, 5)
# time.sleep(1)
InRangeHelper(1, 3, 5)
InRangeHelper(1, 6, 5)
InRangeHelper(1, 7, 5)
InRangeHelper(1, 8, 5)
InRangeHelper(1, 9, 5)
# time.sleep(1)
InRangeHelper(1, 10, 5)
InRangeHelper(1, 10, 5)
# Decode_file(ais_file1)
# Decode_file(ais_file2)