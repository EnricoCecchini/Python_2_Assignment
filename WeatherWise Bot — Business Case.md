# WeatherWise Bot — Business Case

Nov 10, 2026 · @Enrico Cecchini Rivera

## Executive summary

We recommend building WeatherWise, a Telegram bot that turns the forecast for a user's exact location into plain advice ("take an umbrella, rain from 15:00"), backed by a Streamlit analytics dashboard. The MVP can run at near-zero cost: Telegram's Bot API is free and OpenWeather's One Call API 3.0 includes 1,000 free calls per day.

- **Problem:** forecasts give numbers, not decisions; people still get caught without a coat, umbrella or sunscreen.
- **Solution:** location-aware, rule-based recommendations delivered on demand or as a morning push, inside an app users already open daily.
- **Ask:** about 6 weeks of one developer's time to ship an MVP, then a 3-month pilot measured on retention and recommendation usefulness.
- **Decision needed:** approve the MVP scope (section 5) and the pilot success thresholds (section 10).

## Problem statement and opportunity

Weather apps report conditions but leave the interpretation to the user. Translating "12 °C, 70% chance of rain after 3pm, UV 6" into what to wear and carry takes attention people rarely give in a rushed morning.

- **Decision gap:** users must combine temperature, feels-like, rain probability, wind and UV themselves.
- **Timing gap:** the check happens once, early; conditions later in the day are missed.
- **App fatigue:** another standalone app competes for a home-screen slot and notification permission.

The opportunity is to deliver the *decision*, not the data, through a messaging channel the user already trusts. Telegram bots need no install, no app-store review, and support native location sharing.

## Proposed solution and user journey

WeatherWise has two surfaces sharing one backend: a Telegram bot for end users and a Streamlit dashboard for weather analytics and product monitoring. The core journey takes a new user from `/start` to a first recommendation in under 30 seconds.

1. User opens the bot and sends `/start`; the bot explains what it does and what data it uses.
2. Bot shows a **Share location** button (Telegram's `request_location` keyboard); the user can also type a city name as a fallback.
3. Backend stores the coordinates and calls the OpenWeather One Call API for current, hourly and daily data.
4. The recommendation engine scores conditions against rules (rain, cold, wind, UV, heat) and composes a short message with items to take.
5. Bot replies with the advice plus a one-line forecast summary and inline buttons: *Tomorrow*, *Daily alert*, *Change location*.
6. Optional: user subscribes to a daily morning push at a chosen time.
7. Every request and response is logged, feeding the Streamlit dashboard.

## Target users and value proposition

The primary segment is daily commuters who already use Telegram; secondary segments are parents, outdoor enthusiasts and travellers.

| Segment | Core need | What WeatherWise gives them |
| --- | --- | --- |
| Commuters (walk, bike, transit) | Know what to wear and carry before leaving | Morning push: coat, umbrella, gloves, with the rain window |
| Parents | Dress kids correctly for school | Feels-like based clothing advice, afternoon pickup forecast |
| Runners and cyclists | Pick the best time to train | Hourly windows with low rain, wind and heat |
| Travellers | Pack for an unfamiliar city | Multi-day packing list for a shared or typed location |
| Outdoor workers | Avoid heat and UV exposure | UV and heat warnings with sunscreen and hydration reminders |

**Value proposition:** "Tell me what to bring, not what the weather is." No app to install, advice in under 30 seconds, and alerts only when something changes.

## Functional scope

The MVP covers six bot commands, a transparent rule-based recommendation engine and a four-page dashboard. Thresholds below are starting values to tune during the pilot.

### Bot commands

| Command / trigger | Action | MVP |
| --- | --- | --- |
| `/start` | Onboarding, privacy note, location request button | Yes |
| Location message or city text | Save location, return today's recommendation | Yes |
| `/now` | Recommendation for the next 6 hours | Yes |
| `/tomorrow` | Recommendation for tomorrow | Yes |
| `/alert HH:MM` | Subscribe to a daily morning push; `/alert off` to stop | Yes |
| `/settings` | Units (°C/°F), language, sensitivity (runs cold or warm) | Phase 2 |
| `/delete` | Erase stored location and history | Yes |

### Recommendation rules

Each rule reads One Call API fields for the user's time window and fires an item when its threshold is met.

| Item | Trigger (starting threshold) | API fields |
| --- | --- | --- |
| Umbrella | Precipitation probability ≥ 40% and wind < 30 km/h | `pop`, `rain`, `wind_speed` |
| Raincoat | Precipitation probability ≥ 40% and wind ≥ 30 km/h, or heavy rain | `pop`, `rain`, `wind_speed` |
| Light jacket | Feels-like 12–18 °C | `feels_like` |
| Warm coat, gloves | Feels-like < 8 °C | `feels_like` |
| Sunscreen, sunglasses | UV index ≥ 3 during daylight hours | `uvi` |
| Water, light clothing | Feels-like ≥ 30 °C | `feels_like` |
| Snow boots | Snow forecast in window | `snow`, `weather.id` |
| Severe-weather warning | Any national alert for the location | `alerts` |

### Streamlit dashboard

- **Weather analytics:** current conditions, 48-hour temperature and rain charts, 8-day outlook for any saved location.
- **Recommendation insights:** which items fired most, by city and day.
- **Usage:** daily active users, commands per day, alert subscribers, retention cohorts.
- **Ops health:** API calls used vs the free daily quota, error rate, response latency.

## Technical architecture and data flow

A single Python service handles both user commands and scheduled alerts, so the bot, the alerts and the dashboard all share one recommendation engine, one cache and one database.

&#91;embedded content: system architecture · 9 components\]

User messages arrive through the Telegram Bot API; handlers and the scheduler both call the engine, which asks the cached weather client before hitting OpenWeather. Every request is logged to the database, which the Streamlit dashboard reads.

| Layer | Suggested choice | Why |
| --- | --- | --- |
| Bot framework | python-telegram-bot or aiogram | Mature, async, built-in job queue for alerts |
| Weather data | OpenWeather One Call API 3.0 + Geocoding API | Current, 48 h hourly, 8-day daily and alerts in one call; city-name fallback |
| Storage | SQLite for MVP, PostgreSQL at scale | Zero setup first, easy migration later |
| Dashboard | Streamlit + Plotly | Fast to build analytics pages in Python |
| Hosting | Docker on a small VPS or container platform | One image for bot and dashboard; secrets in environment variables |

## Market and alternatives

The space is crowded with forecast apps but thin on decision-oriented advice inside messengers; WeatherWise competes on convenience and actionability, not forecast accuracy.

| Alternative | Strength | Gap WeatherWise fills |
| --- | --- | --- |
| Built-in phone weather apps | Free, preinstalled, good visuals | Show data, not what to wear or carry |
| Dedicated weather apps | Rich radar and maps | Separate install; advice is rare or paywalled |
| Existing Telegram weather bots | Same channel | Mostly echo the forecast; little personalisation or proactive alerts |
| Voice assistants' morning briefings | Hands-free | Tied to a device; generic, not location-precise on the go |
| "What to wear" apps | Clothing focus | Niche installs; weak on carry items and alerts |

Open question: size of the reachable Telegram audience in the launch market; validate with the pilot's organic sign-up rate before investing in marketing.

## Costs, monetization and financial outlook

Running costs stay near zero until roughly 1,000 active users, because the main external dependency has a free daily allowance and the messaging channel is free. Development time is the real investment.

### Cost drivers (estimates, EUR)

| Item | MVP / pilot | At \~10,000 users | Notes |
| --- | --- | --- | --- |
| OpenWeather One Call API 3.0 | €0 | Pay per call above free tier | 1,000 free calls/day; overage billed per call monthly ([pricing](https://openweathermap.org/api)) |
| Telegram Bot API | €0 | €0 | No usage fees for bots |
| Hosting (bot + DB + Streamlit) | €0–10/month | €20–60/month | Small VPS or container platform; Streamlit Community Cloud for internal dashboard |
| Development | \~6 developer-weeks | \~1 day/week maintenance | Largest cost; one Python developer |

**Keeping API calls inside the free tier:** cache responses per rounded location (about 1 km grid) for 10 minutes, since OpenWeather updates the model at that interval ([One Call docs](https://openweathermap.org/api/uvi)). Batch morning alerts by location, so 500 users in one city cost one call, not 500. Set a hard daily call cap in the OpenWeather account so overages cannot surprise you.

### Monetization options

| Model | How it works | Fit |
| --- | --- | --- |
| Freemium | Free daily advice; premium adds multiple locations, hourly change alerts, custom thresholds, paid in Telegram Stars | Best first test |
| B2B / white-label | Branded bot for employers, schools, tour operators, event organisers | Higher value, slower sales |
| Contextual partnerships | Opt-in, clearly labelled offers (e.g. sunscreen, rain gear) tied to the recommendation | Only after trust is established |

Break-even is reachable early: if hosting plus API overage runs at about €60/month at 10,000 users, a 2% premium conversion at €2/month covers it several times over. These are planning assumptions to validate in the pilot.

## Risks, privacy and compliance

Location is personal data under GDPR, so privacy design is the highest-priority risk; the rest are manageable with standard engineering controls.

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Location data misuse or breach | High | Low | Store coordinates rounded to \~1 km; encrypt at rest; `/delete` erases all data; no sharing with third parties |
| Lack of lawful basis / consent | High | Medium | Explicit opt-in at `/start`, short privacy notice, privacy policy link, data retention limit (e.g. 90 days of history) |
| Wrong advice (forecast miss) | Medium | Medium | Show probability and time window, not certainties; feedback buttons to tune thresholds |
| API quota exceeded or outage | Medium | Low | Caching, batching, hard daily cap, fallback to cached data with a "last updated" note |
| Telegram API changes or bot spam limits | Medium | Low | Use a maintained library (python-telegram-bot or aiogram); respect broadcast rate limits for alerts |
| Low retention after novelty | High | Medium | Daily alert as the habit loop; only notify when conditions change |
| Bot token or API key leak | High | Low | Keys in environment secrets, never in the repo; rotate on suspicion |

Review OpenWeather's terms on attribution and commercial use of the data before launching paid features.

## KPIs and success metrics

The pilot succeeds if users keep coming back and find the advice right; growth metrics matter only after that.

| KPI | Definition | Pilot target (3 months) |
| --- | --- | --- |
| Activation rate | Users who share a location after `/start` | ≥ 70% |
| Day-30 retention | Users active 30 days after first use | ≥ 25% |
| Alert adoption | Active users subscribed to the daily push | ≥ 40% |
| Advice usefulness | Thumbs-up share on "Was this helpful?" buttons | ≥ 80% |
| Time to first advice | `/start` to first recommendation | < 30 seconds |
| API cost per active user | Monthly API spend ÷ monthly active users | €0 during pilot |
| Uptime | Bot responds within 3 seconds | ≥ 99% |

All metrics are visible on the Streamlit dashboard's Usage and Ops pages.

## Roadmap and next steps

An MVP ships in about 6 weeks, then a 3-month pilot decides whether to invest in premium features and growth.

&#91;embedded content: roadmap · 4 phases, 2 gates\]

The go/no-go gate uses the pilot targets from the KPI table; missing them means iterating on the rules, not scaling.

- [ ] Approve MVP scope and pilot success thresholds
- [ ] Register the bot with BotFather and create an OpenWeather account with a daily call cap
- [ ] Draft the privacy notice and data-retention policy
- [ ] Recruit 50 to 200 pilot users
- [ ] Decide on premium pricing before the go/no-go review

## Sources

- [OpenWeather API overview and pricing](https://openweathermap.org/api)
- [OpenWeather One Call API 3.0 documentation](https://openweathermap.org/api/uvi)
- [OpenWeather FAQ](https://openweathermap.org/faq)
