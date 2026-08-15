"""ApplyFlow governance: append-only event log.

Every record is one JSON object per line in data/governance.jsonl.
Records are never modified or deleted.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path("C:/va-pipeline/data")
LOG = DATA / "governance.jsonl"


def log_event(event_type, payload):
    """Append a governance event."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "payload": payload if isinstance(payload, dict) else {"value": payload},
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_events(limit=200):
    """Return the most recent events."""
    if not LOG.exists():
        return []
    lines = LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
    out = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
