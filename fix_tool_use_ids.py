"""
Utility to fix duplicate tool_use IDs in Anthropic API message arrays.

The Anthropic Messages API requires all tool_use block IDs to be unique across
the entire messages array. When tool_use IDs are duplicated (e.g., from retries,
copy-paste, or conversation reconstruction), the API returns:

    400 invalid_request_error: tool_use ids must be unique

This module provides functions to detect and fix duplicate tool_use IDs.
"""

import uuid
from copy import deepcopy
from typing import Any


def generate_tool_use_id() -> str:
    """Generate a unique tool_use ID in the Anthropic format."""
    return f"toolu_{uuid.uuid4().hex[:24]}"


def find_duplicate_tool_use_ids(messages: list[dict[str, Any]]) -> dict[str, list[tuple[int, int]]]:
    """Find duplicate tool_use IDs in a messages array.

    Returns a dict mapping each duplicated ID to a list of (message_index, content_block_index)
    locations where it appears.
    """
    seen: dict[str, list[tuple[int, int]]] = {}

    for msg_idx, message in enumerate(messages):
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block_idx, block in enumerate(content):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tool_id = block.get("id")
                if tool_id:
                    seen.setdefault(tool_id, []).append((msg_idx, block_idx))

    return {tid: locs for tid, locs in seen.items() if len(locs) > 1}


def fix_tool_use_ids(messages: list[dict[str, Any]], *, in_place: bool = False) -> list[dict[str, Any]]:
    """Fix duplicate tool_use IDs in a messages array.

    For each set of duplicates, keeps the first occurrence unchanged and assigns
    new unique IDs to subsequent occurrences. Also updates any corresponding
    tool_result blocks that reference the old ID.

    Args:
        messages: The messages array to fix.
        in_place: If True, modify messages in place. If False (default), work on a deep copy.

    Returns:
        The fixed messages array.
    """
    if not in_place:
        messages = deepcopy(messages)

    duplicates = find_duplicate_tool_use_ids(messages)
    if not duplicates:
        return messages

    # Build a mapping of old_id -> new_id for all duplicate occurrences (skip first)
    id_remap: dict[str, str] = {}
    # Track which specific (msg_idx, block_idx) locations need remapping
    location_remap: dict[tuple[int, int], str] = {}

    for old_id, locations in duplicates.items():
        # Keep the first occurrence, remap the rest
        for msg_idx, block_idx in locations[1:]:
            new_id = generate_tool_use_id()
            location_remap[(msg_idx, block_idx)] = new_id

    # First pass: remap the duplicate tool_use blocks
    all_remapped_ids: dict[str, list[str]] = {}  # old_id -> [new_ids]
    for (msg_idx, block_idx), new_id in location_remap.items():
        block = messages[msg_idx]["content"][block_idx]
        old_id = block["id"]
        block["id"] = new_id
        all_remapped_ids.setdefault(old_id, []).append(new_id)

    # Second pass: for tool_result blocks referencing a remapped ID, update them.
    # Strategy: the first tool_result for a duplicated ID corresponds to the
    # kept (first) tool_use, so we skip it. Subsequent tool_results get remapped
    # to the new IDs in order.
    result_counters: dict[str, int] = {old_id: 0 for old_id in all_remapped_ids}

    for msg_idx, message in enumerate(messages):
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block_idx, block in enumerate(content):
            if isinstance(block, dict) and block.get("type") == "tool_result":
                ref_id = block.get("tool_use_id")
                if ref_id in result_counters:
                    count = result_counters[ref_id]
                    if count == 0:
                        # First tool_result matches the kept tool_use — skip
                        result_counters[ref_id] = 1
                    else:
                        new_ids = all_remapped_ids[ref_id]
                        idx = count - 1
                        if idx < len(new_ids):
                            block["tool_use_id"] = new_ids[idx]
                        result_counters[ref_id] = count + 1

    return messages


def validate_tool_use_ids(messages: list[dict[str, Any]]) -> list[str]:
    """Validate that all tool_use IDs are unique and tool_results reference valid IDs.

    Returns a list of error descriptions. Empty list means valid.
    """
    errors = []

    # Check uniqueness
    duplicates = find_duplicate_tool_use_ids(messages)
    for tid, locations in duplicates.items():
        locs_str = ", ".join(f"messages[{m}].content[{b}]" for m, b in locations)
        errors.append(f"Duplicate tool_use id '{tid}' at: {locs_str}")

    # Check that all tool_results reference existing tool_use IDs
    tool_use_ids: set[str] = set()
    for message in messages:
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tool_use_ids.add(block.get("id", ""))

    for msg_idx, message in enumerate(messages):
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block_idx, block in enumerate(content):
            if isinstance(block, dict) and block.get("type") == "tool_result":
                ref_id = block.get("tool_use_id")
                if ref_id and ref_id not in tool_use_ids:
                    errors.append(
                        f"tool_result at messages[{msg_idx}].content[{block_idx}] "
                        f"references unknown tool_use_id '{ref_id}'"
                    )

    return errors
