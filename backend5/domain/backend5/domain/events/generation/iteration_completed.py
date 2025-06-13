class IterationCompletedEvent:
    """
    Event published when an iteration of content generation is completed.
    
    Attributes:
        iteration_id (str): Unique identifier for the iteration.
        result (dict): The result of the iteration, containing generated content and metadata.
        timestamp (datetime): The time when the iteration was completed.
    """

    def __init__(self, iteration_id: str, result: dict, timestamp: datetime):
        self.iteration_id = iteration_id
        self.result = result
        self.timestamp = timestamp

    def __repr__(self):
        return f"<IterationCompletedEvent(iteration_id={self.iteration_id}, timestamp={self.timestamp})>"