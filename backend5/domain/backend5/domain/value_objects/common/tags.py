class Tags:
    """
    Represents a collection of tags used for categorizing and organizing content.
    """

    def __init__(self, tags=None):
        """
        Initializes the Tags object with a list of tags.

        :param tags: Optional list of tags. Defaults to an empty list.
        """
        self._tags = tags if tags is not None else []

    def add_tag(self, tag):
        """
        Adds a tag to the collection.

        :param tag: The tag to add.
        """
        if tag not in self._tags:
            self._tags.append(tag)

    def remove_tag(self, tag):
        """
        Removes a tag from the collection.

        :param tag: The tag to remove.
        """
        if tag in self._tags:
            self._tags.remove(tag)

    def get_tags(self):
        """
        Returns the list of tags.

        :return: List of tags.
        """
        return self._tags

    def __repr__(self):
        return f"Tags({self._tags})"