from threading import Thread

from flask import Flask, jsonify, request
from flask_cors import CORS

# Ajoutez cette ligne après la création de l'instance Flask
class WebhookHandler:
    def __init__(self, host='192.168.1.152', port=3030):
        self.app = Flask(__name__)
        self.host = host
        self.port = port

        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            print(request)
            data = request.json
            print("Webhook received:", data)

            # Utiliser un thread pour traiter les données du webhook sans bloquer la réponse
            webhook_thread = Thread(target=self.process_webhook_data, args=(data,))
            webhook_thread.start()

            return jsonify({"message": "Webhook received and processing"})

    def process_webhook_data(self, data):
        # Traiter les données du webhook ici, par exemple, intégrer la détection de personnes avec YOLOv4
        print(data)
        pass

    def run(self):
        CORS(self.app.run(host=self.host, port=self.port, threaded=True))

