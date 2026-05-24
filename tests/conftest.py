"""Shared pytest fixtures for the Seismic-Reporting test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_dir() -> Path:
    """Directory holding the GeoJSON test fixtures."""
    return FIXTURE_DIR


@pytest.fixture
def sample_path() -> Path:
    """Path to the four-event sample GeoJSON fixture."""
    return FIXTURE_DIR / "sample.geojson"


@pytest.fixture
def empty_path() -> Path:
    """Path to the zero-event GeoJSON fixture."""
    return FIXTURE_DIR / "empty.geojson"


@pytest.fixture
def sample_bytes(sample_path: Path) -> bytes:
    """Raw bytes of the sample GeoJSON fixture."""
    return sample_path.read_bytes()


@pytest.fixture
def empty_bytes(empty_path: Path) -> bytes:
    """Raw bytes of the empty GeoJSON fixture."""
    return empty_path.read_bytes()
