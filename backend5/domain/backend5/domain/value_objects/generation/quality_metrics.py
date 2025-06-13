class QualityMetrics:
    """
    Represents the quality assessment metrics for generated content.
    """

    def __init__(self, balance_score: float, thematic_coherence: float, compliance_score: float):
        self.balance_score = balance_score
        self.thematic_coherence = thematic_coherence
        self.compliance_score = compliance_score

    def is_high_quality(self) -> bool:
        """
        Determines if the content meets high-quality standards based on metrics.
        """
        return (self.balance_score >= 8.0 and
                self.thematic_coherence >= 8.0 and
                self.compliance_score >= 8.0)

    def __repr__(self) -> str:
        return (f"QualityMetrics(balance_score={self.balance_score}, "
                f"thematic_coherence={self.thematic_coherence}, "
                f"compliance_score={self.compliance_score})")