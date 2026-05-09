"""Lichte HTTP helper, geen externe dependencies.

Gebruikt `urllib.request` zodat de LLM-laag geen extra requirements
introduceert.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


def post_json(url: str, payload: dict, timeout: int = 60) -> dict | None:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if not data:
            return None
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            return {"_raw": data.decode("utf-8", errors="replace")}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None
