class DomainEvent:
    """Base class for all domain events."""
    
    def __init__(self):
        self.timestamp = self._get_current_timestamp()

    def _get_current_timestamp(self):
        """Get the current timestamp."""
        from datetime import datetime
        return datetime.now()