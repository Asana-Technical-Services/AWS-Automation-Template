"""
sharedLayer/asana_client.py
A wrapper on python Requests module with extra error handling and exponential backoff for rate limits
"""
import requests
import time
import os
from urllib import parse as urlUtil
import json
import random

class Asana_Client:

    def __init__(self, api_key) -> None:
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        pass

    def random_asana_color(self):
        colors = [
            "dark-blue",
            "dark-brown",
            "dark-green",
            "dark-orange",
            "dark-pink",
            "dark-purple",
            "dark-red",
            "dark-teal",
            "dark-warm-gray",
            "light-blue",
            "light-green",
            "light-orange",
            "light-pink",
            "light-purple",
            "light-red",
            "light-teal",
            "light-warm-gray",
            "light-yellow",
        ]
        color_index = random.randint(0, len(colors) - 1)
        return colors[color_index]

    def request(self, method, urlFragment, data={}):
        """
        make a request to Asana with a given method, url extension, and data

        """
        if urlFragment.startswith("/"):
            urlFragment = urlFragment[1:]

        url = urlUtil.urljoin(os.environ["ASANA_API_URL"], urlFragment)
        data_string = json.dumps(data)

        # init retry variables for exponential backoff if we hit rate limits.
        retry_on_error = True
        retries = 1
        max_retries = 8
        backoff_s = 0.250

        while retry_on_error:
            try:
                response = requests.request(
                    method=method, url=url, headers=self.headers, data=data_string
                )
                status = response.status_code
                if (status in [429, 500, 503]) & (retries <= max_retries):
                    # either hit rate limits or server has an issue, we'll retry with exponential backoff
                    time.sleep(backoff_s)
                    backoff_s = 2 * backoff_s
                else:
                    # we didn't hit rate limits, so we won't retry
                    retry_on_error = False

                    # raise an exception for any non-success statuses
                    response.raise_for_status()

                    response_content = json.loads(response.content)

                    # often relevant data from Asana is wrapped in "data". unwrap it if it exists.
                    if "data" in response_content:
                        result = response_content["data"]
                    else:
                        result = response_content

                    return {"success": True, "data": result}

            except requests.exceptions.HTTPError as error:
                # Catch and clearly log any error related to the actual API call. Other exceptions will bubble up.
                print(f"{method} request to {url} with body {data_string} failed:")
                print(error)
                print(response.content)
                return {"success": False, "data": {}}

        # if we reach this point, we haven't successfully made any call even after retries. Log and return a failure.
        print(
            f"after {max_retries} attempts, still got error code {status} for {method} request to {url} with body {data_string}"
        )
        return {"success": False, "result": {}}
