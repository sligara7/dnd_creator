class TemplateSpecification:
    """
    Specification for validating template matching criteria.
    """

    def __init__(self, required_elements):
        self.required_elements = required_elements

    def is_satisfied_by(self, template):
        """
        Check if the given template satisfies the specification.
        """
        return all(element in template.elements for element in self.required_elements)

    def get_violation_reasons(self, template):
        """
        Get reasons why the template does not satisfy the specification.
        """
        missing_elements = [element for element in self.required_elements if element not in template.elements]
        return [f"Missing required element: {element}" for element in missing_elements] if missing_elements else []