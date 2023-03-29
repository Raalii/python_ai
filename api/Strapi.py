import requests

class StrapiClient:
    def __init__(self, base_url, jwt_token=None):
        self.base_url = base_url
        self.jwt_token = jwt_token

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()











    



