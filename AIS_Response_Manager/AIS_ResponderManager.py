import os
import sqlite3
from Algorithm import haversine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FileRoute_sql3 = os.path.join(BASE_DIR, "Data/AIS-Responder.db")

class AIS_ResponderManager:
    def __init__(self, _USER_ID, IsTest = False):
        self.FileRoute_sql3 = FileRoute_sql3
        if IsTest:
            self.FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
            self.USER_ID = 1
        self.USER_ID = _USER_ID # Refrence to self.
        self.Create_Table()

    def DB_Exists(self):
        if os.path.exists(self.FileRoute_sql3):
            return True
        return False
    
    def Create_Table(self):
        if self.DB_Exists():
            try:
                conn = sqlite3.connect(self.FileRoute_sql3)
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS AIS_SubData (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        distance REAL,
                        CPA REAL,
                        TCPA REAL,
                        BRG REAL,
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
                conn.close()
        else:
            print("AIS-Responder.db not found")
        conn.close()
        
    def Update_SubData_With_Value(self, c, Boat_ID, distance, CPA, TCPA, BRG):
        if self.DB_Exists():
            try:
                # conn = sqlite3.connect(self.FileRoute_sql3)
                c.execute('''
                    INSERT INTO AIS_SubData (Boat_ID ,distance, CPA, TCPA, BRG)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(Boat_ID)
                    DO UPDATE SET
                        distance = excluded.distance,
                        CPA = excluded.CPA,
                        TCPA = excluded.TCPA,
                        BRG = excluded.BRG
                ''',
                (
                    Boat_ID,
                    distance,
                    CPA,
                    TCPA,
                    BRG
                )   
                )
                # print("AIS_Render_History.DB created")
            except Exception as e:
                print("Error during AIS_SubData update:")
                print(e)
        else:
            print("AIS-Responder.db not found")

        