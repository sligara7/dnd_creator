class IterationManager:
    """
    Manages the iteration process for content generation,
    ensuring that each iteration adheres to the defined
    constraints and quality metrics.
    """

    def __init__(self, generation_service, quality_assessor):
        self.generation_service = generation_service
        self.quality_assessor = quality_assessor

    def run_iterations(self, content_request, max_iterations=10):
        """
        Runs a specified number of iterations for content generation.

        Args:
            content_request: The request object containing generation parameters.
            max_iterations: The maximum number of iterations to run.

        Returns:
            A list of generated content results.
        """
        results = []
        for iteration in range(max_iterations):
            generated_content = self.generation_service.generate(content_request)
            quality_metrics = self.quality_assessor.assess(generated_content)

            if self._is_quality_acceptable(quality_metrics):
                results.append(generated_content)
                break  # Stop if quality is acceptable

        return results

    def _is_quality_acceptable(self, quality_metrics):
        """
        Checks if the generated content meets the quality standards.

        Args:
            quality_metrics: The metrics obtained from the quality assessment.

        Returns:
            True if the quality is acceptable, False otherwise.
        """
        return quality_metrics.is_within_thresholds()