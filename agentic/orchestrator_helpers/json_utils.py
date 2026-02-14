"""JSON utilities for the orchestrator."""

import json
from datetime import datetime
from typing import Optional, Any


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def json_dumps_safe(obj, **kwargs) -> str:
    """JSON dumps with datetime support."""
    return json.dumps(obj, cls=DateTimeEncoder, **kwargs)


def _coerce_to_text(response_text: Any) -> str:
    if isinstance(response_text, str):
        return response_text
    if isinstance(response_text, bytes):
        return response_text.decode("utf-8", errors="replace")
    if isinstance(response_text, list):
        parts = []
        for item in response_text:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, (dict, list)):
                parts.append(json.dumps(item, cls=DateTimeEncoder))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    if isinstance(response_text, (dict, list)):
        return json.dumps(response_text, cls=DateTimeEncoder)
    return str(response_text)


def extract_json(response_text: Any) -> Optional[str]:
    """Extract JSON from LLM response (may be wrapped in markdown)."""
    text = _coerce_to_text(response_text)
    json_start = text.find("{")
    json_end = text.rfind("}") + 1

    if json_start >= 0 and json_end > json_start:
        return text[json_start:json_end]
    return None
