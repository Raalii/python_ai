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
    api_handler = StrapiClient(os.getenv("BASE_URL_API"))

    # Initialise la capture vidéo
    print(api_handler.cameras[0]["polygons"])
    print(api_handler.cameras[0]["id"])
    print(api_handler.cameras[0]["url"])

    # TODO : gérer les classes pour utiliser plusieurs flux vidéos
    cap = CameraStream(api_handler.cameras[0]["id"], api_handler.cameras[0]
                       ["url"], Lib.convert_polygons(api_handler.cameras[0])).start()

    server = WebhookHandler(cap)
    webhook_server_thread = Thread(target=server.run)
    webhook_server_thread.daemon = True

    webhook_server_thread.start()
    weights_path = "yolov4-tiny.weights"
    config_path = "yolov4-tiny.cfg"
    names_path = "coco.names"
    print(server.strapi_webhook_handler.cameras.polygons)
    # Crée une instance de la classe PersonDetector
    person_detector = PersonDetector(
        weights_path, config_path, names_path, api_handler, cap)

    desired_fps = 10
    frame_time = 1.0 / desired_fps

    while True:
        start_time = time.time()
        frame = person_detector.detect_persons_in_polygons(
            server.strapi_webhook_handler.cameras.read(), server.strapi_webhook_handler.cameras.polygons)
        for polygon in server.strapi_webhook_handler.cameras.polygons:
            frame = person_detector.draw_detection_zone(frame, polygon)

        Lib.maintain_fps(frame_time, start_time)
        cv2.imshow("frame", frame)
        if cv2.waitKey(60) == ord("q"):
            break
        if cv2.waitKey(100) == ord("e"):
            person_detector.person_detected = True
            print("TRUE")
        if cv2.waitKey(100) == ord("t"):
            person_detector.person_detected = False
            print("FALSE")

    cap.release()
    person_detector.camera_recorder.release()
    # api_handler.upload(person_detector.camera_recorder.video_file_path) # ajoute l'enregistrement
    cv2.destroyAllWindows()


main()
