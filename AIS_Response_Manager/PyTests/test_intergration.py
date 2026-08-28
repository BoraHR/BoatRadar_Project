import time
import os
import sys
import sqlite3
from concurrent.futures import ThreadPoolExecutor


import pytest
# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from RadarPlotter import RadarPlotter
from Algorithm import miles_to_km
from Algorithm import calculate_cpa_tcpa
from test_pyais_decoder import DB_Exists, Save_DecodedData
from AIS_ResponderManager import AIS_ResponderManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

@pytest.fixture(scope="session", autouse=True)
def setup_clean_mock_db():
    """Create a fresh mock database once before the test session."""

    test_db_path = os.path.join(
        BASE_DIR,
        "PyTests/MockData/AIS-Responder.db"
    )

    test_AIS_file = os.path.join(
        BASE_DIR,
        "PyTests/MockData/ais_all.txt"
    )
    conn = None

    # Remove old test database
    try:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    

        # Create AIS_Decoder table and populate it
        Save_DecodedData(test_AIS_file)

        # Create the additional table required by AIS_ResponderManager
        with sqlite3.connect(test_db_path) as conn:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS AIS_SubData (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    distance REAL,
                    CPA REAL,
                    TCPA REAL,
                    BRG REAL,
                    Boat_ID INTEGER UNIQUE,
                    FOREIGN KEY (Boat_ID) REFERENCES AIS_Decoder(id)
                )
            """)

            conn.commit()

    except Exception as e:
            print("Failed mock database(re)creation:")
            print(e)
    finally:
        if conn is not None:
            conn.close()
    yield

def wait_for_image(plotter, timeout=5.0):
    start = time.time()

    while time.time() - start < timeout:
        if plotter.draw.img_RAM is not None:
            return

        if (
            plotter.draw._save_thread is not None
            and not plotter.draw._save_thread.is_alive()
        ):
            break

        time.sleep(0.01)

    assert plotter.draw.img_RAM is not None

def test_mock_database_contains_required_tables():
    db_path = os.path.join(
        BASE_DIR,
        "PyTests/MockData/AIS-Responder.db"
    )

    with sqlite3.connect(db_path) as conn:
        tables = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """).fetchall()

    table_names = {table[0] for table in tables}

    assert "AIS_Decoder" in table_names
    assert "AIS_SubData" in table_names

def test_integration_plotter_with_mock_db():
    test_AIS_file = os.path.join(BASE_DIR, "PyTests/MockData/ais_all.txt")
    plotter = RadarPlotter(IsTest=True)
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    assert plotter.RadarConsoleData

    while plotter.draw.img_RAM is None and plotter.draw._save_thread is not None and plotter.draw._save_thread.is_alive():
        time.sleep(0.05)
    
    assert plotter.draw.img_RAM is not None
            

def test_miles_mode_range_is_converted_to_km_before_filtering():
    plotter = RadarPlotter(IsTest=True)
    plotter.IsKM = False
    plotter.InRangeHelper(plotter.ID, range=1, timeWindow=10)

    assert plotter.RadarConsoleData
    for row in plotter.RadarConsoleData:
        distance_km = row[2]
        assert distance_km <= miles_to_km(1) + 1e-9


def test_realtime_database_update_is_used_by_next_refresh():
    plotter = RadarPlotter(IsTest=True)
    original_speed = plotter.GetBoat(plotter.ID)[7]
    updated_speed = original_speed + 1.0

    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    with sqlite3.connect(plotter.FileRoute_sql3) as connection:
        connection.execute(
            "UPDATE AIS_Decoder SET Speed = ? WHERE id = ?",
            (updated_speed, plotter.ID),
        )
        connection.commit()

    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)

    assert plotter.GetBoat(plotter.ID)[7] == pytest.approx(updated_speed)


def test_multiple_radar_refreshes_keep_rendering_images():
    plotter = RadarPlotter(IsTest=True)

    for _ in range(5):
        plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
        wait_for_image(plotter)

        assert plotter.draw.img_RAM is not None
        assert plotter.RadarConsoleData


def test_simultaneous_cpa_tcpa_calculations_match_serial_results():
    calculations = [
        (0, 0, 10, 0, 1000, 500, 8, 180),
        (0, 0, 12, 90, -500, 1200, 6, 270),
        (0, 0, 5, 45, 800, -300, 9, 225),
        (0, 0, 15, 180, -700, -900, 11, 0),
    ]

    with ThreadPoolExecutor(max_workers=len(calculations)) as executor:
        parallel_results = list(
            executor.map(lambda values: calculate_cpa_tcpa(*values), calculations)
        )

    serial_results = [calculate_cpa_tcpa(*values) for values in calculations]

    assert parallel_results == pytest.approx(serial_results)


def test_rendering_with_multiple_targets_produces_radar_image():
    plotter = RadarPlotter(IsTest=True)

    plotter.InRangeHelper(plotter.ID, range=12, timeWindow=10)

    assert len(plotter.RadarConsoleData) > 1
    wait_for_image(plotter)
    assert plotter.draw.img_RAM is not None


def test_switching_radar_distances_updates_radar_scale():
    plotter = RadarPlotter(IsTest=True)

    plotter.InRangeHelper(plotter.ID, range=1, timeWindow=10)
    assert plotter.draw.KM_build == 1

    plotter.InRangeHelper(plotter.ID, range=6, timeWindow=10)
    assert plotter.draw.KM_build == 6
    assert plotter.draw.img_RAM is not None


def test_switching_day_and_night_mode_updates_render_configuration():
    plotter = RadarPlotter(IsTest=True)

    plotter.draw.setBGColor_RGB(144, 144, 144)
    plotter.draw.IsDark = False
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    wait_for_image(plotter)
    light_image = plotter.draw.img_RAM.copy()

    plotter.draw.setBGColor_RGB(0, 23, 68)
    plotter.draw.IsDark = True
    plotter.draw.KM_build = -1
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    wait_for_image(plotter)
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10) # the 2nd refresh is required for dark/day mode to apply
    wait_for_image(plotter)
    dark_image = plotter.draw.img_RAM.copy()

    plotter.draw.setBGColor_RGB(144, 144, 144)
    plotter.draw.IsDark = False
    plotter.draw.KM_build = -1
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10)
    wait_for_image(plotter)
    plotter.InRangeHelper(plotter.ID, range=3, timeWindow=10) # the 2nd refresh is required for dark/day mode to apply
    wait_for_image(plotter)
    light_image_2 = plotter.draw.img_RAM

    assert light_image.getpixel((0, 0)) != dark_image.getpixel((0, 0))
    assert light_image.getpixel((0, 0)) == light_image_2.getpixel((0, 0))