"""Tests for seismic_reporting.core."""

from __future__ import annotations

import datetime
from urllib.parse import parse_qs, urlparse

import pytest

from seismic_reporting import core
from seismic_reporting.core import (
    DEFAULT_ORIGIN,
    SORT_DISTANCE,
    SORT_LOCATION,
    SORT_MAGNITUDE,
    SORT_TIME,
    Origin,
    Quake,
    build_fdsn_url,
    check_type,
    fetch_geojson,
    format_place,
    format_report,
    magnitude_summary,
    parse_quakes,
    sort_quakes,
)

# --------------------------------------------------------------------------
# check_type
# --------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (4.5, 4.5),
    (3, 3.0),
    (0, 0.0),
    (-1.2, -1.2),
])
def test_check_type_numeric(value: object, expected: float) -> None:
    """Numeric input is coerced to float."""
    assert check_type(value) == expected


@pytest.mark.parametrize("value", [None, "abc", [], {}])
def test_check_type_non_numeric_returns_zero(value: object) -> None:
    """Non-numeric input (e.g. JSON null) becomes 0.00."""
    assert check_type(value) == 0.00


# --------------------------------------------------------------------------
# format_place
# --------------------------------------------------------------------------

def test_format_place_comma_form() -> None:
    """A 'detail, region' string is reordered region-first."""
    assert format_place("10km SE of Pahala, Hawaii") == "Hawaii, 10km SE of Pahala"


def test_format_place_region_name_with_keyword_unchanged() -> None:
    """A comma-less region name is already region-led; returned unchanged."""
    assert format_place("Southern Mid-Atlantic Ridge") == "Southern Mid-Atlantic Ridge"
    assert format_place("Balleny Islands region") == "Balleny Islands region"


def test_format_place_region_name_without_keyword_unchanged() -> None:
    """A comma-less string with no region keyword is also returned unchanged."""
    assert format_place("south of the Fiji Islands") == "south of the Fiji Islands"


def test_format_place_comma_region_containing_keyword() -> None:
    """A comma-form string is reversed even when its region holds a keyword.

    'Ocean City, Maryland' has a comma, so it is detail-then-region and must
    be reversed - the keyword 'Ocean' must not misclassify it as a region
    name. This is the false-positive the old keyword heuristic risked.
    """
    assert format_place("Ocean City, Maryland") == "Maryland, Ocean City"


# --------------------------------------------------------------------------
# build_fdsn_url
# --------------------------------------------------------------------------

def _params(url: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(url).query)


def test_build_fdsn_url_minimal() -> None:
    """A minimal query carries only the mandatory parameters."""
    params = _params(build_fdsn_url(2.5, "2024-01-01T00:00:00"))
    assert params["format"] == ["geojson"]
    assert params["starttime"] == ["2024-01-01T00:00:00"]
    assert params["minmagnitude"] == ["2.5"]
    assert params["orderby"] == ["time"]
    assert "latitude" not in params
    assert "endtime" not in params
    assert "limit" not in params


def test_build_fdsn_url_radial_query() -> None:
    """lat + lon + radius together add the radial parameters."""
    params = _params(build_fdsn_url(
        1.0, "2024-01-01T00:00:00", lat=19.6, lon=-155.9, radius_km=300))
    assert params["latitude"] == ["19.6"]
    assert params["longitude"] == ["-155.9"]
    assert params["maxradiuskm"] == ["300"]


def test_build_fdsn_url_partial_radius_ignored() -> None:
    """A lat without lon/radius does not produce a radial query."""
    params = _params(build_fdsn_url(1.0, "2024-01-01T00:00:00", lat=19.6))
    assert "latitude" not in params
    assert "maxradiuskm" not in params


def test_build_fdsn_url_optional_params() -> None:
    """endtime, limit and orderby are emitted when supplied."""
    params = _params(build_fdsn_url(
        1.0, "2024-01-01T00:00:00", endtime="2024-02-01T00:00:00",
        orderby="magnitude", limit=50))
    assert params["endtime"] == ["2024-02-01T00:00:00"]
    assert params["orderby"] == ["magnitude"]
    assert params["limit"] == ["50"]


def test_build_fdsn_url_targets_fdsn_endpoint() -> None:
    """The URL points at the configured FDSN endpoint."""
    url = build_fdsn_url(2.5, "2024-01-01T00:00:00")
    assert url.startswith(core.FDSN_ENDPOINT + "?")


# --------------------------------------------------------------------------
# fetch_geojson  (urlopen monkeypatched - no real network)
# --------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, code: int, payload: bytes = b"") -> None:
        self._code = code
        self._payload = payload

    def getcode(self) -> int:
        return self._code

    def read(self) -> bytes:
        return self._payload


def test_fetch_geojson_200_returns_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 200 response returns the body bytes verbatim."""
    payload = b'{"features": []}'
    monkeypatch.setattr(core, "urlopen",
                         lambda url, timeout=10: _FakeResponse(200, payload))
    assert fetch_geojson("http://example.test/q") == payload


def test_fetch_geojson_204_returns_empty_collection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A 204 response yields a synthetic empty FeatureCollection."""
    monkeypatch.setattr(core, "urlopen",
                         lambda url, timeout=10: _FakeResponse(204))
    data = fetch_geojson("http://example.test/q")
    assert b'"features":[]' in data
    assert b'"count":0' in data


def test_fetch_geojson_non_200_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Any other status raises RuntimeError."""
    monkeypatch.setattr(core, "urlopen",
                         lambda url, timeout=10: _FakeResponse(500))
    with pytest.raises(RuntimeError, match="HTTP 500"):
        fetch_geojson("http://example.test/q")


# --------------------------------------------------------------------------
# parse_quakes
# --------------------------------------------------------------------------

def test_parse_quakes_reads_all_features(sample_bytes: bytes) -> None:
    """All features are decoded, in feed order, with metadata."""
    quakes, meta = parse_quakes(sample_bytes, DEFAULT_ORIGIN)
    assert len(quakes) == 4
    assert meta["count"] == 4
    assert meta["title"] == "USGS FDSN sample fixture"
    assert [q.place for q in quakes][0] == "10km SE of Pahala, Hawaii"


def test_parse_quakes_null_magnitude_becomes_zero(sample_bytes: bytes) -> None:
    """A JSON-null magnitude is coerced to 0.0 (the Mid-Atlantic fixture event)."""
    quakes, _ = parse_quakes(sample_bytes, DEFAULT_ORIGIN)
    null_mag = next(q for q in quakes if q.place == "Southern Mid-Atlantic Ridge")
    assert null_mag.mag == 0.0


def test_parse_quakes_distance_computed(sample_bytes: bytes) -> None:
    """Distance is measured from the supplied origin."""
    quakes, _ = parse_quakes(sample_bytes, DEFAULT_ORIGIN)
    near = next(q for q in quakes if q.place.startswith("10km SE of Pahala"))
    far = next(q for q in quakes if q.place == "Southern Mid-Atlantic Ridge")
    assert 0 < near.distance_km < 200
    assert far.distance_km > 10000


def test_parse_quakes_empty(empty_bytes: bytes) -> None:
    """An empty FeatureCollection yields no quakes."""
    quakes, meta = parse_quakes(empty_bytes, DEFAULT_ORIGIN)
    assert quakes == []
    assert meta["count"] == 0


def test_parse_quakes_time_is_local_aware(sample_bytes: bytes) -> None:
    """Event times are timezone-aware and converted to the host local zone.

    The fixture's Pahala event carries epoch 1714500000000 ms, i.e. the
    instant 2024-04-30 18:00:00 UTC. Aware-to-aware equality compares the
    underlying instant, so this holds regardless of the host's zone.
    """
    quakes, _ = parse_quakes(sample_bytes, DEFAULT_ORIGIN)
    pahala = next(q for q in quakes if q.place.startswith("10km SE of Pahala"))
    assert pahala.time.tzinfo is not None
    assert pahala.time == datetime.datetime(
        2024, 4, 30, 18, 0, 0, tzinfo=datetime.timezone.utc)


# --------------------------------------------------------------------------
# magnitude_summary
# --------------------------------------------------------------------------

def test_magnitude_summary_populated(sample_bytes: bytes) -> None:
    """A populated list reports max, mean and median - and no longer mode."""
    quakes, _ = parse_quakes(sample_bytes, DEFAULT_ORIGIN)
    line = magnitude_summary(quakes)
    assert line.startswith("Magnitude Max =")
    assert "4.50" in line
    assert "Mean =" in line
    assert "Median =" in line
    assert "Mode" not in line


def test_magnitude_summary_empty() -> None:
    """An empty list produces the no-results notice."""
    assert magnitude_summary([]).startswith("** No results found")


# --------------------------------------------------------------------------
# sort_quakes
# --------------------------------------------------------------------------

def _quake(mag: float, place: str, dist: float, day: int) -> Quake:
    return Quake(mag=mag, place=place, distance_km=dist,
                 time=datetime.datetime(2024, 1, day,
                                        tzinfo=datetime.timezone.utc))


@pytest.fixture
def quake_list() -> list[Quake]:
    return [
        _quake(4.5, "Hawaii", 100.0, 2),
        _quake(2.5, "Alaska", 50.0, 3),
        _quake(3.1, "Zulu", 200.0, 1),
    ]


def test_sort_by_magnitude(quake_list: list[Quake]) -> None:
    assert [q.mag for q in sort_quakes(quake_list, SORT_MAGNITUDE)] == [2.5, 3.1, 4.5]


def test_sort_by_magnitude_reverse(quake_list: list[Quake]) -> None:
    result = sort_quakes(quake_list, SORT_MAGNITUDE, reverse=True)
    assert [q.mag for q in result] == [4.5, 3.1, 2.5]


def test_sort_by_distance(quake_list: list[Quake]) -> None:
    result = sort_quakes(quake_list, SORT_DISTANCE)
    assert [q.distance_km for q in result] == [50.0, 100.0, 200.0]


def test_sort_by_time(quake_list: list[Quake]) -> None:
    result = sort_quakes(quake_list, SORT_TIME)
    assert [q.time.day for q in result] == [1, 2, 3]


def test_sort_by_location(quake_list: list[Quake]) -> None:
    result = sort_quakes(quake_list, SORT_LOCATION)
    assert [q.place for q in result] == ["Alaska", "Hawaii", "Zulu"]


def test_sort_unknown_code_defaults_to_magnitude(quake_list: list[Quake]) -> None:
    """An unrecognised sort code falls back to magnitude order."""
    assert (sort_quakes(quake_list, 99)
            == sort_quakes(quake_list, SORT_MAGNITUDE))


def test_sort_does_not_mutate_input(quake_list: list[Quake]) -> None:
    """sort_quakes returns a new list; the argument is untouched."""
    before = list(quake_list)
    sort_quakes(quake_list, SORT_DISTANCE)
    assert quake_list == before


# --------------------------------------------------------------------------
# format_report
# --------------------------------------------------------------------------

def test_format_report_contains_sections(quake_list: list[Quake]) -> None:
    """The rendered report includes the header, stats and a sort banner."""
    meta = {"count": 3, "title": "fixture"}
    report = format_report(quake_list, meta, "Past Week", DEFAULT_ORIGIN,
                            SORT_MAGNITUDE, "stats here", 0.01, width=100)
    assert "Event statistical Analysis" in report
    assert "Recorded 3 events from fixture, Past Week" in report
    assert "stats here" in report
    assert "sorted by MAGNITUDE" in report


def test_format_report_omits_empty_period(quake_list: list[Quake]) -> None:
    """An empty period label leaves the header with no trailing separator."""
    meta = {"count": 3, "title": "fixture"}
    report = format_report(quake_list, meta, "", DEFAULT_ORIGIN,
                            SORT_MAGNITUDE, "stats", 0.01, width=100)
    assert "Recorded 3 events from fixture" in report
    assert "fixture," not in report


def test_format_report_distance_banner_names_origin(
    quake_list: list[Quake],
) -> None:
    """The distance sort banner names the origin location."""
    meta = {"count": 3, "title": "fixture"}
    report = format_report(quake_list, meta, "Past Day", DEFAULT_ORIGIN,
                            SORT_DISTANCE, "stats", 0.01, width=100)
    assert DEFAULT_ORIGIN.name in report


def test_origin_dataclass_fields() -> None:
    """Origin stores the three observer fields."""
    o = Origin(1.0, 2.0, "Somewhere")
    assert (o.lat, o.lon, o.name) == (1.0, 2.0, "Somewhere")
