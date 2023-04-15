import requests

class API:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def _get_headers(self, content_type=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def upload(self, file_path):
        url = f"{self.base_url}/upload"
        headers = self._get_headers()
        files = {'files': open(file_path, 'rb')}
        response = requests.post(url, headers=headers,  files=files)
        response.raise_for_status()
        return response.json()

# Remplacez ces valeurs par votre propre URL de base et clé API
base_url = "http://localhost:1337/api"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NCwiaWF0IjoxNjgxNTE1NDY4LCJleHAiOjE2ODQxMDc0Njh9.O3Me1KtJ224TJaF4yUOMttWxD04ClrI8BeNF247mKEk"

api = API(base_url, api_key)
file_path = "./videos/video_2023-04-14_23-21-21.mp4"
response = api.upload(file_path)
print(response)