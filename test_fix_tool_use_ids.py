"""Tests for fix_tool_use_ids module."""

from fix_tool_use_ids import (
    find_duplicate_tool_use_ids,
    fix_tool_use_ids,
    generate_tool_use_id,
    validate_tool_use_ids,
)


def test_generate_tool_use_id_format():
    tid = generate_tool_use_id()
    assert tid.startswith("toolu_")
    assert len(tid) == 30  # "toolu_" (6) + 24 hex chars


def test_generate_tool_use_id_uniqueness():
    ids = {generate_tool_use_id() for _ in range(1000)}
    assert len(ids) == 1000


def test_find_no_duplicates():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_aaa", "content": "ok"},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_bbb", "name": "write", "input": {}},
        ]},
    ]
    assert find_duplicate_tool_use_ids(messages) == {}


def test_find_duplicates():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_aaa", "content": "ok"},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "write", "input": {}},
        ]},
    ]
    dupes = find_duplicate_tool_use_ids(messages)
    assert "toolu_aaa" in dupes
    assert len(dupes["toolu_aaa"]) == 2
    assert dupes["toolu_aaa"] == [(0, 0), (2, 0)]


def test_fix_no_duplicates_is_noop():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
    ]
    fixed = fix_tool_use_ids(messages)
    assert fixed[0]["content"][0]["id"] == "toolu_aaa"


def test_fix_duplicates():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_aaa", "content": "first result"},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "write", "input": {}},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_aaa", "content": "second result"},
        ]},
    ]
    fixed = fix_tool_use_ids(messages)

    # First occurrence keeps its ID
    assert fixed[0]["content"][0]["id"] == "toolu_aaa"
    assert fixed[1]["content"][0]["tool_use_id"] == "toolu_aaa"

    # Second occurrence gets a new ID
    new_id = fixed[2]["content"][0]["id"]
    assert new_id != "toolu_aaa"
    assert new_id.startswith("toolu_")

    # Corresponding tool_result is updated
    assert fixed[3]["content"][0]["tool_use_id"] == new_id

    # No more duplicates
    assert find_duplicate_tool_use_ids(fixed) == {}


def test_fix_does_not_mutate_original():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
    ]
    fix_tool_use_ids(messages, in_place=False)
    # Original should be unchanged
    assert messages[0]["content"][0]["id"] == "toolu_aaa"
    assert messages[1]["content"][0]["id"] == "toolu_aaa"


def test_fix_in_place():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
    ]
    fix_tool_use_ids(messages, in_place=True)
    # Second should be changed in place
    assert messages[0]["content"][0]["id"] == "toolu_aaa"
    assert messages[1]["content"][0]["id"] != "toolu_aaa"


def test_fix_multiple_duplicate_groups():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
            {"type": "tool_use", "id": "toolu_bbb", "name": "write", "input": {}},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
            {"type": "tool_use", "id": "toolu_bbb", "name": "write", "input": {}},
        ]},
    ]
    fixed = fix_tool_use_ids(messages)
    all_ids = []
    for msg in fixed:
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                all_ids.append(block["id"])
    assert len(all_ids) == len(set(all_ids)), "All IDs should be unique"


def test_fix_triple_duplicate():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
    ]
    fixed = fix_tool_use_ids(messages)
    ids = [msg["content"][0]["id"] for msg in fixed]
    assert ids[0] == "toolu_aaa"
    assert len(set(ids)) == 3


def test_handles_string_content():
    """Messages with string content (not list) should be handled gracefully."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
    ]
    fixed = fix_tool_use_ids(messages)
    assert fixed[0]["content"] == "Hello"


def test_validate_clean_messages():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_aaa", "content": "ok"},
        ]},
    ]
    assert validate_tool_use_ids(messages) == []


def test_validate_catches_duplicates():
    messages = [
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_aaa", "name": "read", "input": {}},
        ]},
    ]
    errors = validate_tool_use_ids(messages)
    assert len(errors) == 1
    assert "Duplicate" in errors[0]


def test_validate_catches_orphan_tool_result():
    messages = [
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_nonexistent", "content": "ok"},
        ]},
    ]
    errors = validate_tool_use_ids(messages)
    assert len(errors) == 1
    assert "unknown" in errors[0]


if __name__ == "__main__":
    import sys

    test_functions = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in test_functions:
        try:
            test()
            passed += 1
            print(f"  PASS  {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {test.__name__}: {e}")

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
