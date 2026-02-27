import os
import sqlite3
from pyais import decode
from pyais.stream import FileReaderStream
import time
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder_DB.db")

import math

def OpenDB():
        NotImplementedError

def Decode_file(file):
    with open(ais_file1, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            start = time.time()
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Extract only the AIS sentence (starts with $AIVDM)
            if "$AIVDM" in line:
                nmea_sentence = line.split("$AIVDM")[-1]
                nmea_sentence = "$AIVDM" + nmea_sentence

                try:
                    decoded = decode(nmea_sentence)
                    if(181.0 == float(decoded.lon) or 91.0 == float(decoded.lat) or 0.00 > float(decoded.lon) or 0.00 > float(decoded.lat)):
                        print("Decoded message:")
                        print(decoded)
                        print("-" * 50)
                        end = time.time()
                        print(f"ms: {end - start}")
                except Exception as e:
                    # print("Failed to decode:", nmea_sentence)
                    # print("Error:", e)
                    # print("-" * 50)
                    # end = time.time()
                    # print(f"ms: {end - start}")
                    pass

def Save_DecodedData(_file):
    total_time = 0.00
    failed = 0
    skipped = 0
    passed = 0
    conn = sqlite3.connect(FileRoute_sql3)
    c = conn.cursor()
    # Accuracy and Raim is bool stored as an integer because of sql3 limitations 
    # 0 == False, 1 == True
    c.execute('''
        CREATE TABLE IF NOT EXISTS AIS_Decoder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            MsgType INTEGER,
            Repeat INTEGER,
            Mmsi TEXT NOT NULL CHECK (length(Mmsi) = 9),
            Status INTEGER,
            Turn REAL,
            Speed REAL,
            Accuracy INTEGER,
            Longitude REAL,
            Latitude REAL,
            Course REAL,
            Heading REAL,
            Second REAL,
            Manuever TEXT,
            Spare_1 TEXT,
            Raim INTEGER,
            Radio INTEGER
        )
    ''') 
    conn.commit()
    print("DB created")
    with open(_file, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            start = time.time()
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Extract only the AIS sentence (starts with $AIVDM)
            if "$AIVDM" in line:
                frag_sentence = line.split("$AIVDM")
                nmea_sentence = "$AIVDM" + frag_sentence[1]
                date = frag_sentence[0].split(" ")[1]
                try:
                    decoded = decode(nmea_sentence)
                    accuracyInt = int(bool(decoded.accuracy))
                    raimInt = int(bool(decoded.raim))
                    if(decoded.mmsi and len(str(decoded.mmsi).strip()) == 9):
                        if(ValidateFields(decoded) == True and ValidateDate(date) == True):
                            try:
                                c.execute('''
                                    INSERT INTO AIS_Decoder
                                    (
                                        Date,
                                        MsgType, 
                                        Repeat,
                                        Mmsi,
                                        Status,
                                        Turn,
                                        Speed,
                                        Accuracy,
                                        Longitude,
                                        Latitude,
                                        Course,
                                        Heading,
                                        Second,
                                        Manuever,
                                        Spare_1,
                                        Raim,
                                        Radio
                                    )
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''',
                                (
                                    date,
                                    decoded.msg_type,
                                    decoded.repeat,
                                    decoded.mmsi,
                                    decoded.status,
                                    decoded.turn,
                                    decoded.speed,
                                    accuracyInt,
                                    decoded.lon,
                                    decoded.lat,
                                    decoded.course,
                                    decoded.heading,
                                    decoded.second,
                                    decoded.maneuver,
                                    decoded.spare_1,
                                    raimInt,
                                    decoded.radio
                                )   
                            )
                                end = time.time()
                                print("Passed:")
                                print(date)
                                print(nmea_sentence)
                                print(decoded)
                                print(f"ms: {(end - start) * 1000:.2f}")
                                print("-" * 50)
                                total_time += end - start
                                passed += 1
                            except Exception as e:
                                print("Failed:")
                                print(date)
                                print(nmea_sentence)
                                print(decoded)
                                print("Do to an error during SQL Insertion")
                                print(e)
                                end = time.time()
                                print(f"ms: {(end - start) * 1000:.2f}")
                                print("-" * 50)
                                total_time += end - start
                                failed += 1
                        else:
                            print("Skipped:")
                            print(date)
                            print(nmea_sentence)
                            print(decoded)
                            print("Because field validation failed")
                            end = time.time()
                            print(f"ms: {(end - start) * 1000:.2f}")
                            print("-" * 50)
                            total_time += end - start
                            skipped += 1
                            continue
                    else:
                        print("Failed:")
                        print(date)
                        print(nmea_sentence)
                        print(decoded)
                        print("Because one or more vailidation have failed")
                        end = time.time()
                        print(f"ms: {(end - start) * 1000:.2f}")
                        print("-" * 50)
                        total_time += end - start
                        failed += 1
                        continue
                except Exception as e:
                    print("Failed to decode:", date, nmea_sentence)
                    print("Error:", e)
                    end = time.time()
                    print(f"ms: {(end - start) * 1000:.2f}")
                    print("-" * 50)
                    total_time += end - start
                    continue
        conn.commit()
        conn.close()
        print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped} | Time(ms): {total_time * 1000:.2f}")


def ValidateFields(decoded) -> bool:
    try:
        if(
            decoded.msg_type is None or 
            decoded.repeat is None or 
            decoded.mmsi is None or 
            decoded.status is None or
            decoded.turn is None or
            decoded.accuracy is None or
            decoded.lon is None or
            decoded.lat is None or
            decoded.course is None or
            decoded.heading is None or
            decoded.second is None or
            decoded.maneuver is None or
            decoded.spare_1 is None or
            decoded.raim is None or
            decoded.radio is None
        ):
            print("Validation failed one or more fields are None")
            return False
        if(
            decoded.lon > 180.00 or decoded.lon < 0.00 or
            decoded.lat > 90.00 or decoded.lat < 0.00 or
            decoded.course >= 360.00 or decoded.course < 0.00 or
            decoded.heading >= 360.00 or decoded.heading < 0.00 or
            decoded.second > 60 or decoded.second < 0
            # decoded.turn > 127.00 or decoded.turn < -127.00
        ):
            print("Validation failed one or more fields have invalid data")
            return False
        return True
    except Exception as e:
        print("Field validation failed do to exception:")
        print(e)
        return False

def km_to_lat_deg(km):
    return km / 111.0

def km_to_lon_deg(km, lat):
    return km / (111.0 * math.cos(math.radians(lat)))
    
def ValidateDate(strDate, isDebug = False) -> bool:
    # https://docs.python.org/3/library/datetime.html
    try:
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

def ConvertToX_Y(lat1, lon1, lat2, lon2):
    print(math.pi * lat1/180)
    print(math.pi * lon1/180)
    print(math.pi * lat2/180)
    print(math.pi * lon2/180)

# range = distance between your boat and other boat in both Lad and long
# timeWindow = how far appart the received message is allowed to be shown in the list of other Boats
def InRangeHelper(boat_id, range=0.009, timeWindow = 10.00):
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
    print()
    conn.close()


# Save_DecodedData(ais_file1)
# Save_DecodedData(ais_file2)
# InRangeHelper(1, 5, 5)
ConvertToX_Y(51.990935, 4.050667, 51.957192, 4.076493)
# Decode_file(ais_file1)
# Decode_file(ais_file2)