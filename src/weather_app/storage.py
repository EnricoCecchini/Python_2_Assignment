# Logging fetched snapshots to a local file (CSV or SQLite) with a timestamp, and loading them back.
# README "3. Data and analytics": this is what turns single API calls into a real time series.

import csv
from dataclasses import asdict, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from .models import OpenWeatherResponse

DATA_FILE = Path(__file__).resolve().parents[2] / 'data' / 'weather.csv'

# `fetched_at` = when our app fetched the data; `timestamp` = when OpenWeather calculated it.
COLUMNS = ['fetched_at'] + [f.name for f in fields(OpenWeatherResponse)]


def _to_row(response: OpenWeatherResponse, fetched_at: datetime) -> dict:
    row = asdict(response)
    row['timestamp'] = response.timestamp.isoformat()
    row['fetched_at'] = fetched_at.isoformat()
    return row


def _check_header(path: Path) -> bool:
    """Return True if the file already has content, after making sure its header matches COLUMNS."""

    if not path.exists() or path.stat().st_size == 0:
        return False

    with path.open('r', newline='', encoding='utf-8') as f:
        header = next(csv.reader(f), [])

    if header != COLUMNS:
        raise ValueError(
            f"{path} has an unexpected header {header}; expected {COLUMNS}. "
            "Refusing to append to avoid corrupting the history."
        )
    return True


def append_snapshots(
    responses: Iterable[OpenWeatherResponse],
    path: Path = DATA_FILE,
) -> int:
    """Append fetched snapshots to the CSV history file, never overwriting it.

    Creates the file (and its folder) with a header row on first use.
    Returns the number of rows written.
    """

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    has_content = _check_header(path)
    fetched_at = datetime.now(timezone.utc)

    count = 0
    with path.open('a', newline='', encoding='utf-8') as f:  # 'a' = append-only
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not has_content:
            writer.writeheader()
        for response in responses:
            writer.writerow(_to_row(response, fetched_at))
            count += 1
    return count


def append_snapshot(response: OpenWeatherResponse, path: Path = DATA_FILE) -> None:
    """Append a single fetched snapshot to the CSV history file."""

    append_snapshots([response], path)


def load_history(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the whole history as a DataFrame (empty, with the right columns, if no file yet)."""

    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMNS)

    df = pd.read_csv(path)
    df['fetched_at'] = pd.to_datetime(df['fetched_at'], utc=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    return df
