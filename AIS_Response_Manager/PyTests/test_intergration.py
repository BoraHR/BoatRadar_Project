import time
import os
import sys

import pytest
# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from RadarPlotter import RadarPlotter
from Algorithm import miles_to_km
from test_pyais_decoder import DB_Exists, Save_DecodedData

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

@pytest.fixture(autouse=True)
def setup_clean_mock_db():
    """Ensures a 100% fresh mock database before the test runs."""
    test_db_path = os.path.join(BASE_DIR, "PyTests/MockData/AIS-Responder.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path) # Wipe stale data
        
    test_AIS_file = os.path.join(BASE_DIR, "PyTests/MockData/ais_all.txt")
    Save_DecodedData(test_AIS_file) # Seed fresh data
    yield

def test_integration_plotter_with_mock_db():
    plotter = RadarPlotter(IsTest=True)
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    assert plotter.RadarConsoleData

    while plotter.draw.img_RAM is None and plotter.draw._save_thread is not None and plotter.draw._save_thread.is_alive():
        time.sleep(0.05)

    assert plotter.draw.img_RAM is not None
    time.sleep(0.05)
    ps1 = os.path.join(BASE_DIR, "Radar/PostScript/drawing(0).ps") 
    ps2 = os.path.join(BASE_DIR, "Radar/PostScript/drawing(1).ps") 
    with open(ps1, "r", encoding="utf-8") as file1:
        with open(ps2, "r", encoding="utf-8") as file2:
            lines1 = file1.readlines()
            lines2 = file2.readlines()
            assert len(lines1) == len(lines2) # if they are exact same image both postscripts have same amount of lines
            i = 0
            # Creation dates are always different so exclude them
            while i < len(lines1):
                if not lines1[i].contains("%%CreationDate") and not lines2[i].contains("%%CreationDate"):
                    lines1[i] == lines2[i]
                i = i + 1
            




def test_miles_mode_range_is_converted_to_km_before_filtering():
    plotter = RadarPlotter(IsTest=True)
    plotter.IsKM = False
    plotter.InRangeHelper(plotter.ID, range=1, timeWindow=10)

    assert plotter.RadarConsoleData
    for row in plotter.RadarConsoleData:
        distance_km = row[2]
        assert distance_km <= miles_to_km(1) + 1e-9