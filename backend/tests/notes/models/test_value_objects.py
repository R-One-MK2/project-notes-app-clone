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
  [ ] Cycle 17: Title equality (VOs equal if values are)         → (extra)
  [ ] Cycle 18: Content rejects string over 1MB                  → AC-11
  [ ] Cycle 19: Content accepts empty string                     → AC-12
"""

import pytest
from app.notes.models.value_objects import Title


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


def test_title_strips_leading_and_trailning_whitespace():
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
