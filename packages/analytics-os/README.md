# blueforge-analytics-os

Python client for the [analytics-os](https://github.com/blueforge-studio/forge-control)
capture API. Stdlib-only — no third-party dependencies.

## Install

```
pip install blueforge-analytics-os
```

## Usage

```python
from blueforge_analytics_os import AnalyticsOsClient

client = AnalyticsOsClient(
    api_key="aos_live_<prefix>.<secret>",
    base_url="https://api.app.blueforge.studio",
)

client.capture({
    "name": "pageview",
    "distinctId": "user-123",
    "url": "https://example.com/landing",
})

# Flush on shutdown (atexit is registered automatically).
client.flush()
```

## Configuration

| Env var | Default | Description |
|---|---|---|
| `BLUEFORGE_ANALYTICS_OS_API_KEY` | (required) | Bearer token issued via `mintApiKey`. |
| `BLUEFORGE_ANALYTICS_OS_BASE_URL` | `https://api.app.blueforge.studio` | analytics-os API base URL. |

Tunables (constructor args): `flush_interval_ms=5000`, `max_batch_size=50`, `max_buffer_size=1000`.

## License

MIT.
