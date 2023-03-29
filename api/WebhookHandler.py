from flask import Flask, request, jsonify
from threading import Thread

class WebhookHandler:
    def __init__(self, host='0.0.0.0', port=5000):
        self.app = Flask(__name__)
        self.host = host
        self.port = port

        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            data = request.json
            # Traitez les données du webhook ici, par exemple, mettez à jour les polygones
            print("Webhook received:", data)
            
            # Si vous devez effectuer des opérations longues, vous pouvez utiliser un thread pour ne pas bloquer la réponse du webhook.
            webhook_thread = Thread(target=self.process_webhook_data, args=(data,))
            webhook_thread.start()

            return jsonify({"message": "Webhook received and processing"})

    def process_webhook_data(self, data):
        # Mettez votre logique de traitement des données du webhook ici, par exemple, mettez à jour les polygones
        pass

    def run(self):
        self.app.run(host=self.host, port=self.port)