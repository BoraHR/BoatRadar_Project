import os
import sqlite3
from Algorithm import haversine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder.db")

class AIS_ResponderManager:
    def __init__(self, _USER_ID):
        self.USER_ID = _USER_ID # Refrence to self.
        self.Create_Table()

    def DB_Exists(self):
        if os.path.exists(FileRoute_sql3):
            return True
        return False
    
    def Create_Table(self):
        if self.DB_Exists():
            try:
                conn = sqlite3.connect(FileRoute_sql3)
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS AIS_SubData (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        distance REAL,
                        CPA REAL,
                        TCPA REAL,
                        Boat_ID INTEGER UNIQUE,
                        FOREIGN KEY (Boat_ID) REFERENCES AIS_Decoder(id) 
                    )
                '''
                )
                conn.commit()
                c.execute('''
                    INSERT INTO AIS_SubData (Boat_ID)
                    VALUES (?)
                    ON CONFLICT(Boat_ID)
                    DO UPDATE SET
                        Boat_ID = excluded.Boat_ID
                ''',
                    (self.USER_ID,)
                )
                conn.commit()
            except Exception as e:
                print("Error during AIS_SubData update:")
                print(e)
        else:
            print("AIS-Responder.db not found")
        
    def Update_SubData_With_Tuple(self, data):
        if self.DB_Exists():
            try:
                conn = sqlite3.connect(FileRoute_sql3)
                c = conn.cursor()
                conn = sqlite3.connect(FileRoute_sql3)
                c = conn.cursor()
                count = c.execute('''
                    INSERT INTO AIS_SubData (distance, CPA, TCPA)
                    VALUES (?, ?, ?)
                    ON CONFLICT(Boat_ID)
                    DO UPDATE SET
                        distance = excluded.distance,
                        CPA = excluded.CPA,
                        TCPA = excluded.TCPA
                ''',
                (
                    # True == 1, False == 0
                    data[0],
                    data[1],
                    data[2],
                    data[3]
                )   
                )
                conn.commit()
                conn.close()
                # print("AIS_Render_History.DB created")
            except Exception as e:
                print("Error during AIS_SubData update:")
                print(e)
        else:
            print("AIS-Responder.db not found")

    def Update_SubData_With_Value(self, Boat_ID, distance, CPA, TCPA):
        if self.DB_Exists():
            try:
                conn = sqlite3.connect(FileRoute_sql3)
                c = conn.cursor()
                conn = sqlite3.connect(FileRoute_sql3)
                c = conn.cursor()
                c.execute('''
                    INSERT INTO AIS_SubData (Boat_ID ,distance, CPA, TCPA)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(Boat_ID)
                    DO UPDATE SET
                        distance = excluded.distance,
                        CPA = excluded.CPA,
                        TCPA = excluded.TCPA
                ''',
                (
                    # True == 1, False == 0
                    Boat_ID,
                    distance,
                    CPA,
                    TCPA
                )   
                )
                conn.commit()
                conn.close()
                # print("AIS_Render_History.DB created")
            except Exception as e:
                print("Error during AIS_SubData update:")
                print(e)
        else:
            print("AIS-Responder.db not found")

# ARM = AIS_ResponderManager(1)
# ARM.Create_Table()
        