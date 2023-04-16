import os
import time

from threading import Thread
from dotenv import load_dotenv
from twilio.rest import Client
from time import sleep

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBERS = ["+33622876337"]


class Lib():
    def __init__(self) -> None:
        pass

    @staticmethod
    def maintain_fps(frame_time, start_time):
        elapsed_time = time.time() - start_time
        if elapsed_time < frame_time:
            time.sleep(frame_time - elapsed_time)
    
    @staticmethod
    def send_sms(message):
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            for phone_number in RECIPIENT_PHONE_NUMBERS:
                client.messages.create(
                    body=message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=phone_number
                )
        except:
            pass

    @staticmethod    
    def convert_polygons(data):
        converted_polygons = []
        
        for polygon in data["polygons"]:
            converted_points = []
            
            for point in polygon["points"]:
                converted_points.append(tuple(point))
            
            converted_polygons.append(converted_points)
        
        return converted_polygons





