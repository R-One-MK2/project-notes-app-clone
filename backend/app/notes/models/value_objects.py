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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Title):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class Content:
    """
    A note's body content. Empty allowed, max 1 MB
    """

    MAX_BYTES = 1_048_576  # 1 MB in bytes

    def __init__(self, value) -> None:

        if len(value.encode("utf-8")) > self.MAX_BYTES:
            raise ValueError(f"Content exceeds {self.MAX_BYTES} bytes (1MB)")
        self._value = value

    @property
    def value(self):
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Content):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
