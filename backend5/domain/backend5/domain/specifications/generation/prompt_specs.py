# File: /backend5/domain/specifications/generation/prompt_specs.py

"""
This file defines prompt requirement specifications for content generation in the D&D framework.
"""

class PromptSpecification:
    """
    Specification for validating prompt requirements.
    """

    def __init__(self, required_elements):
        self.required_elements = required_elements

    def is_satisfied_by(self, prompt):
        """
        Check if the prompt satisfies the required elements.
        """
        return all(element in prompt for element in self.required_elements)

    def get_violation_reasons(self, prompt):
        """
        Get reasons for violations if the prompt does not satisfy the requirements.
        """
        missing_elements = [element for element in self.required_elements if element not in prompt]
        return missing_elements if missing_elements else None

# Example usage
# prompt_spec = PromptSpecification(required_elements=["theme", "character", "goal"])
# if not prompt_spec.is_satisfied_by(prompt):
#     reasons = prompt_spec.get_violation_reasons(prompt)
#     print("Prompt does not satisfy requirements:", reasons)