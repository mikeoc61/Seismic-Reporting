"""Tests for seismic_reporting.haversine."""

from __future__ import annotations

import math

import pytest

from seismic_reporting.haversine import EARTH_RADIUS_KM, calc_dist


def test_zero_distance() -> None:
    """Identical coordinates yield zero distance."""
    assert calc_dist(19.64, -155.99, 19.64, -155.99) == pytest.approx(0.0, abs=1e-9)


def test_quarter_circumference() -> None:
    """Equator point to a pole is a quarter of the great circle."""
    expected = EARTH_RADIUS_KM * math.pi / 2
    assert calc_dist(0.0, 0.0, 90.0, 0.0) == pytest.approx(expected, rel=1e-9)


def test_antipodal() -> None:
    """Antipodal points are half the circumference apart."""
    expected = EARTH_RADIUS_KM * math.pi
    assert calc_dist(0.0, 0.0, 0.0, 180.0) == pytest.approx(expected, rel=1e-9)


def test_symmetry() -> None:
    """Distance is independent of argument order."""
    a = calc_dist(19.64, -155.99, 37.77, -122.42)
    b = calc_dist(37.77, -122.42, 19.64, -155.99)
    assert a == pytest.approx(b, rel=1e-12)


def test_custom_radius_scales_linearly() -> None:
    """Result scales linearly with the radius argument."""
    km = calc_dist(0.0, 0.0, 0.0, 1.0)
    half = calc_dist(0.0, 0.0, 0.0, 1.0, radius=EARTH_RADIUS_KM / 2)
    assert half == pytest.approx(km / 2, rel=1e-12)


def test_one_degree_of_latitude() -> None:
    """One degree of latitude is roughly 111 km."""
    assert calc_dist(0.0, 0.0, 1.0, 0.0) == pytest.approx(111.2, abs=0.5)
