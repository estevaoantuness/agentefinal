"""Slot tracking utilities for NLP intents."""
from typing import Dict, List


INTENT_SCHEMAS: Dict[str, Dict[str, List[str]]] = {
    "view_tasks": {
        "required": [],
        "optional": ["filter_status"],
    },
    "create_task": {
        "required": ["title"],
        "optional": ["description", "priority"],
    },
    "mark_done": {
        "required": ["task_numbers"],
        "optional": [],
    },
    "mark_in_progress": {
        "required": ["task_numbers"],
        "optional": [],
    },
    "view_progress": {
        "required": [],
        "optional": [],
    },
}


class SlotTracker:
    """Check for missing slots based on intent schema."""

    def __init__(self, schemas: Dict[str, Dict[str, List[str]]] = None):
        self.schemas = schemas or INTENT_SCHEMAS

    def check_missing_slots(self, intent: str, provided_args: Dict[str, any]) -> List[str]:
        schema = self.schemas.get(intent)
        if not schema:
            return []
        missing = []
        for slot in schema.get("required", []):
            if not provided_args.get(slot):
                missing.append(slot)
        return missing
