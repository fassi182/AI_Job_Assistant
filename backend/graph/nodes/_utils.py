"""
Small helpers shared by graph nodes.
"""
import json
import re


def safe_json_parse(raw: str) -> dict:
    """Strips markdown code fences (```json ... ```) if present, then parses
    JSON. Raises json.JSONDecodeError if it still can't be parsed."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)
