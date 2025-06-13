class GenerationAggregate:
    """
    Generation aggregate managing the lifecycle of generation requests,
    results, and associated business rules.
    """

    def __init__(self):
        self.requests = []
        self.results = []

    def add_request(self, request):
        self.requests.append(request)

    def add_result(self, result):
        self.results.append(result)

    def get_requests(self):
        return self.requests

    def get_results(self):
        return self.results

    def clear_requests(self):
        self.requests.clear()

    def clear_results(self):
        self.results.clear()