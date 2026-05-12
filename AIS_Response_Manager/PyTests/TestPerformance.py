# performance tests require prints execute given instructions,
# 1. Assuming you use VSC, Rightclick on PyTests in explorer and select "Open Intergrated Terminal"
# 2. Use fellowing command "pytest -s TestPerformance.py"
# 3. If you launch test for first time it might take some time to insert AIS Data, this can take a few minutes.

from decimal import Decimal
import sqlite3
import shutil
import pytest
import os
import sys
from tkinter import *
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import AIS_ResponderManager
from AIS_ResponderManager import AIS_ResponderManager
from test_pyais_decoder import DB_Exists, Decode_file, Save_DecodedData
from Algorithm import haversine, bearing_deg, ConvertToX_Y

from RadarConsole import RadarConsole
from RadarPlotter import RadarPlotter
from RadarDrawing import RadarDrawing

def get_self(c):
    return c.execute('''
        SELECT *
        FROM AIS_Decoder
        WHERE id = ?
    ''', (1,)).fetchone()

def get_all_boats(c, ignore = -1):
    return c.execute('''
        SELECT *
        FROM AIS_Decoder
        WHERE id != ?
    ''', (ignore,)).fetchall()

def ProgramForEachTest(size = 0):
    test_AIS_file = os.path.join(BASE_DIR, "Pytests/MockData/ais_NONE.txt")
    if size == 1:
        test_AIS_file = os.path.join(BASE_DIR, "Pytests/MockData/ais_small.txt")
    elif size == 2:
        test_AIS_file = os.path.join(BASE_DIR, "Pytests/MockData/ais_moderate.txt")
    elif size == 3:
        test_AIS_file = os.path.join(BASE_DIR, "Pytests/MockData/ais_large.txt")
    elif size == 4:
        test_AIS_file = os.path.join(BASE_DIR, "Pytests/MockData/ais_all.txt")
    
    if DB_Exists() == False:
        Save_DecodedData(test_AIS_file)
    testARM = AIS_ResponderManager(1, True)

    testDrawer = RadarDrawing()
    testPlotter = RadarPlotter()

    window = Tk()
    testConsole = RadarConsole(window, True)

    return testARM, testDrawer, testPlotter, testConsole

def DB_Exists():
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "Pytests/MockData/AIS-Responder.db")
    if os.path.exists(test_FileRoute_sql3):
        return True
    return False

def ClearDB():
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "Pytests/MockData/AIS-Responder.db")
    if os.path.exists(test_FileRoute_sql3):
        os.remove(test_FileRoute_sql3)

def test_initialize():
    testARM, testDrawer, testPlotter, testConsole = ProgramForEachTest()

    assert testARM is not None
    assert testDrawer is not None
    assert testPlotter is not None
    assert testConsole is not None

    # DB already exists because constructor creates it
    assert testARM.DB_Exists() == True


def test_convertX_Y_algorithm_speed():
    run_algorithm_speed_test("X_Y_CONVERSION", ConvertToX_Y)

def test_haversine_algorithm_speed():
    run_algorithm_speed_test("HAVERSINE", haversine)

def test_bearing_algorithm_speed():
    run_algorithm_speed_test("BEARING", bearing_deg)

def run_algorithm_speed_test(testname, algorithm):
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    testARM, testDrawer, testPlotter, testConsole = ProgramForEachTest(4)
    myBoat = testConsole.get_boat_data(1)
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    max = 0.000
    min = 2147483647.000
    total = 0.000
    count = 0
    otherBoats = get_all_boats(c, 1)
    for b in otherBoats:
        start = time.perf_counter()
        var = algorithm(myBoat[9], myBoat[10], b[9], b[10]) # function
        end = time.perf_counter()
        result = end - start
        if result > max:
            max = result
        if result < min:
            min = result
        total += result
        count += 1
    GetResults(testname, count, total, max, min)

def GetResults(testname, count, total, max, min):
    avr = total / count
    print("\n")
    print(f"---- {testname.upper()} ---- ")
    print(f"Count: {count}")
    print(f"Total: {total:.40f}")
    print(f"Max: {max:.40f}")
    print(f"Min: {min:.40f}")
    print(f"Avr: {avr:.40f}")
    assert count == 749
    assert max < 0.001
    assert min != 2147483647.000
    assert avr < 0.0001
    assert total < 0.01


    
# def test_initialize_repeat():