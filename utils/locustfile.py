"""
This file defines load testing behaviours for the web application
"""


from locust import HttpUser, between, task


class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)

    @task(10)
    def index(self):
        self.client.get("/")

    # @task(3)
    # def view_items(self):
    #     for item_id in range(10):
    #         self.client.get(f"/item?id={item_id}", name="/item")
    #         time.sleep(1)

    def on_start(self):
        pass
        # self.client.post("/login", json={"username":"foo", "password":"bar"})
