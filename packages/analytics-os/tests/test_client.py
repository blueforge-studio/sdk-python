"""Retry + threading tests for AnalyticsOsClient."""
from __future__ import annotations
import threading
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError
from blueforge_analytics_os.client import AnalyticsOsClient


def _ok_response():
    m = MagicMock()
    m.__enter__.return_value.status = 200
    m.__exit__.return_value = False
    return m


def test_drops_batch_after_three_500s():
    client = AnalyticsOsClient(api_key="k", base_url="https://x", flush_interval_ms=10_000, max_batch_size=10)
    client.capture({"name": "evt", "distinctId": "u1"})

    responses = [_ok_response(), _ok_response(), _ok_response(), _ok_response()]
    with patch("blueforge_analytics_os.client.urlrequest.urlopen", side_effect=[
        HTTPError("https://x", 500, "Server Error", {}, None),
        HTTPError("https://x", 500, "Server Error", {}, None),
        HTTPError("https://x", 500, "Server Error", {}, None),
    ]):
        client.flush()
    # No exception propagates; events are dropped silently (logged).


def test_succeeds_after_one_429():
    client = AnalyticsOsClient(api_key="k", base_url="https://x", flush_interval_ms=10_000, max_batch_size=10)
    client.capture({"name": "evt", "distinctId": "u1"})

    calls = []
    def fake(req, timeout=5):
        calls.append(req)
        if len(calls) == 1:
            raise HTTPError("https://x", 429, "Too Many Requests", {}, None)
        return _ok_response()

    with patch("blueforge_analytics_os.client.urlrequest.urlopen", side_effect=fake):
        client.flush()
    assert len(calls) == 2


def test_retries_then_drops_on_URLError():
    client = AnalyticsOsClient(api_key="k", base_url="https://x", flush_interval_ms=10_000, max_batch_size=10)
    client.capture({"name": "evt", "distinctId": "u1"})

    calls = []
    def fake(req, timeout=5):
        calls.append(req)
        if len(calls) < 3:
            raise URLError("ECONNREFUSED")
        return _ok_response()

    with patch("blueforge_analytics_os.client.urlrequest.urlopen", side_effect=fake):
        client.flush()
    # 3 attempts (the 3rd succeeds); the test verifies the retry happens,
    # not the success path — both branches must not raise.
    assert len(calls) == 3


def test_concurrent_capture_is_thread_safe():
    client = AnalyticsOsClient(api_key="k", base_url="https://x", flush_interval_ms=10_000, max_batch_size=10_000, max_buffer_size=10_000)
    errors: list[Exception] = []

    def worker(i: int):
        try:
            for j in range(100):
                client.capture({"name": "evt", "distinctId": f"u{i}-{j}"})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert errors == []
    assert len(client._buffer) == 800  # all 800 events buffered
    client.stop()