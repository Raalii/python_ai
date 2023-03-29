from camera.CameraStream import CameraStream
from ai.PersonDetector import PersonDetector
from lib.lib import Lib
import time
import cv2


def main():
    # Initialise la capture vidéo
    cap = CameraStream(src="rtsp://admin:FIGUE95140@192.168.1.120:554/cam/realmonitor?channel=1&subtype=0&unicast=true").start()

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

        Lib.maintain_fps(frame_time, start_time)    
        cv2.imshow("frame", frame)
        if cv2.waitKey(60) == ord("q"):
            break


    cap.release()
    cv2.destroyAllWindows()



main()