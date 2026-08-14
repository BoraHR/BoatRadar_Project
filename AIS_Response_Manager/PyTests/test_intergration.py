import time
import os
import sys
# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from RadarPlotter import RadarPlotter
from Algorithm import miles_to_km
from test_pyais_decoder import DB_Exists, Save_DecodedData

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def test_integration_plotter_with_mock_db():
    test_AIS_file = os.path.join(BASE_DIR, "Pytests/MockData/ais_all.txt")
    if DB_Exists() == False:
        Save_DecodedData(test_AIS_file)
    plotter = RadarPlotter(IsTest=True)
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    assert plotter.RadarConsoleData

    while plotter.draw.img_RAM is None and plotter.draw._save_thread is not None and plotter.draw._save_thread.is_alive():
        time.sleep(0.05)
    
    assert plotter.draw.img_RAM is not None


def test_miles_mode_range_is_converted_to_km_before_filtering():
    test_AIS_file = os.path.join(BASE_DIR, "Pytests/MockData/ais_all.txt")
    if DB_Exists() == False:
        Save_DecodedData(test_AIS_file)
    plotter = RadarPlotter(IsTest=True)
    plotter.IsKM = False
    plotter.InRangeHelper(plotter.ID, range=1, timeWindow=10)

    assert plotter.RadarConsoleData
    for row in plotter.RadarConsoleData:
        distance_km = row[2]
        assert distance_km <= miles_to_km(1) + 1e-9