# AI collaboration log

Add one entry per feature/class you asked an AI agent to help with, in the order you worked on them.
Keep this running as you go — don't reconstruct it from memory at the end.

## Feature: <short name>

**Asked:** <the actual prompt you gave the agent>

**Got:** <what file/function it produced>

**Checked:** <how you verified it — a hand-made test case, a comparison against a known value, etc.>

**Kept as-is / changed / rejected:** <which, and why>

---

## Feature: RequestHandler (OpenWeather Current Weather client)

**Asked:** "Continue implementing the RequestHandler class, which will perform HTTP requests to OpenWeather's Current & Forecast API. lat and long values will be received as parameters and passed to the _request method. The RequestHandler will only perform GET requests to the URL using in-line arguments for lat, lon and the APPID (API_KEY), and the response JSON will be parsed into an OpenWeatherResponse class object."

**Got:** `src/weather_app/client.py` — `RequestHandler` with `get(lat, lon)` → `_request(lat, lon)` (GET to `weather?lat=..&lon=..&appid=..`), `close()` and context-manager support, plus a `WeatherAPIError` exception. `src/weather_app/models.py` — `OpenWeatherResponse` dataclass with `from_json()`. `config.py` `BASE_URL` changed to the API root (`/data/2.5`). Added `httpx` dependency and `pytest` dev dependency. `tests/test_client.py` with mocked-transport tests.

**Checked:** 3 offline tests using `httpx.MockTransport` and a hand-made sample response (query string contains lat/lon/appid, JSON fields parsed correctly, 401 raises `WeatherAPIError`, out-of-range coordinates rejected) — all pass. Live call for Rome (41.9028, 12.4964) returned a valid `OpenWeatherResponse` (Trevi, IT, 293.25 K, 77% humidity).

**Kept as-is / changed / rejected:** Changed from the initial draft: timeout was 3000 (httpx uses seconds, not ms) → 10 s; `_request` returned the raw response or `None` on error → now returns a parsed `OpenWeatherResponse` and raises `WeatherAPIError` (message excludes the URL so the API key isn't leaked); `get` now takes `lat, lon` directly instead of a params dict. Temperatures are in Kelvin since no `units` argument is sent.

---
