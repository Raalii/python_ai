from threading import Thread
import cv2

class CameraStream:
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
