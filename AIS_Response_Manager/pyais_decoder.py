import os
import sqlite3
from pyais import decode
from pyais.stream import FileReaderStream
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder_DB.db")

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
                    print("Decoded message:")
                    print(decoded)
                    print("-" * 50)
                    end = time.time()
                    print(f"ms: {end - start}")
                except Exception as e:
                    print("Failed to decode:", nmea_sentence)
                    print("Error:", e)
                    print("-" * 50)
                    end = time.time()
                    print(f"ms: {end - start}")

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
            MsgType TEXT,
            Repeat TEXT,
            Mmsi TEXT NOT NULL CHECK (length(Mmsi) = 9),
            Status TEXT,
            Turn TEXT,
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
                nmea_sentence = line.split("$AIVDM")[-1]
                nmea_sentence = "$AIVDM" + nmea_sentence
                try:
                    decoded = decode(nmea_sentence)
                    accuracyInt = int(bool(decoded.accuracy))
                    raimInt = int(bool(decoded.raim))
                    if(decoded.mmsi and len(str(decoded.mmsi).strip()) == 9):
                        if(ValidateFields(decoded) == True):
                            try:
                                c.execute('''
                                    INSERT INTO AIS_Decoder
                                    (
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
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''',
                                (
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
                                print(nmea_sentence)
                                print(decoded)
                                print(f"ms: {(end - start) * 1000:.2f}")
                                print("-" * 50)
                                total_time += end - start
                                passed += 1
                            except Exception as e:
                                print("Failed:")
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
                        print(nmea_sentence)
                        print(decoded)
                        print("Because it has an invalid mssi")
                        end = time.time()
                        print(f"ms: {(end - start) * 1000:.2f}")
                        print("-" * 50)
                        total_time += end - start
                        failed += 1
                        continue
                except Exception as e:
                    print("Failed to decode:", nmea_sentence)
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
        if(decoded.msg_type is None or 
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
        else:
            return True
    except Exception as e:
        print("Validation failed do to exception:")
        print(e)
        return False
    
# 0.009 is 1KM 
def InRangeHelper(boat_id, range=0.009):
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
    
    # mmsi = 3
    # lon = 9
    # lat = 10
    mmsi = myBoat[3]
    lon = myBoat[8]
    lat = myBoat[9]
    otherBoats = c.execute('''
        SELECT *
        FROM AIS_Decoder
        WHERE Mmsi != ?
        AND ABS(Longitude - ?) <= ?
        AND ABS(Latitude - ?) <= ?
    ''', 
    (myBoat[3], lon, range, lat, range)).fetchall()
    print("YourBoat:")
    print(myBoat)
    print()
    print(f"Other boats in range of {range} lon and lat:")
    for boat in otherBoats:
        print(boat)

    print()
    conn.close()

InRangeHelper(1)
# InRangeHelper(1, 9)
# InRangeHelper(1, 12)
# InRangeHelper(1, 16)
# InRangeHelper(1, 30)






