class DependencyResolver:
    """
    The DependencyResolver class is responsible for resolving dependencies
    between various content entities in the D&D content generation framework.
    """

    def __init__(self):
        self.dependencies = {}

    def register_dependency(self, content_type, dependencies):
        """
        Register dependencies for a specific content type.

        :param content_type: The type of content (e.g., spell, feat).
        :param dependencies: A list of dependencies for the content type.
        """
        self.dependencies[content_type] = dependencies

    def resolve_dependencies(self, content_type):
        """
        Resolve and return the dependencies for the specified content type.

        :param content_type: The type of content for which to resolve dependencies.
        :return: A list of resolved dependencies.
        """
        return self.dependencies.get(content_type, [])

    def clear_dependencies(self):
        """
        Clear all registered dependencies.
        """
        self.dependencies.clear()