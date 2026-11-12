"""Redact common credentials and contact addresses from trace values."""

import re

PATTERNS = (
    (re.compile(r"(?i)bearer\s+[^\s,;]+"), "******"),
    (re.compile(r"(?i)(api[_ -]?key|password|secret|token)\s*[:=]\s*[^\s,;]+"), r"\1=[redacted]"),
    (re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"), "[email]"),
)
SENSITIVE_KEYS = {
    "password",
    "api_key",
    "api-key",
    "api key",
    "authorization",
    "csrf",
    "token",
    "secret",
    "access_token",
    "refresh_token",
}


def redact(value):
    """Return a recursively redacted copy without changing the source structure."""
    if isinstance(value, str):
        for pattern, replacement in PATTERNS:
            value = pattern.sub(replacement, value)
        return value
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, dict):
        return {
            key: "[redacted]" if isinstance(key, str) and key.lower() in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    return value
