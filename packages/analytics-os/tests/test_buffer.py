"""Buffer + auto-flush tests."""
from __future__ import annotations
from unittest.mock import patch, MagicMock
from blueforge_analytics_os.client import AnalyticsOsClient


def _client(max_batch_size: int = 50, max_buffer_size: int = 1000):
    """Build a client with a mocked urlopen so we can observe flushes."""
    with patch("blueforge_analytics_os.client.urlrequest.urlopen") as m:
        # urlopen returns a context manager; mock it as one.
        m.return_value.__enter__.return_value.status = 200
        client = AnalyticsOsClient(
            api_key="aos_live_x.y",
            base_url="https://aos.example.com",
            flush_interval_ms=10_000,  # disable interval-driven flush
            max_batch_size=max_batch_size,
            max_buffer_size=max_buffer_size,
        )
    return client


def test_auto_flush_when_buffer_fills(monkeypatch):
    client = _client(max_batch_size=5)
    sent: list[list[dict]] = []

    def fake_urlopen(req, timeout=5):
        import json as _json
        body = _json.loads(req.data.decode())
        sent.append(body["events"])
        m = MagicMock()
        m.__enter__.return_value.status = 200
        m.__exit__.return_value = False
        return m

    monkeypatch.setattr("blueforge_analytics_os.client.urlrequest.urlopen", fake_urlopen)
    for i in range(5):
        client.capture({"name": "evt", "distinctId": f"u{i}"})
    assert len(sent) == 1
    assert len(sent[0]) == 5


def test_flush_on_empty_buffer_is_noop():
    client = _client()
    with patch("blueforge_analytics_os.client.urlrequest.urlopen") as m:
        client.flush()  # no fetch should be attempted
        m.assert_not_called()


def test_overflow_drops_events_silently(monkeypatch):
    client = _client(max_batch_size=1000, max_buffer_size=3)
    sent: list[list[dict]] = []

    def fake_urlopen(req, timeout=5):
        import json as _json
        body = _json.loads(req.data.decode())
        sent.append(body["events"])
        m = MagicMock()
        m.__enter__.return_value.status = 200
        m.__exit__.return_value = False
        return m

    monkeypatch.setattr("blueforge_analytics_os.client.urlrequest.urlopen", fake_urlopen)
    for i in range(10):
        client.capture({"name": "evt", "distinctId": f"u{i}"})
    client.flush()
    # max_buffer_size=3 → only the first 3 should be sent.
    assert sum(len(batch) for batch in sent) == 3
    flat = [e for batch in sent for e in batch]
    assert [e["distinctId"] for e in flat] == ["u0", "u1", "u2"]
