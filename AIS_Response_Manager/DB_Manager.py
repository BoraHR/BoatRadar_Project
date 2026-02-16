import os
import pandas as pd

FileRoute = 'AIS-Responder_Data.xlsx'

def GetCurrentDirectory():
    # used the startpoint of directory file search.
    print("Current working directory:")
    print(os.getcwd())

def ReadExcell():
    df = pd.read_excel(FileRoute) 
    print(df)
    
def ReadFirst5Rows():
    df = pd.read_excel(FileRoute) 
    print(df.head)

def ReadLast5Rows():
    df = pd.read_excel(FileRoute) 
    print(df.tail)

def AddRow():
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

    # Read existing file (or create empty if not exists)
    if os.path.exists(FileRoute):
        df_existing = pd.read_excel(FileRoute)
    else:
        df_existing = pd.DataFrame(columns=[
            "ID", "Name", "Msii", "Flag", "Class",
            "N", "W", "ReportAge", "Speed", "Course",
            "Heading", "Range", "Bearing", "TurnRate"
        ])

    # Generate new ID
    if df_existing.empty:
        new_id = 1
    else:
        new_id = df_existing["ID"].max() + 1

    # Create new row properly
    new_row = {
        "ID": new_id,
        "Name": shipName,
        "Msii": mssi,
        "Flag": flag,
        "Class": boatClass,
        "N": n,
        "W": w,
        "ReportAge": reportAge,
        "Speed": speed,
        "Course": course,
        "Heading": heading,
        "Range": range_val,
        "Bearing": bearing,
        "TurnRate": turnRate
    }

    df_new = pd.DataFrame([new_row])

    # Append safely (modern pandas way)Br
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    # Save
    df_combined.to_excel(FileRoute, index=False)

    print("Ship added successfully.")

def DropRow(_row):
    try:
        row = int(_row)
    except ValueError:
        print("Invalid input: cannot convert to integer")
        return
    
    if(row < 0):
        print("row index cant be negative")
        return

    if (os.path.exists(FileRoute) == False):
        print("File not found")
        return

    content = pd.read_excel(FileRoute)

     # Save deleted row for printing
    deleted_row = content.loc[row]

    # Drop row
    content = content.drop(row)

    # Save updated file
    content.to_excel(FileRoute, index=False)

    print("Deleted row:")
    print(deleted_row)

