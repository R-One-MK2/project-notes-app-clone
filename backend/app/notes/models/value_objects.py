"""
Value Objects for the Notes domain.

Value Objects are immutable and validate themselves at construction.
Invalid states are impossible — construction fails fast with ValueError.
"""


class Title:
    """
    A note's title. Non-empty string, max 255 chars, no leading/trailing whitespace."""

    MAX_LENGTH = 255

    def __init__(self, value: str) -> None:
        # Raise error if no value
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title cannot be empty")
        if len(stripped) > self.MAX_LENGTH:
            raise ValueError(f"Title exceeds {self.MAX_LENGTH} characters")
        self._value = stripped

    @property
    def value(self) -> str:
        return self._value
