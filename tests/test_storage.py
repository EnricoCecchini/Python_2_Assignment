from datetime import datetime, timezone

import pytest

from weather_app.models import OpenWeatherResponse
from weather_app.storage import COLUMNS, append_snapshot, append_snapshots, load_history


def make_response(city: str = "Rome", temp: float = 290.15) -> OpenWeatherResponse:
    return OpenWeatherResponse(
        city=city, country="IT", lat=41.9, lon=12.5,
        timestamp=datetime(2026, 11, 11, 12, 0, tzinfo=timezone.utc),
        condition="Clouds", description="overcast clouds",
        temp=temp, feels_like=289.5, temp_min=288.7, temp_max=291.2,
        pressure=1015, humidity=72, wind_speed=3.6, wind_deg=220,
        clouds=90, visibility=10000,
    )


def test_creates_file_with_header(tmp_path):
    path = tmp_path / "data" / "weather.csv"  # folder doesn't exist yet
    append_snapshot(make_response(), path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(COLUMNS)
    assert len(lines) == 2


def test_appends_without_overwriting(tmp_path):
    path = tmp_path / "weather.csv"
    append_snapshot(make_response("Rome", 290.0), path)
    append_snapshots([make_response("Milan", 285.0), make_response("Turin", 284.0)], path)
    append_snapshot(make_response("Rome", 291.0), path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5  # one header + 4 rows, header written only once
    assert lines.count(",".join(COLUMNS)) == 1

    df = load_history(path)
    assert list(df["city"]) == ["Rome", "Milan", "Turin", "Rome"]
    assert list(df["temp"]) == [290.0, 285.0, 284.0, 291.0]
    assert df["timestamp"].iloc[0] == datetime(2026, 11, 11, 12, 0, tzinfo=timezone.utc)


def test_refuses_to_append_to_file_with_different_header(tmp_path):
    path = tmp_path / "weather.csv"
    path.write_text("foo,bar\n1,2\n", encoding="utf-8")

    with pytest.raises(ValueError):
        append_snapshot(make_response(), path)
    assert path.read_text(encoding="utf-8") == "foo,bar\n1,2\n"  # untouched


def test_load_history_missing_file_returns_empty(tmp_path):
    df = load_history(tmp_path / "nope.csv")
    assert df.empty
    assert list(df.columns) == COLUMNS
