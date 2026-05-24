"""Tests for seismic_reporting.cli."""

from __future__ import annotations

from pathlib import Path

import pytest

from seismic_reporting import cli

# --------------------------------------------------------------------------
# parse_args
# --------------------------------------------------------------------------

def test_parse_args_defaults() -> None:
    """With no arguments the documented defaults apply."""
    args = cli.parse_args([])
    assert args.min_mag == 2.5
    assert args.days == 1.0
    assert args.sort == "distance"
    assert args.reverse is False
    assert args.radius is None
    assert args.limit is None
    assert args.width == 100
    assert args.file is None


def test_parse_args_overrides() -> None:
    """Supplied options override the defaults."""
    args = cli.parse_args([
        "--min-mag", "4.5", "--days", "7", "--sort", "time",
        "--reverse", "--radius", "300", "--limit", "20",
        "--lat", "37.77", "--lon", "-122.42", "--name", "SF",
    ])
    assert args.min_mag == 4.5
    assert args.days == 7.0
    assert args.sort == "time"
    assert args.reverse is True
    assert args.radius == 300.0
    assert args.limit == 20
    assert args.lat == 37.77
    assert args.lon == -122.42
    assert args.name == "SF"


def test_parse_args_rejects_bad_sort() -> None:
    """An unknown --sort value is rejected by argparse."""
    with pytest.raises(SystemExit):
        cli.parse_args(["--sort", "depth"])


def test_sort_codes_cover_all_choices() -> None:
    """Every CLI sort name maps to a known core sort code."""
    assert set(cli._SORT_CODES) == {"magnitude", "location", "distance", "time"}


@pytest.mark.parametrize("days,expected", [
    (1, "Past 1 day"),
    (1.0, "Past 1 day"),
    (7, "Past 7 days"),
    (30, "Past 30 days"),
    (1.5, "Past 1.5 days"),
])
def test_period_label(days: float, expected: str) -> None:
    """Day counts render as a singular/plural 'Past N day(s)' label."""
    assert cli._period_label(days) == expected


# --------------------------------------------------------------------------
# main  (file-driven: no network)
# --------------------------------------------------------------------------

def test_main_file_mode_succeeds(
    sample_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """Reading a GeoJSON file prints a report and exits 0."""
    rc = cli.main(["--file", str(sample_path), "--sort", "magnitude"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Event statistical Analysis" in out
    assert "Recorded 4 events" in out


@pytest.mark.parametrize("sort_name", ["magnitude", "location", "distance", "time"])
def test_main_file_mode_all_sorts(
    sample_path: Path, sort_name: str, capsys: pytest.CaptureFixture[str],
) -> None:
    """The file path renders cleanly under every sort mode."""
    rc = cli.main(["--file", str(sample_path), "--sort", sort_name])
    assert rc == 0
    assert capsys.readouterr().out.strip() != ""


def test_main_empty_file(
    empty_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """An empty FeatureCollection reports the no-results notice, exits 0."""
    rc = cli.main(["--file", str(empty_path)])
    assert rc == 0
    assert "No results found" in capsys.readouterr().out


def test_main_missing_file_returns_1(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A nonexistent --file path is an error: stderr message, exit 1."""
    rc = cli.main(["--file", "/nonexistent/path/quakes.geojson"])
    assert rc == 1
    assert "Error reading" in capsys.readouterr().err
