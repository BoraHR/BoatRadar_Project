import time
import os
import sys
# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from RadarPlotter import RadarPlotter

def test_integration_plotter_with_mock_db():
    plotter = RadarPlotter(IsTest=True)
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    assert plotter.RadarConsoleData

    while plotter.draw.img_RAM is None and plotter.draw._save_thread is not None and plotter.draw._save_thread.is_alive():
        time.sleep(0.05)
    
    assert plotter.draw.img_RAM is not None