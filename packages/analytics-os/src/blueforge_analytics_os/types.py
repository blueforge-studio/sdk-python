"""Typed event shape for analytics-os capture."""
from __future__ import annotations
from typing import TypedDict


class AnalyticsEvent(TypedDict, total=False):
    name: str
    distinctId: str
    properties: dict
    timestamp: str  # ISO 8601; default = now()
