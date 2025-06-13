class ValueObject:
    """
    Base class for value objects in the domain model.
    Value objects are immutable and defined by their attributes.
    """

    def __eq__(self, other):
        if not isinstance(other, ValueObject):
            return NotImplemented
        return vars(self) == vars(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(sorted(vars(self).items())))

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in vars(self).items())})"