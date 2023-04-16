from threading import Thread

from flask import Flask, jsonify, request
from flask_cors import CORS
from lib.lib import Lib
import cv2
# Ajoutez cette ligne après la création de l'instance Flask
class WebhookHandler:
    def __init__(self,  cameras, host='192.168.1.110', port=3030):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.strapi_webhook_handler = StrapiWebhookHandler(cameras)

        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            # print(request)
            data = request.json
            event_type = request.headers.get('X-Strapi-Event')
            # print("Webhook received:", data)  
            # print("Webhook received:", event_type, data)
            # Utiliser un thread pour traiter les données du webhook sans bloquer la réponse
            webhook_thread = Thread(target=self.strapi_webhook_handler.handle_event, args=(event_type, data))
            webhook_thread.start()

            return jsonify({"message": "Webhook received and processing"})

    def run(self):
        CORS(self.app.run(host=self.host, port=self.port, threaded=True))



class StrapiWebhookHandler:
    def __init__(self, cameras):
        pass
        self.cameras = cameras

    def handle_event(self, event_type, data):
        if event_type == "entry.create":
            self.handle_create(data)
        elif event_type == "entry.update":
            self.handle_update(data)
        elif event_type == "entry.delete":
            self.handle_delete(data)
        else:
            print(f"Unhandled event type: {event_type}")

    def handle_create(self, data):
        print("Create event received:", data)
        # Traitez l'événement de création ici


    def handle_update(self, data):
        print("Update event received:", data)
        # Traitez l'événement de mise à jour ici
        print(data["entry"]["url"])
        try:
            self.cameras.polygons = Lib.convert_polygons(data["entry"])
        except:
            pass
        
        self.cameras.stream = cv2.VideoCapture(data["entry"]["url"])
        
        # try:
        # except:
        #     pass
        
    def handle_delete(self, data):
        print("Delete event received:", data)
        # Traitez l'événement de suppression ici
