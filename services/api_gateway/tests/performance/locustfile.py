from locust import HttpUser, task, between

class APIGatewayUser(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        """Setup for each user."""
        # Get API key or token
        self.headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }
    
    @task(3)
    def get_health(self):
        """Test health endpoint."""
        self.client.get("/health", headers=self.headers)
    
    @task(2)
    def get_services(self):
        """Test service discovery endpoint."""
        self.client.get("/discovery/services", headers=self.headers)
    
    @task(1)
    def get_metrics(self):
        """Test metrics endpoint."""
        self.client.get("/monitoring/metrics", headers=self.headers)
