from locust import HttpUser, between, task


class GudlftUser(HttpUser):
    """Performance journey used with six simultaneous users."""

    wait_time = between(0.5, 1.5)

    def on_start(self):
        """Log in and perform one real points update per virtual user."""
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})
        with self.client.post(
            "/purchasePlaces",
            data={"competition": "Fall Classic", "places": "1"},
            name="POST points update",
            catch_response=True,
        ) as response:
            if b"1 place(s) booked" not in response.content:
                response.failure("Booking was not confirmed")
            elif response.elapsed.total_seconds() > 2:
                response.failure("Points update took more than 2 seconds")

    @task(3)
    def list_competitions(self):
        with self.client.post(
            "/showSummary",
            data={"email": "john@simplylift.co"},
            name="POST competition list",
            catch_response=True,
        ) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Competition list took more than 5 seconds")

    @task(1)
    def display_points(self):
        with self.client.get(
            "/pointsDisplay", name="GET public points", catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Points display took more than 5 seconds")
