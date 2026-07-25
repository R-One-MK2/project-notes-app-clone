"""
Tests for the Notes domain Value Objects: Title and Content.

SESSION 3 (Part A) — Value Objects
Goal: Value Objects are immutable, self-validating primitives.
      Constructing them with invalid input raises immediately (fail-fast).

Cycles:
  [x] Cycle 13: Title rejects empty string                       → AC-07
  [x] Cycle 14: Title rejects whitespace-only string             → AC-08
  [x] Cycle 15: Title strips leading/trailing whitespace         → AC-10
  [x] Cycle 16: Title rejects string over 255 chars              → AC-09
  [x] Cycle 17: Title equality (VOs equal if values are)         → (extra)
  [x] Cycle 18: Content rejects string over 1MB                  → AC-11
  [x] Cycle 19: Content accepts empty string                     → AC-12
"""

import pytest
from app.notes.models import Content, Title

#  TITLE


def test_title_rejects_empty_string():
    """
    AC-07: Empty string title is rejected.

    Enforced by the Title Value Object at construction.
    Requirement: FR-002 — title is required.
    """
    with pytest.raises(ValueError, match="empty"):
        Title("")


def test_title_rejects_whitespace_only_string():
    """
    AC-08: Whitespace-only title is rejected.

    A title consisting only of spaces/tabs/newlines is semantically
    equivalent to empty and must be rejected.
    Requirement: FR-002 — title requires meaningful content.
    """
    with pytest.raises(ValueError, match="empty"):
        Title("   ")


def test_title_strips_leading_and_trailing_whitespace():
    """
    AC-10: Title normalizes whitespace at construction.

    Leading and trailing whitespace is removed. Internal whitespace
    is preserved (only the boundaries are stripped).
    Requirement: FR-002 — title stored in canonical form.
    """
    title = Title(" hello world ")
    assert title.value == "hello world"


def test_title_rejects_string_over_max_length():
    """
    AC-09: Title over max length (255 chars) is rejected.

    Enforced at construction. Length is measured on the stripped
    value (canonical form), not the raw input.
    Requirement: FR-002 — title must fit within storage constraints.
    """
    too_long = "a" * 256
    with pytest.raises(ValueError, match="255"):
        Title(too_long)


def test_titles_with_same_value_are_equal_and_hashable():
    """
    Title VO contract: value equality.

    Two Title objects with the same value are equal and hash to
    the same value (usable in sets/dicts).
    Two Titles with different values are not equal.
    """
    t1 = Title("Grocery")
    t2 = Title("Grocery")
    t3 = Title("Shopping")

    # Assert equal
    assert t1 == t2

    # Different Value -> Not Equal
    assert t1 != t3

    # Equal Objects must have equal hashes
    assert hash(t1) == hash(t2)

    # Usable in a set: Duplicates deduplicated
    # assert len({t1, t2, t3}) == 2
    assert len({t1, t2, t3}) == 2


def test_title_is_not_equal_to_different_type():
    """
    Title VO contract: type safety.

    A Title is never equal to a non-Title, even if the underlying
    string matches. Prevents subtle bugs where raw strings are
    accidentally compared to VOs.
    """

    title = Title("Grocery")

    assert title != "Grocery"
    assert title != 42
    assert title != None


# CONTENT


def test_content_rejects_string_over_max_size():
    """
    AC-11: Content over max size (1 MB) is rejected.

    Enforced at construction. Size measured in UTF-8 bytes for
    unicode safety.
    Requirement: FR-002 — content must fit within storage constraints.
    """
    too_large = "a" * (Content.MAX_BYTES + 1)

    with pytest.raises(ValueError, match="1"):
        Content(too_large)


def test_content_accepts_empty_string():
    """
    AC-12: Empty content is allowed.

    Unlike Title, empty Content is a valid state. Users may create
    a note with just a title and add content later.
    Requirement: FR-002 — content is optional.
    """
    content = Content("")
    assert content.value == ""


def test_contents_with_same_value_are_equal_and_hashable():
    """Content VO contract: value equality and hashing."""
    c1 = Content("Milk, eggs")
    c2 = Content("Milk, eggs")
    c3 = Content("Bread")

    assert c1 == c2
    assert c1 != c3
    assert hash(c1) == hash(c2)
    assert len({c1, c2, c3}) == 2


def test_content_is_not_equal_to_different_type():
    """Content VO contract: type safety."""
    content = Content("Milk")
    assert content != "Milk"
    assert content != 42
