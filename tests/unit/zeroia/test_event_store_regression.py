from datetime import datetime, timedelta
from pathlib import Path

from modules.zeroia.event_store import EventStore, EventType


def test_store_event_uses_event_type_key(tmp_path: Path):
    store = EventStore(cache_dir=str(tmp_path / "events.json"))

    store.store_event("decision_made", {"foo": "bar"})
    events = store.get_events(event_type="decision_made")

    assert len(events) == 1
    assert events[0]["event_type"] == "decision_made"
    assert "type" not in events[0]


def test_clear_old_events_deletes_old_entries_without_event_prefix(tmp_path: Path):
    store = EventStore(cache_dir=str(tmp_path / "events.json"))
    event_id = store.add_event(EventType.DECISION_MADE, {"value": 1}, module="zeroia")
    assert event_id in store.events

    old_timestamp = (datetime.now() - timedelta(days=40)).isoformat()
    store.events[event_id]["timestamp"] = old_timestamp

    deleted = store.clear_old_events(days_to_keep=30)

    assert deleted == 1
    assert event_id not in store.events

