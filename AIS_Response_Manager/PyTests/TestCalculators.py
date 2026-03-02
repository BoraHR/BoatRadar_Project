import pytest # https://docs.pytest.org/en/stable/
import sys
import os
import math

# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyais_decoder import km_to_lat_deg, km_to_lon_deg, ConvertToX_Y

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

def test_same_point_zero_distance():
    x, y, d = ConvertToX_Y(52.0, 5.0, 52.0, 5.0)
    assert pytest.approx(x, abs=1e-6) == 0
    assert pytest.approx(y, abs=1e-6) == 0
    assert pytest.approx(d, abs=1e-6) == 0


def test_return_types():
    result = ConvertToX_Y(52.0, 5.0, 53.0, 6.0)
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert all(isinstance(v, float) for v in result)


def test_symmetry_distance():
    """Distance should be same regardless of order."""
    _, _, d1 = ConvertToX_Y(52.0, 5.0, 53.0, 6.0)
    _, _, d2 = ConvertToX_Y(53.0, 6.0, 52.0, 5.0)

    assert pytest.approx(d1, rel=1e-9) == d2


def test_small_known_distance_latitude():
    """
    Moving 1 degree latitude ≈ 111 km
    """
    _, _, d = ConvertToX_Y(52.0, 5.0, 53.0, 5.0)

    assert 110000 < d < 112000  # meters


def test_small_known_distance_longitude():
    """
    Longitude distance depends on latitude.
    Around NL (~52°), 1 degree lon ≈ 68 km
    """
    _, _, d = ConvertToX_Y(52.0, 5.0, 52.0, 6.0)

    assert 65000 < d < 71000


def test_debug_flag_does_not_crash(capsys):
    ConvertToX_Y(52.0, 5.0, 52.1, 5.1, debug=True)
    captured = capsys.readouterr()
    assert "X =" in captured.out