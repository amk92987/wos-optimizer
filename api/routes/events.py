"""
Events Guide API routes.
"""

from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()

# Load events guide data
PROJECT_ROOT = Path(__file__).parent.parent.parent
EVENTS_GUIDE_PATH = PROJECT_ROOT / "data" / "events_guide.json"


@router.get("/guide")
def get_events_guide():
    """Get the full events guide data."""
    if EVENTS_GUIDE_PATH.exists():
        with open(EVENTS_GUIDE_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {"events": {}, "cost_categories": {}, "priority_tiers": {}}


@router.get("/list")
def list_events():
    """Get a simplified list of events for quick display."""
    if not EVENTS_GUIDE_PATH.exists():
        return []

    with open(EVENTS_GUIDE_PATH, encoding='utf-8') as f:
        data = json.load(f)

    events = data.get("events", {})
    return [
        {
            "id": event_id,
            "name": event.get("name", event_id),
            "type": event.get("type", ""),
            "frequency": event.get("frequency", ""),
            "priority": event.get("priority", "C"),
            "f2p_friendly": event.get("f2p_friendly", False),
            "cost_category": event.get("cost_category", "free"),
            "description": event.get("description", ""),
        }
        for event_id, event in events.items()
    ]
