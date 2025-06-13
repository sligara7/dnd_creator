class PermissionSpecification:
    """
    Specification for user permissions in the system.
    """

    def __init__(self, user):
        self.user = user

    def can_create_content(self):
        """
        Check if the user has permission to create content.
        """
        return self.user.role in ['admin', 'editor']

    def can_edit_content(self, content_owner):
        """
        Check if the user has permission to edit content owned by another user.
        """
        return self.user.role in ['admin', 'editor'] or self.user.id == content_owner.id

    def can_delete_content(self, content_owner):
        """
        Check if the user has permission to delete content owned by another user.
        """
        return self.user.role == 'admin' or self.user.id == content_owner.id

    def can_view_content(self):
        """
        Check if the user has permission to view content.
        """
        return True  # All users can view content

    def can_manage_users(self):
        """
        Check if the user has permission to manage other users.
        """
        return self.user.role == 'admin'