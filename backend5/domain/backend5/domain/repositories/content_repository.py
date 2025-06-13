from abc import ABC, abstractmethod

class ContentRepository(ABC):
    @abstractmethod
    def add_content(self, content):
        """Add new content to the repository."""
        pass

    @abstractmethod
    def get_content(self, content_id):
        """Retrieve content by its ID."""
        pass

    @abstractmethod
    def update_content(self, content):
        """Update existing content in the repository."""
        pass

    @abstractmethod
    def delete_content(self, content_id):
        """Delete content from the repository by its ID."""
        pass

    @abstractmethod
    def list_all_content(self):
        """List all content in the repository."""
        pass