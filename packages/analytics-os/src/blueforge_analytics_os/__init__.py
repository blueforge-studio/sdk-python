"""blueforge-analytics-os — analytics-os capture client."""
from __future__ import annotations
from .client import AnalyticsOsClient
from .types import AnalyticsEvent

__version__ = "0.1.0"

__all__ = ["AnalyticsOsClient", "AnalyticsEvent"]