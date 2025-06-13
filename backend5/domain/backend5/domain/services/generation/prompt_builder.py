from typing import List

class PromptBuilder:
    """
    Service for constructing prompts based on character concepts and generation requirements.
    """

    def __init__(self):
        pass

    def build_prompt(self, character_concept: str, content_types: List[str]) -> str:
        """
        Constructs a prompt for content generation based on the character concept and desired content types.

        Args:
            character_concept (str): The character concept to base the prompt on.
            content_types (List[str]): The types of content to generate (e.g., spells, feats).

        Returns:
            str: The constructed prompt.
        """
        prompt = f"Generate the following content for a character based on the concept: '{character_concept}'.\n"
        prompt += "Content types requested:\n"
        for content_type in content_types:
            prompt += f"- {content_type}\n"
        return prompt.strip()  # Remove trailing newline characters

    def refine_prompt(self, prompt: str, additional_context: str) -> str:
        """
        Refines an existing prompt by adding additional context.

        Args:
            prompt (str): The original prompt to refine.
            additional_context (str): Additional context to include in the prompt.

        Returns:
            str: The refined prompt.
        """
        return f"{prompt}\n\nAdditional context: {additional_context}"