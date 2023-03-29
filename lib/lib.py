import time
from twilio.rest import Client
from dotenv import load_dotenv
import os


load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBERS = ["+330788573854"]


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


