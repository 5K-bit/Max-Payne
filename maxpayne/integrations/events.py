from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_EVENT_URL = "http://127.0.0.1:8000/events/v1/publish"


def publish_event(
    event_type: str,
    payload: dict[str, Any],
    *,
    source: str = "maxpayne",
    correlation_id: str | None = None,
    parent_event_id: str | None = None,
    timeout: float = 1.5,
) -> bool:
    endpoint = os.getenv("OBEOS_EVENT_URL", "").strip()
    if not endpoint:
        return False
    envelope = {
        "contract_version": "1.0",
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "parent_event_id": parent_event_id,
        "payload": payload,
    }
    request = Request(
        endpoint or DEFAULT_EVENT_URL,
        data=json.dumps(envelope).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return 200 <= int(response.status) < 300
    except (OSError, URLError, ValueError):
        return False
