class TemplateRepository:
    """
    Interface for template repository operations.
    """

    def get_template(self, template_id: str) -> dict:
        """
        Retrieve a template by its ID.
        """
        pass

    def save_template(self, template_data: dict) -> None:
        """
        Save a new template.
        """
        pass

    def update_template(self, template_id: str, template_data: dict) -> None:
        """
        Update an existing template.
        """
        pass

    def delete_template(self, template_id: str) -> None:
        """
        Delete a template by its ID.
        """
        pass

    def list_templates(self) -> list:
        """
        List all templates.
        """
        pass