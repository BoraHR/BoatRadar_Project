import os
import sqlite3
from pyais import decode
from pyais.stream import FileReaderStream
import time
from datetime import datetime, timedelta
import math

# !!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
FileRoute_sql3 = os.path.join(BASE_DIR, "Pytests/MockData/AIS-Responder.db")

def DB_Exists():
    print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")
    if os.path.exists(FileRoute_sql3):
        return True
    return False

def Decode_file(file):
    print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")
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
                    if(181.0 > float(decoded.lon) and 91.0 > float(decoded.lat) and -181.00 < float(decoded.lon) and -91.00 < float(decoded.lat)):
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
    print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")

def Save_DecodedData(_file):
    print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")
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
            Manuever INTERGER,
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
                                    UPDATE AIS_Decoder
                                    SET
                                        Date = ?,
                                        MsgType = ?, 
                                        Repeat = ?,
                                        Mmsi = ?,
                                        Status = ?,
                                        Turn = ?,
                                        Speed = ?,
                                        Accuracy = ?,
                                        Longitude = ?,
                                        Latitude = ?,
                                        Course = ?,
                                        Heading = ?,
                                        Second = ?,
                                        Manuever = ?,
                                        Spare_1 = ?,
                                        Raim = ?,
                                        Radio = ?
                                    WHERE Mmsi = ?
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
                                    decoded.radio,
                                    decoded.mmsi
                                )   
                                )
                                if c.rowcount == 0:
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
        print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")
        
def Create_AIS_Render_History():
    print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")
    try:
        if os.path.exists(FileRoute_sql3):
            conn = sqlite3.connect(FileRoute_sql3)
            c = conn.cursor()
            c. execute('''
                CREATE TABLE IF NOT EXISTS AIS_Render_History (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    DateString TEXT,
                    LastRange REAL,
                    RangeIsKM INTEGER,
                    Boat_ID INTEGER UNIQUE,
                    FOREIGN KEY (Boat_ID) REFERENCES AIS_Decoder(id) 
                )
            ''')
            conn.commit()
            conn.close()
            print("AIS_Render_History created")
        else:
            print("AIS_Responder.db not found")
    except Exception as e:
        print("Failed to create AIS_Render_History.db: ")
        print(e)
    print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")

def Update_Row_AIS_Render_History(DateTime, LastRange, BoatID, IsKM=True):
    print("!!! DO NOT USE test_pyais_decoder.py IN ACTUAL PROGRAM USE pyais_decoder.py INSTEAD !!!")
    try:    
        if os.path.exists(FileRoute_sql3):
            conn = sqlite3.connect(FileRoute_sql3)
            c = conn.cursor()
            count = c.execute('''
                INSERT INTO AIS_Render_History (Boat_ID, DateString, LastRange, RangeIsKM)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(Boat_ID)
                DO UPDATE SET
                    DateString = excluded.DateString,
                    LastRange = excluded.LastRange,
                    RangeIsKM = excluded.RangeIsKM
            ''',
            (
                BoatID,
                DateTime,
                LastRange,
                int(IsKM) # True == 1, False == 0
            )   
            )
            conn.commit()
            conn.close()
            # print("AIS_Render_History.DB created")
        else:
            print("AIS_Rsponder.DB.db not found")
    except Exception as e:
        print("Failed to Insert/update AIS_Render_History.db: ")
        print(e)

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
            decoded.lon > 180.00 or decoded.lon < -180.00 or
            decoded.lat > 90.00 or decoded.lat < -90.00 or
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

# Save_DecodedData(ais_file1)
# Save_DecodedData(ais_file2)