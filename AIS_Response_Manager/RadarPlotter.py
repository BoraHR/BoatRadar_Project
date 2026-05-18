import os
import sqlite3
from pyais import decode
from pyais.stream import FileReaderStream
import time
from RadarDrawing import RadarDrawing 
from datetime import datetime, timedelta
from Algorithm import km_to_lat_deg,  km_to_lon_deg, bearing_deg, haversine, ConvertToX_Y, calculate_cpa_tcpa
from pyais_decoder import Update_Row_AIS_Render_History
from enum import Enum
from AIS_ResponderManager import AIS_ResponderManager
import winsound
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder.db")
# Range_setting = 3
# ID = 1
ID = 46

# https://www.geeksforgeeks.org/python/enum-in-python/
class Order(Enum):
    DEFAULT = 0
    RANGE = 1
    CPA = 2
    TCPA = 3

class RadarPlotter:

    def __init__(self, IsTest = False):
        self.IsDebug = False
        self.FileRoute_sql3 = FileRoute_sql3
        self.conn = sqlite3.connect(FileRoute_sql3)
        self.ID = ID
        if IsTest:
            self.FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
            self.ID = 1
        self.Order = Order.RANGE
        self.RadarConsoleData = []
        self.PrevRadarConsole_BoatID = []
        self.draw = RadarDrawing()
        self.ARM = AIS_ResponderManager(ID)
        # self.draw.color_bg()
        # targetId ensures that selected target from RadarController will be orange when the ID condition is met
        # DEFAULT is -1 instead of None to prefent potentioal None exeptions
        self.targetId = -1
        # self.IsTarget = False

    def toglePrint(self):
        if self.IsDebug:
            self.IsDebug = False
        else:
            self.IsDebug = True

    def setTarget(self, id):
        try:
            if(str(id).isnumeric()):
                if(self.targetId == id):
                    self.targetId = -1 #self.clearTarget()
                else:
                    self.targetId = id
        except Exception as e:
            print("Error Setting target:")
            print(e)

    def setEnum(self, val):
        try:
            if val.isnumeric():
                self.Order = Order.value(int(val))
            else:
                self.Order = Order[val.upper()]
        except Exception as e:
            print("Failed to set Enum:")
            print(e)

    def clearConsoleData(self):
        self.RadarConsoleData.clear()

    def saveBoatsOutOfRange(self, myBoat):
        lon = myBoat[9]
        lat = myBoat[10]
        strDateTime = datetime.now().isoformat()
        
        for data2 in self.PrevRadarConsole_BoatID:
            history = lambda id, RCD : any(item[0][0] == id for item in RCD)
            if history(data2, self.RadarConsoleData) == False:
                c = self.conn.cursor()
                Lat_Long = c.execute('''
                    SELECT Longitude, Latitude
                    FROM AIS_Decoder
                    WHERE id = ?
                ''', (data2,)).fetchone()
                LastRange = ConvertToX_Y(lat, lon, Lat_Long[0], Lat_Long[1])
                Update_Row_AIS_Render_History(strDateTime, LastRange[2], data2, True)
                self.PrevRadarConsole_BoatID.remove(data2)

    # def clearTarget(self):
    #     self.targetId = -1

    def GetBoat(self, boat_id):
        c = self.conn.cursor()
        return c.execute('''
            SELECT *
            FROM AIS_Decoder
            WHERE id = ?
        ''', (boat_id,)).fetchone()
    
    def orderList(self, reverse=False):
        try:
            # boat[0], number[1], distance[2], cpa[3], tcpa[4], 
            if self.Order is Order.RANGE:
                self.RadarConsoleData = sorted(self.RadarConsoleData, key=lambda x: x[2], reverse=reverse) 
            elif self.Order is Order.CPA:
                self.RadarConsoleData = sorted(self.RadarConsoleData, key=lambda x: x[3], reverse=reverse)
            elif self.Order is Order.TCPA:
                self.RadarConsoleData = sorted(self.RadarConsoleData, key=lambda x: abs(x[4]), reverse=reverse)
            else:
                self.RadarConsoleData = sorted(self.RadarConsoleData, reverse=reverse)
        except Exception as e:
            print(f"Failed to order by {self.Order.name}")
            print(e)

    def plot_boats(self, myBoat):
        for i, item in enumerate(self.RadarConsoleData, start=1):
            item[1] = i

        for boat in self.RadarConsoleData:
            if boat[5] != None:
                pd = boat[5] # (boat_id, X_Y[0], X_Y[1], number, scale, boat[12], False)
                #  def plot_otherBoat(self, boatToSave, x_meters, y_meters, number, scale=0.050, heading=0.00, IsTarget = False):
                if self.targetId == boat[0][0]:
                    self.draw.plot_otherBoat(myBoat, boat[0], pd[1], pd[2], boat[1], pd[4], pd[5], True)
                else:
                    self.draw.plot_otherBoat(myBoat, boat[0], pd[1], pd[2], boat[1], pd[4], pd[5], False)


    # range = distance between your boat and other boat in both Lad and long
    # timeWindow = how far appart the received message is allowed to be shown in the list of other Boats
    def InRangeHelper(self, boat_id, range=0.009, timeWindow = 10.00):
        self.clearConsoleData()
        self.draw.clear_otherBoats()
        start = time.time()
        
        dataTuple = "(id, Date, MsgType, Repeat, Mmsi, Status, Turn, Speed, Accuracy, Longitude, Latitude, Course, Heading, Second, Manuever, Spare_1, Raim, Radio)"
        c = self.conn.cursor()

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
        speed = myBoat[7]
        heading = myBoat[12]

        performance = self.draw.draw_radar_Custom(range, heading, speed)
        # CONVERT KM → DEGREE BOUNDING BOX
        lat_range = km_to_lat_deg(range)
        lon_range = km_to_lon_deg(range, lat)

        min_lon = lon - lon_range
        max_lon = lon + lon_range
        min_lat = lat - lat_range
        max_lat = lat + lat_range
            
        try:
            dateOfPosition = datetime.fromisoformat(myBoat[1])
        except Exception as e:
            print("Failed datetime operation (MyBoat):")
            print(myBoat)
            print(e)
            return
        
        min_time = (dateOfPosition - timedelta(seconds=timeWindow)).isoformat()
        max_time = (dateOfPosition + timedelta(seconds=timeWindow)).isoformat() 
        otherBoats = c.execute('''
        SELECT *
        FROM AIS_Decoder
        WHERE Mmsi != ?
        AND Longitude BETWEEN ? AND ?
        AND Latitude BETWEEN ? AND ?
        AND Date BETWEEN ? AND ?
        OR ID == ?
        ''',
        (
            mmsi,
            min_lon, max_lon,
            min_lat, max_lat,
            min_time, max_time,
            self.targetId
        )).fetchall()
        if self.IsDebug:        
            print("YourBoat:")
            print(dataTuple)
            print(myBoat)
            print(f"lon: {myBoat[9]}, lat: {myBoat[10]}")
            print()
        if len(otherBoats) == 0:
            if self.IsDebug:
                print(f"NO BOATS IN RANGE OF {range}KM CONTACT YOUR AIS PROVIDER FOR ANY UPDATES")
            self.draw.SaveImg()
            return
        if self.IsDebug:
            print(f"Other boats in range of {range} lon and lat:")
            print(dataTuple)
        number = 0
        for boat in otherBoats:
            distance = haversine(lat, lon, boat[10], boat[9])
            is_target = boat[0] == self.targetId
            
            # Always include target boat, or include if in range
            if distance <= range or is_target:
                number += 1
                heading_to_target = bearing_deg(lat, lon, boat[10], boat[9])
                if self.IsDebug:
                    print(boat)
                    print(f"lon: {boat[9]}, lat: {boat[10]}")
                    print(f"Distance from myBoat in KM: {distance:.2f}")
                    print(f"Bearing to boat: {heading_to_target:.1f}°")
                X_Y = ConvertToX_Y(lat, lon, boat[10], boat[9]) # tuple(X, Y, Distance)


                range_meters = range * 1000
                radar_radius_pixels = 250

                cpa, tcpa = calculate_cpa_tcpa(
                    0, 0, speed, heading,
                    X_Y[0], X_Y[1], boat[7], boat[12]
                )

                if self.IsDebug:
                    print(f"CPA: {cpa:.1f} meters")
                    print(f"TCPA: {tcpa:.1f} seconds")
                    print("-" * 50)

                scale = radar_radius_pixels / range_meters           
                if is_target:
                    self.RadarConsoleData.append([(boat), number, distance, cpa, tcpa, (boat_id, X_Y[0], X_Y[1], number, scale, boat[12], True)])
                    self.ARM.Update_SubData_With_Value(boat[0], distance, cpa, tcpa)
                    if boat[0] not in self.PrevRadarConsole_BoatID:
                        self.PrevRadarConsole_BoatID.append(boat[0])
                else:
                    self.RadarConsoleData.append([(boat), number, distance, cpa, tcpa, (boat_id, X_Y[0], X_Y[1], number, scale, boat[12], False)])
                    self.ARM.Update_SubData_With_Value(boat[0], distance, cpa, tcpa)
                    if boat[0] not in self.PrevRadarConsole_BoatID:
                        self.PrevRadarConsole_BoatID.append(boat[0])

        # self.saveBoatsOutOfRange(myBoat)
        self.orderList()
        self.plot_boats(myBoat)
            
        # when new KM setting is selected it takes longer to generate because it has to redraw radar reading chached drawing is almost always instant
        print(f"Radar generated in {performance} seconds")
        # saving the image does not close the turtle window by default;
        # we may call ``SaveImg(close=True)`` at the very end of the
        # program if we want to tear the canvas down.
        self.draw.SaveImg()
        end = time.time()
        fin_performance = end - start
        print(f"Radar data trasmited in {fin_performance} seconds")
        return myBoat
    
    