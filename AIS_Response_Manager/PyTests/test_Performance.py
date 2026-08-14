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
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import AIS_ResponderManager
from AIS_ResponderManager import AIS_ResponderManager
from test_pyais_decoder import DB_Exists, Save_DecodedData
from Algorithm import haversine, bearing_deg, ConvertToX_Y, velocity_vector, calculate_cpa_tcpa, km_to_lat_deg, km_to_lon_deg

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
    testPlotter = RadarPlotter(True)

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
    testARM, testDrawer, testPlotter, testConsole = ProgramForEachTest(4)

    assert testARM is not None
    assert testDrawer is not None
    assert testPlotter is not None
    assert testConsole is not None

    # DB already exists because constructor creates it
    assert testARM.DB_Exists() == True
    print("\n")
    print(f"---- SQL initilize ---- ")
    start = time.perf_counter()
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    boat = get_self(c)
    end = time.perf_counter()
    result = end - start
    print(f"Result: {result:.40f}")
    conn.close()
    assert result < 0.05
    assert boat != None
    assert boat[0] == 1
    testConsole.window.destroy()
    

def test_SQL_retrieve_all_bb():
    print("\n")
    print(f"---- SQL GET ALL BOATS WITH CONNECT ---- ")
    start = time.perf_counter()
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    boats = get_all_boats(c)
    end = time.perf_counter()
    result = end - start
    print(f"Result: {result:.40f}")
    print(f"Count: {len(boats)}")
    assert result < 0.05
    assert len(boats) == 750
    print("\n")
    print(f"---- SQL GET ALL BOATS WHILE CONNECTED ---- ")
    # retry without clossing
    start = time.perf_counter()
    boats = get_all_boats(c)
    end = time.perf_counter()
    result = end - start
    print(f"Result (Connected): {result:.40f}")
    print(f"Count (Connected): {len(boats)}")
    conn.close()
    assert result < 0.025
    assert len(boats) == 750
    time.sleep(0.01)

def test_SQL_retrieve_all_with_foreachLoop():
    print("\n")
    print(f"---- SQL GET ALL BOATS + foreachLoop ---- ")
    start = time.perf_counter()
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    boats = get_all_boats(c)
    count = 0
    max = 0.000
    min = 2147483647.000
    total = 0.000
    for boat in boats:
        count += 1
    conn.close()
    end = time.perf_counter()
    result = end - start
    print(f"Result: {result:.40f}")
    print(f"ListCount: {len(boats)}")
    print(f"LoopCount: {count}")
    assert result < 0.05
    assert len(boats) == 750
    assert count == 750

def test_SQL_update_SubData():
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    testARM, testDrawer, testPlotter, testConsole = ProgramForEachTest(4)
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    count = 0
    max = 0.000
    min = 2147483647.000
    total = 0.000
    myBoat = get_self(c)
    boats = get_all_boats(c)
    
    for boat in boats:
        distance = haversine(myBoat[10], myBoat[9], boat[10], boat[9])
        X_Y = ConvertToX_Y(myBoat[10], myBoat[9], boat[10], boat[9]) # tuple(X, Y, Distance)
        cpa, tcpa = calculate_cpa_tcpa(
            0, 0, myBoat[7], myBoat[12],
            X_Y[0], X_Y[1], boat[7], boat[12]
        )
        brg = bearing_deg(myBoat[10], myBoat[9], boat[10], boat[9])
        start = time.perf_counter()
        testARM.Update_SubData_With_Value(conn, boat[0], distance, cpa, tcpa, brg)
        end = time.perf_counter()
        result = end - start
        if result > max:
            max = result
        if result < min:
            min = result
        total += result
        count += 1
    GetResults_WithTargets("SQL UPDATE SUBDATA", count, total, max, min, 750, 0.09, 0.003, 0.65, False)
    conn.close()
    testConsole.window.destroy()
    time.sleep(0.05)

def test_lat_long_algorithm_speed():
    i = 1
    max = 0.000
    min = 2147483647.000
    total = 0.000
    count = 0
    while i < 750:
        start = time.perf_counter()
        lat = km_to_lat_deg(i)
        lon = km_to_lon_deg(i, lat)
        end = time.perf_counter()
        result = end - start
        if result > max:
            max = result
        if result < min:
            min = result
        total += result
        count += 1
        i += 1
    GetResults("LAT_LON_PERFORMANCE", count, total, max, min)
    time.sleep(0.05)

def test_vector_calculation_speed():
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    testARM, testDrawer, testPlotter, testConsole = ProgramForEachTest(4)
    myBoat = testConsole.get_boat_data(1)
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    i = 1
    max = 0.000
    min = 2147483647.000
    total = 0.000
    count = 0
    otherBoats = get_all_boats(c, 1)
    for b in otherBoats:
        start = time.perf_counter()
        var =  velocity_vector(b[7], b[12])# function
        end = time.perf_counter()
        result = end - start
        if result > max:
            max = result
        if result < min:
            min = result
        total += result
        count += 1
    
    GetResults("VECTOR_CALLCULATION (calculate_cpa_tcpa helper)", count, total, max, min)
    testConsole.window.destroy()
    time.sleep(0.05)

def test_convertX_Y_algorithm_speed():
    run_algorithm_speed_test("X_Y_CONVERSION (calculate_cpa_tcpa helper)", ConvertToX_Y)

def test_calculate_cpa_tcpa():
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    testARM, testDrawer, testPlotter, testConsole = ProgramForEachTest(4)
    myBoat = testConsole.get_boat_data(1)
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    i = 1
    max = 0.000
    min = 2147483647.000
    total = 0.000
    count = 0

    otherBoats = get_all_boats(c, 1)
    for b in otherBoats:
        start = time.perf_counter()
        X_Y = ConvertToX_Y(myBoat[10], myBoat[9], b[10], b[9])
        var = calculate_cpa_tcpa(
            0, 0, myBoat[7], myBoat[12],
            X_Y[0], X_Y[1], b[7], b[12]
        ) # function
        end = time.perf_counter()
        result = end - start
        if result > max:
            max = result
        if result < min:
            min = result
        total += result
        count += 1

    GetResults("CALCULATE_CPA_TCPA", count, total, max, min)
    testConsole.window.destroy()
    time.sleep(0.05)

def test_haversine_algorithm_speed():
    run_algorithm_speed_test("HAVERSINE", haversine)
    time.sleep(0.05)

def test_bearing_algorithm_speed():
    run_algorithm_speed_test("BEARING", bearing_deg)
    time.sleep(0.05)

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
    testConsole.window.destroy()
    time.sleep(0.05)

def test_ImgSave_JustSelf_3KM():
    ImageSaveLoop("RADAR LOOP NO TARGETS 3km", 3, False)

def test_ImgSave_JustSelf_6KM():
    ImageSaveLoop("RADAR LOOP NO TARGETS 6km", 6, False)

def test_ImgSave_JustSelf_9KM():
    ImageSaveLoop("RADAR LOOP NO TARGETS 9km", 9, False)

def test_ImgSave_JustSelf_12KM():
    ImageSaveLoop("RADAR LOOP NO TARGETS 12km", 12, False)

def test_ImgSave_WithTargets_3KM():
    ImageSaveLoop("RADAR LOOP WITH TARGETS 3km", 3, True)

def test_ImgSave_WithTargets_6KM():
    ImageSaveLoop("RADAR LOOP WITH TARGETS 6km", 6, True)

def test_ImgSave_WithTargets_9KM():
    ImageSaveLoop("RADAR LOOP WITH TARGETS 9km", 9, True)

def test_ImgSave_WithTargets_12KM():
    ImageSaveLoop("RADAR LOOP WITH TARGETS 12km", 12, True)


def ImageSaveLoop(testname, KM, IncludeTargets):
    test_FileRoute_sql3 = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    testARM, testDrawer, testPlotter, testConsole = ProgramForEachTest(4)
    testConsole.set_B_primary(144)
    testConsole.set_R_primary(144)
    testConsole.set_G_primary(144)
    testDrawer.setBGColor_RGB(testConsole.RGB_Pri[0], testConsole.RGB_Pri[1], testConsole.RGB_Pri[2]) # background
    # testDrawer.img_loc = os.path.join(BASE_DIR, f"Radar/Renders/imgTest.png")
    myBoat = testConsole.get_boat_data(46)
    conn = sqlite3.connect(test_FileRoute_sql3)
    c = conn.cursor()
    targets = []
    if IncludeTargets:
        testPlotter.InRangeHelper(46, KM)
    max = 0.000
    min = 2147483647.000
    total = 0.000
    count = 0
    i = 0
    print("\n Testing image loop...")
    while i < 21:
        start = time.perf_counter()
        if not IncludeTargets:
            testDrawer.draw_radar_Custom(KM, 0.00, 2.0)
        testPlotter.plot_boats(myBoat)
        testDrawer.SaveImg()
        end = time.perf_counter()
        # the first index is always None value for img_RAM and should be ignored
        if i != 0:
            assert testDrawer.img_RAM != None
            result = end - start
            if result > max:
                max = result
            if result < min:
                min = result
            total += result
            count += 1 
        i += 1
    
    if IncludeTargets:
        GetResults_WithTargets(testname, count, total, max, min, 20, 1.2, 0.6, 12.00)
    else:
        GetResults_WithTargets(testname, count, total, max, min, 20, 1.0, 0.5, 10.00)
    while testConsole.plotter.draw._save_thread != None:
        pass
    testConsole.CleanFiles() # clean PostScript files for next run
    testConsole.window.destroy()

def GetResults(testname, count, total, max, min):
    avr = total / count
    print("\n")
    print(f"---- {testname.upper()} ---- ")
    print(f"Count: {count}")
    print(f"Total: sec{total:.40f}, ms{1000*total:.40f}")
    print(f"Max: sec{max:.40f}, ms{1000*max:.40f}")
    print(f"Min: sec{min:.40f}, ms{1000*min:.40f}")
    print(f"Avr: sec{avr:.40f}, ms{1000*avr:.40f}")
    assert count == 749
    assert max < 0.03
    assert min != 2147483647.000
    assert avr < 0.001
    assert total < 0.01

def GetResults_WithTargets(testname, count, total, max, min, TargetCount, TargetMax, TargetAvr, TargetTotal, ShowFPS=True):
    avr = total / count
    print("\n")
    print(f"---- {testname.upper()} ---- ")
    print(f"Count: {count}")
    print(f"Total: sec{total:.40f}, ms{1000*total:.40f}")
    if ShowFPS:
        print(f"Max: sec{max:.40f}, ms{1000*max:.40f}, FPS({get_FPS(max)})")
        print(f"Min: sec{min:.40f}, ms{1000*min:.40f}, FPS({get_FPS(min)})")
        print(f"Avr: sec{avr:.40f}, ms{1000*avr:.40f}, FPS({get_FPS(avr)})")
    else:
        print(f"Max: sec{max:.40f}, ms{1000*max:.40f}")
        print(f"Min: sec{min:.40f}, ms{1000*min:.40f}")
        print(f"Avr: sec{avr:.40f}, ms{1000*avr:.40f}")
    assert count == TargetCount
    assert max < TargetMax
    assert min != 2147483647.000
    assert avr < TargetAvr
    assert total < TargetTotal

def get_FPS(seconds):
    return math.floor(1 / seconds)