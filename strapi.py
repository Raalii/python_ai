import requests
from flask import Flask, request, jsonify
from threading import Thread, Lock
import cv2
import numpy as np
import time
from twilio.rest import Client
import os
from dotenv import load_dotenv
import queue


load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBERS = ["+330788573854"]




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


class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.ret, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        thread_stream = Thread(target=self.update, args=())
        thread_stream.daemon = True
        thread_stream.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            try : 
                self.ret, self.frame = self.stream.read()
            except:
                return


    def read(self):
        return self.frame

    def release(self):
        self.stopped = True
        self.stream.release()


class VideoRecorder:
    def __init__(self, video_file_path, fps, frame_size):
        self.video_file_path = video_file_path
        self.fps = fps
        self.frame_size = frame_size
        self.video_writer = None
        self.recording = False
        self.lock = Lock()
        self.delay_counter = 0
        self.delay_seconds = 5
        

    def start_recording(self, frame):
        with self.lock:
            if not self.recording:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.video_writer = cv2.VideoWriter(self.video_file_path, fourcc, self.fps, self.frame_size)
                self.recording = True
                print("Enregistrement vidéo démarré.")

    def stop_recording(self):
        with self.lock:
            if self.recording:
                self.video_writer.release()
                self.video_writer = None
                self.recording = False
                print("Enregistrement vidéo arrêté.")

    def record_frame(self, frame):
        with self.lock:
            if self.recording:
                self.video_writer.write(frame)

    def is_recording(self):
        with self.lock:
            return self.recording

    def handle_recording(self, frame, person_detected):
        if person_detected:
            self.delay_counter = 0
            if not self.is_recording():
                self.start_recording(frame)
        else:
            if self.is_recording():
                self.delay_counter += 1
                delay_frames = self.delay_seconds * self.fps
                if self.delay_counter >= delay_frames:
                    self.stop_recording()
                    self.delay_counter = 0

        if self.is_recording():
            self.record_frame(frame)

def send_sms(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    for phone_number in RECIPIENT_PHONE_NUMBERS:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )


class PersonDetector:
    def __init__(self, weights_path, config_path, names_path, confidence_threshold=0.5, nms_threshold=0.4):
        self.net = cv2.dnn.readNet(weights_path, config_path)
        self.layer_names = self.net.getLayerNames()

        frame_size = (1920, 1080)
        self.video_recorder = VideoRecorder("output.avi", 10, frame_size)

        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        with open(names_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.polygons = [
            [(0, 0), (0, 1080), (1920, 1080), (1920, 0)],
        ]

    
    def detect_persons_in_polygons(self, frame):
        height, width, _ = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.confidence_threshold:
                    center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype('int')
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)


        person_in_polygons = False
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                if label == "person":
                    if self.polygons:
                        for polygon in self.polygons:
                            if self.point_inside_polygon(x + w // 2, y + h // 2, polygon):
                                person_in_polygons = True
                                label = str(self.classes[class_ids[i]])
                                confidence = confidences[i]
                                color = (0, 0, 255)  # Rouge pour les personnes à l'intérieur du polygone
                                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                                cv2.putText(frame, f"{label} {int(confidence * 100)}%", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                print(f"{label} {int(confidence * 100)}%")
                                # TODO : Optimiser l'actualisation
                                send_sms("Une personne a été détécté sur la caméra numéro 5, n'hésitez pas à aller regarder votre oncle")
                                
        
        self.video_recorder.handle_recording(frame, person_in_polygons)

                            
        return frame

    def point_inside_polygon(self, x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            x_intersection = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= x_intersection:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def draw_detection_zone(self, image, points, color=(0, 255, 0), thickness=2):
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        return cv2.polylines(image, [pts], True, color, thickness)
    


def maintain_fps(frame_time, start_time):
    elapsed_time = time.time() - start_time
    if elapsed_time < frame_time:
        time.sleep(frame_time - elapsed_time)

def main():
    # Initialise la capture vidéo
    cap = VideoStream(src="rtsp://admin:FIGUE95140@192.168.1.120:554/cam/realmonitor?channel=1&subtype=0&unicast=true").start()

    weights_path = "yolov4-tiny.weights"
    config_path = "yolov4-tiny.cfg"
    names_path = "coco.names"

    # Crée une instance de la classe PersonDetector
    person_detector = PersonDetector(weights_path, config_path, names_path)
    
    desired_fps = 20
    frame_time = 1.0 / desired_fps

    while True:
        start_time = time.time()
        frame = person_detector.detect_persons_in_polygons(cap.read())

        for polygon in person_detector.polygons:
            frame = person_detector.draw_detection_zone(frame, polygon)

        maintain_fps(frame_time, start_time)    
        cv2.imshow("frame", frame)
        if cv2.waitKey(60) == ord("q"):
            break


    cap.release()
    cv2.destroyAllWindows()



main()