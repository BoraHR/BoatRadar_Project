import pytest # https://docs.pytest.org/en/stable/
import sys
import os
import math

# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyais_decoder import km_to_lat_deg, km_to_lon_deg

def test_lat_conversion_basic():
    # 111 km ≈ 1 degree latitude
    result = km_to_lat_deg(111)
    assert result == pytest.approx(1.0, rel=1e-6)


def test_lat_conversion_zero():
    result = km_to_lat_deg(0)
    assert result == 0


def test_lat_conversion_negative():
    result = km_to_lat_deg(-111)
    assert result == pytest.approx(-1.0, rel=1e-6)


def test_lon_conversion_equator():
    # At equator cos(0)=1 → same as latitude conversion
    result = km_to_lon_deg(111, 0)
    assert result == pytest.approx(1.0, rel=1e-6)


def test_lon_conversion_mid_latitude():
    # At 60° latitude, longitude degrees shrink
    result = km_to_lon_deg(111, 60)
    expected = 111 / (111 * math.cos(math.radians(60)))
    assert result == pytest.approx(expected, rel=1e-6)


def test_lon_conversion_zero_distance():
    result = km_to_lon_deg(0, 45)
    assert result == 0


def test_lon_conversion_negative_distance():
    result = km_to_lon_deg(-111, 0)
    assert result == pytest.approx(-1.0, rel=1e-6)