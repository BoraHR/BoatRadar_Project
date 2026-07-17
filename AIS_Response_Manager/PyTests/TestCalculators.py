import pytest # https://docs.pytest.org/en/stable/
import sys
import os
import math

# Add parent directory to path to import pyais_decoder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Algorithm import km_to_lat_deg, km_to_lon_deg, ConvertToX_Y, bearing_deg, haversine, velocity_vector, calculate_cpa_tcpa

# -----------------------------
# lat_conversion tests
# -----------------------------

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

# -----------------------------
# lon_conversion tests
# -----------------------------

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

# -----------------------------
# ConvertToX_Y tests
# -----------------------------

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


def test_convert_x_positive_when_moving_east():
    x, y, _ = ConvertToX_Y(52.0, 5.0, 52.0, 6.0)

    # function subtracts coordinates internally
    assert x < 0

def test_convert_y_positive_when_moving_south():
    x, y, _ = ConvertToX_Y(53.0, 5.0, 52.0, 5.0)

    assert y > 0

# -----------------------------
# bearing_deg tests
# -----------------------------

def test_bearing_north():
    b = bearing_deg(52.0, 5.0, 53.0, 5.0)
    assert pytest.approx(b, abs=1) == 0

def test_bearing_east():
    b = bearing_deg(52.0, 5.0, 52.0, 6.0)
    assert pytest.approx(b, abs=1) == 90

def test_bearing_south():
    b = bearing_deg(53.0, 5.0, 52.0, 5.0)
    assert pytest.approx(b, abs=1) == 180

def test_bearing_west():
    b = bearing_deg(52.0, 6.0, 52.0, 5.0)
    assert pytest.approx(b, abs=1) == 270


# -----------------------------
# haversine tests
# -----------------------------

def test_haversine_same_point():
    d = haversine(52.0, 5.0, 52.0, 5.0)
    assert pytest.approx(d, abs=1e-9) == 0

def test_haversine_known_lat_distance():
    """
    1 degree latitude ≈ 111 km
    """
    d = haversine(52.0, 5.0, 53.0, 5.0)

    assert 110 < d < 112

def test_haversine_symmetry():
    d1 = haversine(52.0, 5.0, 53.0, 6.0)
    d2 = haversine(53.0, 6.0, 52.0, 5.0)

    assert pytest.approx(d1, rel=1e-9) == d2

# -----------------------------
# velocity_vector tests
# -----------------------------

def test_velocity_vector_north():
    vx, vy = velocity_vector(10, 0)

    assert pytest.approx(vx, abs=1e-6) == 0
    assert vy > 0

def test_velocity_vector_east():
    vx, vy = velocity_vector(10, 90)

    assert vx > 0
    assert pytest.approx(vy, abs=1e-6) == 0

def test_velocity_vector_speed_conversion():
    """
    1 knot = 0.514444 m/s
    """
    vx, vy = velocity_vector(1, 0)

    assert pytest.approx(vy, rel=1e-6) == 0.514444

# -----------------------------
# CPA / TCPA tests
# -----------------------------

def test_cpa_parallel_same_speed():
    """
    Same course and speed => no relative velocity
    """
    cpa, tcpa = calculate_cpa_tcpa(
        0, 0, 10, 0,
        1000, 0, 10, 0
    )

    assert cpa is None
    assert tcpa is None

def test_cpa_head_on_collision():
    """
    Ships moving directly toward each other.
    CPA should be ~0.
    """
    cpa, tcpa = calculate_cpa_tcpa(
        0, 0, 10, 90,
        1000, 0, 10, 270
    )

    assert cpa < 1e-6
    assert tcpa > 0

def test_cpa_already_past_each_other():
    """
    TCPA negative means closest point was in the past.
    """
    cpa, tcpa = calculate_cpa_tcpa(
        0, 0, 10, 90,
        -1000, 0, 10, 270
    )

    assert tcpa < 0

# -----------------------------
# Edge cases
# -----------------------------

def test_lon_conversion_near_pole():
    """
    Longitude degrees become very large near poles.
    """
    result = km_to_lon_deg(1, 89.999)

    assert math.isfinite(result)
    assert result > 100

def test_haversine_large_distance():
    """
    Roughly half Earth circumference.
    """
    d = haversine(0, 0, 0, 180)

    assert 20000 < d < 20150