class PromptTemplate:
    """
    Represents a template for generating prompts based on character concepts.
    """

    def __init__(self, template: str, variables: dict):
        """
        Initializes a new PromptTemplate instance.

        :param template: The prompt template string with placeholders.
        :param variables: A dictionary of variables to fill in the template.
        """
        self.template = template
        self.variables = variables

    def render(self) -> str:
        """
        Renders the prompt template by replacing placeholders with actual values.

        :return: The rendered prompt string.
        """
        return self.template.format(**self.variables)

    def __str__(self) -> str:
        """
        Returns the string representation of the prompt template.

        :return: The prompt template string.
        """
        return self.template

    def __repr__(self) -> str:
        """
        Returns the official string representation of the PromptTemplate instance.

        :return: The string representation of the PromptTemplate.
        """
        return f"PromptTemplate(template={self.template}, variables={self.variables})"