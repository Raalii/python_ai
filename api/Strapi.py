import requests


class StrapiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.jwt_token = None
        self.jwt_token = self.connect()
        self.cameras = self.fetch_all_data()

    def connect(self):
        """Fonction qui va retourner le token nécéssaire à toute les interactions avec l'API"""
        response = self.post('auth/local', {"identifier" : "python@gmail.com", "password" : "python"})
        return response["jwt"]

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
    
    def fetch_all_data(self):
        response = self.get('cameras?populate=*')
        data = []
        for camera in response["data"]:
            attr = camera["attributes"]
            data.append({"id" : camera["id"], "url" : attr["url"], "polygons" : attr["polygons"]})
        
        return data
        










    



