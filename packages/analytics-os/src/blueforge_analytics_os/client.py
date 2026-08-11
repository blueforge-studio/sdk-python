"""AnalyticsOsClient — in-memory ring buffer + threaded flush."""
from __future__ import annotations
import atexit
import json
import logging
import threading
import time
from typing import Any
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

log = logging.getLogger(__name__)


class AnalyticsOsClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.app.blueforge.studio",
        flush_interval_ms: int = 5_000,
        max_batch_size: int = 50,
        max_buffer_size: int = 1_000,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._flush_interval_s = flush_interval_ms / 1000
        self._max_batch_size = max_batch_size
        self._max_buffer_size = max_buffer_size
        self._buffer: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._timer = threading.Thread(target=self._run, daemon=True)
        self._timer.start()
        atexit.register(self.flush)

    def capture(self, event: dict[str, Any]) -> None:
        with self._lock:
            if len(self._buffer) >= self._max_buffer_size:
                log.warning("analytics-os buffer overflow; dropping event")
                return
            self._buffer.append({**event, "provider": "analytics-os"})
            if len(self._buffer) >= self._max_batch_size:
                self._flush_locked()

    def flush(self) -> None:
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        if not self._buffer:
            return
        batch = self._buffer
        self._buffer = []
        self._send_with_retry(batch)

    def _send_with_retry(self, batch: list[dict[str, Any]]) -> None:
        url = f"{self._base_url}/v1/analytics/track"
        body = json.dumps({"events": batch}).encode()
        req_headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        for attempt in range(3):
            try:
                req = urlrequest.Request(url, data=body, headers=req_headers, method="POST")
                with urlrequest.urlopen(req, timeout=5) as resp:
                    if resp.status < 500:
                        return
            except HTTPError as e:
                if e.code in (400, 401, 422):
                    return
                if e.code == 429 or e.code >= 500:
                    time.sleep(2 ** attempt * 0.1)
                    continue
                return
            except URLError:
                time.sleep(2 ** attempt * 0.1)
                continue
        log.warning("analytics-os dropped %d events after 3 retries", len(batch))

    def _run(self) -> None:
        while not self._stop.wait(self._flush_interval_s):
            self.flush()

    def stop(self) -> None:
        """Stop the background flush thread. Flushes pending events first."""
        self.flush()
        self._stop.set()
