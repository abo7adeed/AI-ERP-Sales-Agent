#!/usr/bin/env python3
"""
Test script for PHASE 1: Conversation Memory

Run this to verify:
1. Conversation history storage works
2. History retrieval works correctly
3. Formatting for prompt injection works
"""

import json
import sys
import os
from pathlib import Path

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.agent.conversation_manager import (
    add_message,
    clear_history,
    format_history_for_prompt,
    get_history,
)


def test_add_and_retrieve_messages():
    """Test adding messages and retrieving them."""
    print("\n[PASS] TEST 1: Add and retrieve messages")
    print("=" * 50)

    user_id = "test_user_123"
    clear_history(user_id)  # Start fresh

    # Add some messages
    add_message(user_id, "user", "السلام عليكم، أريد موبايل أيفون")
    add_message(user_id, "assistant", "وعليكم السلام، لدينا عدة أيفونات متاحة")
    add_message(user_id, "user", "كم سعر الأيفون 14؟")
    add_message(user_id, "assistant", "سعر الأيفون 14 هو 5000 جنيه")

    # Retrieve messages
    history = get_history(user_id, limit=5)

    print(f"[OK] Added 4 messages for user_id={user_id}")
    print(f"[OK] Retrieved {len(history)} messages")
    assert len(history) == 4, f"Expected 4 messages, got {len(history)}"

    print("\nRetrieved messages:")
    for i, msg in enumerate(history, 1):
        print(f"  {i}. [{msg['role']}]: {msg['content']}")

    print("[PASS] TEST 1 PASSED\n")


def test_limit_history():
    """Test that limit parameter works correctly."""
    print("[PASS] TEST 2: Limit history to 5 messages")
    print("=" * 50)

    user_id = "test_user_limit"
    clear_history(user_id)

    # Add 10 messages
    for i in range(1, 11):
        add_message(user_id, "user" if i % 2 == 1 else "assistant", f"Message {i}")

    # Retrieve with limit=5
    history = get_history(user_id, limit=5)

    print(f"[OK] Added 10 messages")
    print(f"[OK] Retrieved last {len(history)} messages (with limit=5)")
    assert len(history) == 5, f"Expected 5 messages, got {len(history)}"

    # Verify we got the last 5
    assert history[0]["content"] == "Message 6", "Should get messages 6-10"
    assert history[-1]["content"] == "Message 10", "Should get messages 6-10"

    print("[OK] Retrieved messages 6-10 (the last 5)")
    print("[PASS] TEST 2 PASSED\n")


def test_format_history():
    """Test history formatting for prompt injection."""
    print("[PASS] TEST 3: Format history for prompt injection")
    print("=" * 50)

    user_id = "test_user_format"
    clear_history(user_id)

    add_message(user_id, "user", "مرحبا")
    add_message(user_id, "assistant", "السلام عليكم وعليكم السلام")
    add_message(user_id, "user", "ما أسعار الموبايلات؟")

    history = get_history(user_id, limit=5)
    formatted = format_history_for_prompt(history)

    print("Original history:")
    for msg in history:
        print(f"  [{msg['role']}]: {msg['content']}")

    print("\nFormatted for prompt:")
    print(formatted)

    # Verify format contains expected elements
    assert "سياق المحادثة السابقة" in formatted, "Should contain Arabic header"
    assert "العميل:" in formatted, "Should contain 'العميل' label"
    assert "المساعد:" in formatted, "Should contain 'المساعد' label"
    assert "مرحبا" in formatted, "Should contain user message"
    assert "السلام عليكم وعليكم السلام" in formatted, "Should contain assistant message"

    print("[OK] Format contains all expected elements")
    print("[PASS] TEST 3 PASSED\n")


def test_empty_history():
    """Test behavior with no history."""
    print("[PASS] TEST 4: Empty history (no prior messages)")
    print("=" * 50)

    user_id = "brand_new_user"
    clear_history(user_id)

    history = get_history(user_id, limit=5)
    formatted = format_history_for_prompt(history)

    print(f"[OK] Retrieved history for new user: {len(history)} messages")
    print(f"[OK] Formatted output is empty: {formatted == ''}")

    assert len(history) == 0, "New user should have no history"
    assert formatted == "", "Empty history should format to empty string"

    print("[PASS] TEST 4 PASSED\n")


def test_conversation_file_structure():
    """Test that conversation files are structured correctly."""
    print("[PASS] TEST 5: Conversation file structure")
    print("=" * 50)

    user_id = "test_file_structure"
    clear_history(user_id)

    add_message(user_id, "user", "Test message")
    add_message(user_id, "assistant", "Test response")

    # Read the JSON file directly
    from backend.agent.conversation_manager import _get_conversation_file

    conversation_file = _get_conversation_file(user_id)
    with open(conversation_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[OK] Conversation file created at: {conversation_file}")
    print(f"[OK] File contains {len(data)} messages")

    # Verify structure
    for i, msg in enumerate(data):
        print(f"\n  Message {i + 1}:")
        print(f"    - role: {msg['role']}")
        print(f"    - content: {msg['content'][:30]}...")
        print(f"    - timestamp: {msg['timestamp']}")

        assert "role" in msg, f"Message {i} missing 'role'"
        assert "content" in msg, f"Message {i} missing 'content'"
        assert "timestamp" in msg, f"Message {i} missing 'timestamp'"

    print("\n[OK] All messages have correct structure")
    print("[PASS] TEST 5 PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("PHASE 1: CONVERSATION MEMORY - TEST SUITE")
    print("=" * 50)

    try:
        test_add_and_retrieve_messages()
        test_limit_history()
        test_format_history()
        test_empty_history()
        test_conversation_file_structure()

        print("=" * 50)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 50 + "\n")

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
