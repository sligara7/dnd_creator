class BaseSpecification:
    """
    Base class for all specifications in the domain.
    Provides a common interface for checking if a specification is satisfied.
    """

    def is_satisfied_by(self, candidate):
        """
        Determines if the specification is satisfied by the given candidate.

        :param candidate: The object to check against the specification.
        :return: True if the candidate satisfies the specification, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def __and__(self, other):
        """
        Combines two specifications using logical AND.

        :param other: Another specification to combine with.
        :return: A new specification that is satisfied if both specifications are satisfied.
        """
        return AndSpecification(self, other)

    def __or__(self, other):
        """
        Combines two specifications using logical OR.

        :param other: Another specification to combine with.
        :return: A new specification that is satisfied if either specification is satisfied.
        """
        return OrSpecification(self, other)


class AndSpecification(BaseSpecification):
    """
    Specification that combines two specifications using logical AND.
    """

    def __init__(self, spec1, spec2):
        self.spec1 = spec1
        self.spec2 = spec2

    def is_satisfied_by(self, candidate):
        return self.spec1.is_satisfied_by(candidate) and self.spec2.is_satisfied_by(candidate)


class OrSpecification(BaseSpecification):
    """
    Specification that combines two specifications using logical OR.
    """

    def __init__(self, spec1, spec2):
        self.spec1 = spec1
        self.spec2 = spec2

    def is_satisfied_by(self, candidate):
        return self.spec1.is_satisfied_by(candidate) or self.spec2.is_satisfied_by(candidate)