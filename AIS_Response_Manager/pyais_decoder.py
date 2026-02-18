import os
import sqlite3
from pyais import decode
from pyais.stream import FileReaderStream
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ais_file1 = os.path.join(BASE_DIR, "Data/ais_arca.txt")
ais_file2 = os.path.join(BASE_DIR, "Data/ais_rp42.txt")
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder_DB.db")


def Decode_file1():
    with open(ais_file1, "r") as file:
        for line in file:
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
                except Exception as e:
                    print("Failed to decode:", nmea_sentence)
                    print("Error:", e)
                    print("-" * 50)

def Decode_file2():
    with open(ais_file2, "r") as file:
        for line in file:
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
                except Exception as e:
                    print("Failed to decode:", nmea_sentence)
                    print("Error:", e)
                    print("-" * 50)

def Save_DecodedData_File1():
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
            Logitude REAL,
            Latitude REAL,
            Course REAL,
            Heading REAL,
            Second REAL,
            Manuever TEXT,
            Spare_1 TEXT,
            Raim INTERGER,
            Radio INTERGER
        )
    ''') 
    conn.commit()
    print("DB created")
    with open(ais_file1, "r") as file:
        for line in file:
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
                    accuracyInt = int(bool(decoded.accuracy))
                    raimInt = int(bool(decoded.raim))
                    if(len(str(decoded.mmsi)) == 9):
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
                                        Logitude,
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
                                    int(decoded.accuracy),
                                    decoded.lon,
                                    decoded.lat,
                                    decoded.course,
                                    decoded.heading,
                                    decoded.second,
                                    decoded.maneuver,
                                    decoded.spare_1,
                                    int(decoded.raim),
                                    decoded.radio
                                )   
                            )
                                conn.commit()
                            except Exception as e:
                                print("Failed:")
                                print(nmea_sentence)
                                print(decoded)
                                print("Do to an error during SQL Insertion")
                                print(e)
                        else:
                            print("Skipped:")
                            print(nmea_sentence)
                            print(decoded)
                            print("Because field validation failed")
                    else:
                        print("Skipped:")
                        print(nmea_sentence)
                        print(decoded)
                        print("Because it has an invalid mssi")
                except Exception as e:
                    print("Failed to decode:", nmea_sentence)
                    print("Error:", e)
                    print("-" * 50)
        conn.close()


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
    

print("file 1")
print("--------------------------------------------------")
Decode_file1()
print("file 2")
print("--------------------------------------------------")
Decode_file2()