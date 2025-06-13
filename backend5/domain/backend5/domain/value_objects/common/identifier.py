class Identifier:
    """
    Strongly-typed ID class for domain entities.
    Ensures type safety and consistency across the application.
    """

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Identifier value must be a string.")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        if isinstance(other, Identifier):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"Identifier(value={self.value})"