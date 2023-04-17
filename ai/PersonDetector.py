import datetime

import cv2
import numpy as np
from camera.CameraRecorder import CameraRecorder
from lib.lib import Lib
from ai.Alert import Alert
import pygame


pygame.mixer.init()  # Initialiser le module mixer de Pygame
pygame.mixer.music.load('./sound/alert.mp3')  # Charger le fichier audio


class PersonDetector:
    def __init__(self, weights_path, config_path, names_path, api_handler, cap, confidence_threshold=0.5, nms_threshold=0.4):
        self.net = cv2.dnn.readNet(weights_path, config_path)
        self.layer_names = self.net.getLayerNames()
        self.api_handler = api_handler
        self.alert = None
        self.cap = cap
        self.person_detected = False
        self.sound_played = False
        frame_size = (1920, 1080)
        # Créez un horodatage unique
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Créez le nom de fichier avec l'horodatage
        filename = f"./videos/video_{timestamp}.mp4"

        self.camera_recorder = CameraRecorder(filename, 10, frame_size, api_handler)

        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        with open(names_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold

    
    def detect_persons_in_polygons(self, frame, polygons):
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


        # person_in_polygons = False
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                if label == "person":
                    if polygons:
                        for polygon in polygons:
                            if self.point_inside_polygon(x + w // 2, y + h // 2, polygon):
                                # person_in_polygons = True
                                label = str(self.classes[class_ids[i]])
                                confidence = confidences[i]
                                color = (0, 0, 255)  # Rouge pour les personnes à l'intérieur du polygone
                                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                                cv2.putText(frame, f"{label} {int(confidence * 100)}%", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                # print(f"{label} {int(confidence * 100)}%")
                                # TODO : Optimiser l'actualisation
                                Lib.send_sms("Une personne a été détécté sur la caméra1 situé sur le hall 1 du salon de la tech.")
                                # TODO : person detecté
                                # instancier l'alerte et les infos ==> lancer alerte
                            

                                
        
        self.camera_recorder.handle_recording(frame, self.person_detected)
        self.alert_handler(self.cap.id, self.cap.url)
                            
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
    

    def alert_handler(self, camera_id, camera_url):
            if self.person_detected:
                # if not self.sound_played:
                if self.alert is None:
                    pygame.mixer.music.play(-1)  # Lancer le son en boucle
                    self.sound_played = True
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    self.alert = Alert(camera_id, timestamp, self.api_handler)
                    self.alert.lancer_alerte(camera_id, "Foire de Paris_Stand C10 - Caméra 1", camera_url)

            else:
                if self.alert is not None and not self.camera_recorder.recording:
                    self.sound_played = False
                    pygame.mixer.music.stop()
                    new_url = self.api_handler.upload(self.camera_recorder.video_file_path)[0]['url']
                    self.alert.mettre_a_jour_url_camera(new_url)               
                    self.alert = None

        