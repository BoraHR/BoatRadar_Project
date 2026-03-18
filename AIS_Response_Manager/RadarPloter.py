import os
import sqlite3
from pyais import decode
from pyais.stream import FileReaderStream
import time
from RadarDrawing import RadarDrawing 
from datetime import datetime, timedelta
from Algorithm import km_to_lat_deg,  km_to_lon_deg, bearing_deg, haversine, ConvertToX_Y, calculate_cpa_tcpa

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder_DB.db")
Range_setting = 3

class RadarPlotter:
    def __init__(self):
        self.draw = RadarDrawing()
        # targetId ensures that selected target from RadarController will be orange when the ID condition is met
        # DEFAULT is -1 instead of None to prefent potentioal None exeptions
        self.targetId = -1
        self.IsTarget = False

    def setTarget(self, id):
        try:
            if(id.isnumeric()):
                self.targetId = id
        except Exception as e:
            print("Error Setting target:")
            print(e)

    def clearTarget(self):
        self.targetId = -1

    def GetBoat(self, boat_id):
        conn = sqlite3.connect(FileRoute_sql3)
        c = conn.cursor()
        return c.execute('''
            SELECT *
            FROM AIS_Decoder
            WHERE id = ?
        ''', (boat_id,)).fetchone()

    # range = distance between your boat and other boat in both Lad and long
    # timeWindow = how far appart the received message is allowed to be shown in the list of other Boats
    def InRangeHelper(self, boat_id, range=0.009, timeWindow = 10.00):
        self.draw.clear_otherBoats()
        start = time.time()
        performance = self.draw.draw_radar_Custom(range)
        
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
        speed = myBoat[7]
        heading = myBoat[12]

        # 🔥 CONVERT KM → DEGREE BOUNDING BOX
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
        ''',
        (
            mmsi,
            min_lon, max_lon,
            min_lat, max_lat,
            min_time, max_time
        )).fetchall()
                
        print("YourBoat:")
        print(dataTuple)
        print(myBoat)
        print(f"lon: {myBoat[9]}, lat: {myBoat[10]}")
        print()
        if len(otherBoats) == 0:
            print(f"NO BOATS IN RANGE OF {range}KM CONTACT YOUR AIS PROVIDER FOR ANY UPDATES")
            self.draw.SaveImg()
            return
        
        print(f"Other boats in range of {range} lon and lat:")
        print(dataTuple)
        number = 0
        for boat in otherBoats:
            distance = haversine(lat, lon, boat[10], boat[9])
            if distance <= range:
                number += 1
                heading_to_target = bearing_deg(lat, lon, boat[10], boat[9])
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

                print(f"CPA: {cpa:.1f} meters")
                print(f"TCPA: {tcpa:.1f} seconds")
                print("-" * 50)

                scale = radar_radius_pixels / range_meters           
                if boat[0] == self.targetId:
                    self.draw.plot_otherBoat((boat_id, X_Y[0], X_Y[1]), X_Y[0], X_Y[1], number, scale, boat[12],  True) # "(id, Date, MsgType, Repeat, Mmsi, Status, Turn, Speed, Accuracy, Longitude, Latitude, Course, Heading, Second, Manuever, Spare_1, Raim, Radio)"
                else:
                    self.draw.plot_otherBoat((boat_id, X_Y[0], X_Y[1]), X_Y[0], X_Y[1], number, scale, boat[12], False)

        
        # when new KM setting is selected it takes longer to generate because it has to redraw radar reading chached drawing is almost always instant
        print(f"Radar generated in {performance} seconds") 
        conn.close()
        # saving the image does not close the turtle window by default;
        # we may call ``SaveImg(close=True)`` at the very end of the
        # program if we want to tear the canvas down.
        self.draw.SaveImg()
        end = time.time()
        fin_performance = end - start
        print(f"Radar data trasmited in {fin_performance} seconds")
        return myBoat