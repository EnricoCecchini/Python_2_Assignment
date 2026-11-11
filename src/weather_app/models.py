# Your data classes go here (e.g. a snapshot of one location's conditions at one point in time).
# README "1. Object-oriented design": special methods (__str__/__repr__/__eq__/__lt__...) and an @property.

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class OpenWeatherResponse:
    """Parsed response of OpenWeather's Current Weather endpoint (/data/2.5/weather).

    Temperatures are in Kelvin (the API default when no `units` argument is sent).
    """

    city: str
    country: str
    lat: float
    lon: float
    timestamp: datetime  # UTC time the data was calculated by OpenWeather
    condition: str  # e.g. "Clouds"
    description: str  # e.g. "overcast clouds"
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int  # hPa
    humidity: int  # %
    wind_speed: float  # m/s
    wind_deg: int | None
    clouds: int | None  # cloudiness %
    visibility: int | None  # metres

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "OpenWeatherResponse":
        """Build an OpenWeatherResponse from the raw JSON dict returned by the API."""

        try:
            main = data['main']
            weather = data['weather'][0] if data.get('weather') else {}
            wind = data.get('wind', {})

            return cls(
                city=data.get('name', ''),
                country=data.get('sys', {}).get('country', ''),
                lat=data['coord']['lat'],
                lon=data['coord']['lon'],
                timestamp=datetime.fromtimestamp(data['dt'], tz=timezone.utc),
                condition=weather.get('main', ''),
                description=weather.get('description', ''),
                temp=main['temp'],
                feels_like=main['feels_like'],
                temp_min=main['temp_min'],
                temp_max=main['temp_max'],
                pressure=main['pressure'],
                humidity=main['humidity'],
                wind_speed=wind.get('speed', 0.0),
                wind_deg=wind.get('deg'),
                clouds=data.get('clouds', {}).get('all'),
                visibility=data.get('visibility'),
            )
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Unexpected OpenWeather response format: missing {e}") from e
