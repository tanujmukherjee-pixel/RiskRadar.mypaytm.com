from locust import HttpUser, task, between
import random
import csv
import os

class FastAPIUser(HttpUser):
    wait_time = between(1, 5)  # Specify user wait time between tasks

    @task
    def chat_completion(self):
        url = "/v1/chat/completions"
        payload = {
            "model": "funnel",
            "messages": [{"role": "User", "content": f"tell me last week what is order success % for UPI to self funnel"}],
            "stream": False  # Non-streaming request
        }
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.client.post(url, json=payload, headers=headers)