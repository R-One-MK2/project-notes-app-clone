"""
Tests for the Notes domain Value Objects: Title and Content.

SESSION 3 (Part A) — Value Objects
Goal: Value Objects are immutable, self-validating primitives.
      Constructing them with invalid input raises immediately (fail-fast).

Cycles:
  [ ] Cycle 13: Title rejects empty string                       → AC-07
  [ ] Cycle 14: Title rejects whitespace-only string             → AC-08
  [ ] Cycle 15: Title strips leading/trailing whitespace         → AC-10
  [ ] Cycle 16: Title rejects string over 255 chars              → AC-09
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
