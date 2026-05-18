import pytest # https://docs.pytest.org/en/stable/
import sys
import os
import math

# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyais_decoder import ValidateDate, ValidateFields

def test_DateTest_True():

    valid_date_obj = [
        "2022-08-29T15:18:50.6538401+02:00",
        "2022-08-29T15:18:50.6979972+02:00",
        "2022-08-29T15:18:50.7891172+02:00",
        "2022-08-29T15:18:50.8061467+02:00",
        "2022-08-29T15:18:50.8125038+02:00"
    ]

    for iso_date in valid_date_obj:
        assert True == ValidateDate(iso_date)

def test_DateTest_False():

    invalid_date_obj = [
        "2022-08-29",
        "29-08-2022",
        "18:50.7891172+02:00",
        "T15:18:50.8061467+02:00",
        "8125038+02:00",
        # "2022-08-29T15",
        "18:50",
        "AIS 2022-08-29T15:18:50.8988418+02:00",
        "-1--01--29T15:18:50.9441802+02:00",
        "0-0-29T15:18:51.0177289+02:00",
        "2022-08-29T15:99:99.0980197+02:00",
    ]

    for iso_date in invalid_date_obj:
        assert False == ValidateDate(iso_date)

class MockDecoded:
    def __init__(
        self,
        msg_type=1,
        repeat=0,
        mmsi=123456789,
        status=0,
        turn=0,
        accuracy=True,
        lon=5.1214,
        lat=52.0907,
        course=180.0,
        heading=180,
        second=30,
        maneuver=0,
        spare_1=0,
        raim=False,
        radio=0
    ):
        self.msg_type = msg_type
        self.repeat = repeat
        self.mmsi = mmsi
        self.status = status
        self.turn = turn
        self.accuracy = accuracy
        self.lon = lon
        self.lat = lat
        self.course = course
        self.heading = heading
        self.second = second
        self.maneuver = maneuver
        self.spare_1 = spare_1
        self.raim = raim
        self.radio = radio


def test_ValidateFields_True():

    valid_objects = [
        MockDecoded(),
        MockDecoded(lon=0.0, lat=0.0),
        MockDecoded(lon=-180.0, lat=-90.0),
        MockDecoded(lon=180.0, lat=90.0, course=359.9, heading=359),
        MockDecoded(second=60),
    ]

    for obj in valid_objects:
        assert True == ValidateFields(obj)


def test_ValidateFields_False():

    invalid_objects = [
        MockDecoded(msg_type=None),
        MockDecoded(repeat=None),
        MockDecoded(mmsi=None),
        MockDecoded(status=None),
        MockDecoded(turn=None),
        MockDecoded(accuracy=None),
        MockDecoded(lon=None),
        MockDecoded(lat=None),
        MockDecoded(course=None),
        MockDecoded(heading=None),
        MockDecoded(second=None),
        MockDecoded(maneuver=None),
        MockDecoded(spare_1=None),
        MockDecoded(raim=None),
        MockDecoded(radio=None),

        # Invalid longitude
        MockDecoded(lon=180.1),

        # Invalid latitude
        MockDecoded(lat=90.1),
        MockDecoded(lat=-90.1),

        # Invalid course
        MockDecoded(course=360.0),
        MockDecoded(course=-1.0),

        # Invalid heading
        MockDecoded(heading=360),
        MockDecoded(heading=-1),

        # Invalid second
        MockDecoded(second=61),
        MockDecoded(second=-1),
    ]

    for obj in invalid_objects:
        assert False == ValidateFields(obj)