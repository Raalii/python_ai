import os
import time

import cv2
from ai.PersonDetector import PersonDetector
from api.Strapi import StrapiClient
from camera.CameraStream import CameraStream
from api.WebhookHandler import WebhookHandler
from dotenv import load_dotenv
from lib.lib import Lib
from multiprocessing import Process
from threading import Thread

load_dotenv()


def main():
    server = WebhookHandler()
    webhook_server_thread = Thread(target=server.run)
    webhook_server_thread.daemon = True
    webhook_server_thread.start()
    api = StrapiClient(os.getenv("BASE_URL_API"))
    
    # Initialise la capture vidéo
    print(api.cameras[0]["polygons"])   
    print(api.cameras[0]["id"])
    print(api.cameras[0]["url"])

    # TODO : gérer les classes pour utiliser plusieurs flux vidéos
    cap = CameraStream(api.cameras[0]["id"], api.cameras[0]["url"], Lib.convert_polygons(api.cameras[0]) ).start()

    weights_path = "yolov4-tiny.weights"
    config_path = "yolov4-tiny.cfg"
    names_path = "coco.names"
    print(cap.polygons)
    # Crée une instance de la classe PersonDetector
    person_detector = PersonDetector(weights_path, config_path, names_path)
    
    desired_fps = 20
    frame_time = 1.0 / desired_fps

    while True:
        start_time = time.time()
        frame = person_detector.detect_persons_in_polygons(cap.read(), cap.polygons)
        for polygon in cap.polygons:
            frame = person_detector.draw_detection_zone(frame, polygon)

        Lib.maintain_fps(frame_time, start_time)    
        cv2.imshow("frame", frame)
        if cv2.waitKey(60) == ord("q"):
            break


    cap.release()
    cv2.destroyAllWindows()


main()