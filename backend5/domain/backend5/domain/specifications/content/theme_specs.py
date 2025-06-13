class ThemeSpecification:
    """
    Specification for ensuring thematic consistency in generated content.
    """

    def __init__(self, required_themes):
        self.required_themes = required_themes

    def is_satisfied_by(self, content):
        """
        Check if the content satisfies the theme requirements.
        """
        return all(theme in content.themes for theme in self.required_themes)

    def get_violation_reasons(self, content):
        """
        Get reasons for theme specification violations.
        """
        missing_themes = [theme for theme in self.required_themes if theme not in content.themes]
        return [f"Missing required theme: {theme}" for theme in missing_themes] if missing_themes else []