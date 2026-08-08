"""Shared schema helpers for Raku companion training examples."""

from __future__ import annotations

import json
from typing import Any


SCHEMA_VERSION = "1.0"

BASE_ACTIONS = {
    "speak",
    "play_emote",
    "play_dance",
    "set_expression",
    "mark_location",
    "give_directions",
    "answer_lore",
    "open_shop",
    "call_service",
    "idle",
}

VIP_ACTIONS = {
    "give_item",
    "follow_player",
    "stop_following",
    "ride_with_player",
    "guard_owner",
    "combat_assist",
    "flee",
}

MISSION_ACTIONS = {
    "propose_mission",
    "start_mission",
    "mark_target",
    "stash_loot",
}

ALL_ACTIONS = BASE_ACTIONS | VIP_ACTIONS | MISSION_ACTIONS

GIVEABLE_ITEMS = {
    "water",
    "sandwich",
    "bandage",
    "armor",
    "pistol_ammo",
    "smg_ammo",
    "radio",
    "repairkit",
}

MISSION_POOL = {
    "store_stickup",
    "corner_jack",
    "stash_pickup",
    "escort_escape",
    "ambush_rescue",
}

EMOTES = {
    "idle",
    "wave",
    "thinking",
    "handover",
    "scared",
    "handsup",
    "lean",
    "dance_idle",
    "celebrate",
    "angry",
}


SYSTEM_PROMPT = """You are the action brain for StayDangerous AI NPCs.
Return ONLY one JSON object. No markdown. No prose outside JSON.

Voice: street-literate, in-character, sharp, uncensored GTA RP energy. Keep overhead speech short.
Hard limits: no real-world crime instructions, no slurs, no minor sexual content, no staff/OOC secret leaks, no "as an AI".

Choose exactly one action from allowed_actions. If unsure, choose idle or speak.
Never invent items, missions, exports, or Lua events. Use only what the observation allows.
Combat details are handled by native GTA AI; you only choose high-level intent and short speech.
"""


def compact_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def validate_action(action: dict[str, Any]) -> tuple[bool, str]:
    if not isinstance(action, dict):
        return False, "action_not_object"
    if action.get("schema_version") != SCHEMA_VERSION:
        return False, "bad_schema_version"
    name = action.get("action")
    if name not in ALL_ACTIONS:
        return False, "unknown_action"
    if "say" in action and len(str(action["say"])) > 220:
        return False, "say_too_long"
    if "item" in action and action["item"] not in GIVEABLE_ITEMS:
        return False, "bad_item"
    if "mission" in action and action["mission"] not in MISSION_POOL:
        return False, "bad_mission"
    if "emote" in action and action["emote"] not in EMOTES:
        return False, "bad_emote"
    if "quantity" in action:
        try:
            qty = int(action["quantity"])
        except (TypeError, ValueError):
            return False, "bad_quantity"
        if qty < 1 or qty > 5:
            return False, "quantity_out_of_range"
    return True, "ok"

