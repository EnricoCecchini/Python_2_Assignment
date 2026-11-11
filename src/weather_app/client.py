# Your API client classes go here.
# README "1. Object-oriented design": a generic base class + an OpenWeatherMap-specific subclass.
# summary.md section 1 has a starting pattern — build your own version, don't copy it verbatim.

import httpx

from .config import API_KEY, BASE_URL
from .models import OpenWeatherResponse


class WeatherAPIError(Exception):
    """Raised when a request to OpenWeather fails (network error, bad status, bad JSON)."""


class RequestHandler:
    """Performs GET requests to OpenWeather's Current Weather endpoint."""

    ENDPOINT = 'weather'

    def __init__(self, timeout: float = 10.0):
        """Create HTTP request client. `timeout` is in seconds."""

        self._client = httpx.Client(
            base_url=BASE_URL.rstrip('/'),
            timeout=timeout,
        )

    def __build_endpoint(self, lat: float, lon: float) -> str:
        """Endpoint path with lat, lon and APPID passed as in-line query arguments."""

        return f'{self.ENDPOINT}?lat={lat}&lon={lon}&appid={API_KEY}'

    def _request(self, lat: float, lon: float) -> OpenWeatherResponse:
        """Perform the GET request and parse the JSON body into an OpenWeatherResponse."""

        endpoint = self.__build_endpoint(lat, lon)

        try:
            response = self._client.get(endpoint)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            # Don't include the URL in the message: it contains the API key.
            raise WeatherAPIError(
                f"OpenWeather returned {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise WeatherAPIError(f"Request to OpenWeather failed: {type(e).__name__}") from e
        except ValueError as e:
            raise WeatherAPIError("OpenWeather returned invalid JSON") from e

        return OpenWeatherResponse.from_json(data)

    def get(self, lat: float, lon: float) -> OpenWeatherResponse:
        """Fetch current weather for the given coordinates."""

        if not -90 <= lat <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {lon}")

        return self._request(lat, lon)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""

        self._client.close()

    def __enter__(self) -> "RequestHandler":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
