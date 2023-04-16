class Alert:
    def __init__(self, camera_id, timestamp, api_handler):
        self.camera_id = camera_id
        self.timestamp = timestamp
        self.api_handler = api_handler
        self.id = 0
        

    def lancer_alerte(self, camera_id, nom_alerte, camera_url):
        camera_url = "RECORDING"  # Ajouter le champ "RECORDING"
        # Lancer l'alerte et uploader sur Strapi
        data = {"data": {
            "camera": camera_id,
            "name": nom_alerte,
            "url": camera_url,
        }
        }
        response = self.api_handler.post("alerts", data=data)

        if response:
            print("Alerte créée avec succès et uploadée sur Strapi")
        else:
            print("Erreur lors de l'upload de l'alerte sur Strapi")

        self.id = response['data']['id']

    def mettre_a_jour_url_camera(self, new_camera_url):
        # Mettre à jour l'URL de la caméra
        data = {
            "data": {
                "url": f'http://localhost:1337{new_camera_url}'
            }
        }
        response = self.api_handler.put(f"alerts/{self.id}", data=data)
        if response:
            print("URL de la caméra mise à jour avec succès")
        else:
            print("Erreur lors de la mise à jour de l'URL de la caméra")
