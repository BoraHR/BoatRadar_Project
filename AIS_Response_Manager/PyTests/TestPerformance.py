import pytest
import os
import sys
from tkinter import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import AIS_ResponderManager
from AIS_ResponderManager import AIS_ResponderManager
from test_pyais_decoder import DB_Exists, Decode_file, Save_DecodedData

from RadarConsole import RadarConsole
from RadarPlotter import RadarPlotter
from RadarDrawing import RadarDrawing

def ProgramForEachTest():
    Save_DecodedData()
    AIS_ResponderManager.FileRoute_sql3
    # assert f"PyTests/MockData/AIS-Responder({db_ID}).db" == os.path.abspath(mock_db)

    # remove old test db if it exists
    # if os.path.exists(mock_db):
    #     os.remove(mock_db)

    testARM = AIS_ResponderManager(1, True)

    testDrawer = RadarDrawing()
    testPlotter = RadarPlotter()

    window = Tk()
    testConsole = RadarConsole(window)

    return testARM, testDrawer, testPlotter, testConsole

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
    assert testARM.DB_Exists() == False


# def test_initialize_repeat():