import os
import sqlite3

# Folder where THIS python file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FileRoute_sql3 = os.path.join(BASE_DIR, "AIS-Responder_DB.db")

def CreateDB():
    if not os.path.exists(FileRoute_sql3):
        conn = sqlite3.connect(FileRoute_sql3)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS AIS_Responder (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                Msii TEXT,
                Flag TEXT,
                Class TEXT,
                N TEXT,
                W TEXT,
                ReportAge TEXT,
                Speed TEXT,
                Course TEXT,
                Heading TEXT,
                Range TEXT,
                Bearing TEXT,
                TurnRate TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("DB created")
    else:
        print("DB already exists")

def AddRowDB():
    shipName = input("Name: ")
    mssi = input("MSII: ")
    flag = input("Flag: ")
    boatClass = input("Class: ")
    n = input("N: ")
    w = input("W: ")
    reportAge = input("ReportAge (default = 0s): ")
    if reportAge == "":
        reportAge = "0s"
    speed = input("Speed: ")
    course = input("Course: ")
    heading = input("Heading: ")
    range_val = input("Range: ")
    bearing = input("Bearing: ")
    turnRate = input("TurnRate: ")
    if shipName == "":
        shipName = None
    if mssi == "":
        mssi = None
    if flag == "":
        flag = None
    if boatClass == "":
        boatClass = None
    if n == "":
        n = None
    if w == "":
        w = None
    if speed == "":
        speed = None
    if course == "":
        course = None
    if heading == "":
        heading = None
    if range_val == "":
        range_val = None
    if bearing == "":
        bearing = None
    if turnRate == "":
        turnRate = None

    if os.path.exists(FileRoute_sql3):
        try:
            conn = sqlite3.connect(FileRoute_sql3)
            c = conn.cursor()
            c.execute('''INSERT INTO AIS_Responder
                (
                    Name, 
                    Msii, 
                    Flag,
                    Class,
                    N,
                    W,
                    ReportAge,
                    Speed,
                    Course,
                    Heading,
                    Range,
                    Bearing,
                    TurnRate
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                shipName,
                mssi,
                flag,
                boatClass,
                n,
                w,
                reportAge,
                speed,
                course,
                heading,
                range_val,
                bearing,
                turnRate
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error inserting data:")
            print(e)

def DeleteByID(_id):  
    try:
        id = int(_id)
    except ValueError:
        print("Invalid input: cannot convert to integer")
        print("Deletion failed")
        return

    try:
        conn = sqlite3.connect(FileRoute_sql3)
        c = conn.cursor()
        check = c.execute('''
        SELECT * FROM AIS_Responder WHERE id = ?
        ''', (id,)).fetchone()
        if(check != None):
            choice = " "
            print(check)
            while(choice[0] != 'Y' and choice[0] != 'N'):
                choice = input("are you sure you want to DELETE this data? Its not reverseble. (Y (yes)/N (No)) ").upper()
                # reset choice to prefent exeption if blank
                if choice == "":
                    choice = " "
                    continue
                # confirm input
                if choice[0] == 'Y':
                    c.execute(''' 
                    DELETE FROM AIS_Responder WHERE id = ?
                    ''', (id,))
                    conn.commit()
                    conn.close()
                    print("Deletion succes")
                    return
                print("Deletion cancelled")
                conn.close()
                return
        print(f"id {id} not found")
        print("Deletion cancelled")
        conn.close()
    except Exception as e:
        print("sqlite3 operation failed:")
        print(e)
        print("Deletion failed")

def SearchByMSSI(mssi):
    try:
        conn = sqlite3.connect(FileRoute_sql3)
        c = conn.cursor()
        boat = c.execute('''
        SELECT * FROM AIS_Responder WHERE Msii = ?
        ''', (mssi,)).fetchone()
        if boat != None:
            print(boat)
        else:
            print(f"no boat found with MSSI: {mssi}")
        input("ENTER to continue")

    except Exception as e:
        print("sqlite3 operation failed:")
        print(e)
        print("fetch failed")

CreateDB()
mssi = input("MSSI: ")
SearchByMSSI(mssi)