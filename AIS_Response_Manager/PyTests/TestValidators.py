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