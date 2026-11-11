import httpx
import pytest

from weather_app.client import RequestHandler, WeatherAPIError
from weather_app.models import OpenWeatherResponse

# Trimmed example of a real /data/2.5/weather response (Rome).
SAMPLE = {
    "coord": {"lon": 12.4964, "lat": 41.9028},
    "weather": [{"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04d"}],
    "main": {"temp": 290.15, "feels_like": 289.5, "temp_min": 288.7, "temp_max": 291.2,
             "pressure": 1015, "humidity": 72},
    "visibility": 10000,
    "wind": {"speed": 3.6, "deg": 220},
    "clouds": {"all": 90},
    "dt": 1700000000,
    "sys": {"country": "IT"},
    "name": "Rome",
}


def make_handler(responder) -> RequestHandler:
    """RequestHandler whose HTTP client is backed by a fake transport (no network)."""
    handler = RequestHandler()
    handler._client = httpx.Client(
        base_url=handler._client.base_url, transport=httpx.MockTransport(responder)
    )
    return handler


def test_get_builds_inline_query_and_parses_response():
    seen = {}

    def responder(request: httpx.Request) -> httpx.Response:
        seen["url"] = request.url
        return httpx.Response(200, json=SAMPLE)

    result = make_handler(responder).get(41.9028, 12.4964)

    assert seen["url"].path == "/data/2.5/weather"
    assert seen["url"].params["lat"] == "41.9028"
    assert seen["url"].params["lon"] == "12.4964"
    assert "appid" in seen["url"].params
    assert isinstance(result, OpenWeatherResponse)
    assert result.city == "Rome"
    assert result.temp == 290.15
    assert result.humidity == 72
    assert result.condition == "Clouds"
    assert result.timestamp.year == 2023


def test_http_error_raises_weather_api_error():
    handler = make_handler(lambda r: httpx.Response(401, json={"message": "Invalid API key"}))
    with pytest.raises(WeatherAPIError, match="401"):
        handler.get(0, 0)


def test_invalid_coordinates_rejected():
    handler = make_handler(lambda r: httpx.Response(200, json=SAMPLE))
    with pytest.raises(ValueError):
        handler.get(91, 0)
    with pytest.raises(ValueError):
        handler.get(0, 181)
