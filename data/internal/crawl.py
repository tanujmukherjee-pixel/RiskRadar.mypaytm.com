import requests
import pandas as pd

class Tools:
    def __init__(self):
        pass

    def crawl_website(self, url: str) -> str:
        """
        Takes website url as input and crawl that url
        :param url: Url to be crawlled.
        :return: crawelled data.
        """

        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            print(response.text)
            return response.text
        except requests.RequestException as e:
            print(e)
            return f"Error querying chatbot: {str(e)}"
