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

## Feature: CSV storage of fetched weather history

**Asked:** "create the feature/storage branch and implement functions to append the fetched data to a data/weather.csv file. The file must not be overwritten as we will have to build historical data as the app runs."

**Got:** `src/weather_app/storage.py` — `append_snapshot(response)` and `append_snapshots(responses)` that append `OpenWeatherResponse` rows to `data/weather.csv` (opened in append mode, folder + header created on first write, header written only once, extra `fetched_at` UTC column), plus `load_history()` returning a pandas DataFrame with parsed datetimes. `tests/test_storage.py`.

**Checked:** 4 tests on temp files: header created once with folder auto-created; 4 appends across 3 calls give 1 header + 4 rows in order (nothing overwritten); a file with a different header raises `ValueError` and is left untouched; missing file loads as an empty DataFrame. Live run: fetched Rome and Milan and appended them to `data/weather.csv`; `load_history()` returned both rows.

**Kept as-is / changed / rejected:** Kept as-is. Added a header check that refuses to append if the CSV's columns don't match the model (e.g. after a model change), so the history can't get silently corrupted. `load_history()` was added beyond the request because analytics will need it.

---
