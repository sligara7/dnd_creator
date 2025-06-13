class TemplateMatcher:
    """
    Service for matching templates based on character concepts and requirements.
    """

    def __init__(self, templates):
        """
        Initializes the TemplateMatcher with a list of available templates.

        :param templates: List of templates to match against.
        """
        self.templates = templates

    def match_template(self, character_concept):
        """
        Matches a template to the given character concept.

        :param character_concept: The character concept to match a template for.
        :return: The matched template or None if no match is found.
        """
        for template in self.templates:
            if self._is_match(template, character_concept):
                return template
        return None

    def _is_match(self, template, character_concept):
        """
        Determines if the given template matches the character concept.

        :param template: The template to check.
        :param character_concept: The character concept to match against.
        :return: True if the template matches the character concept, False otherwise.
        """
        # Implement matching logic based on template criteria and character concept attributes
        return True  # Placeholder for actual matching logic

    def get_all_templates(self):
        """
        Returns all available templates.

        :return: List of all templates.
        """
        return self.templates