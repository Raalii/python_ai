from threading import Lock
import cv2
import uuid
import ffmpeg

class CameraRecorder:
    def __init__(self, video_file_path, fps, frame_size, api_handler):
        self.video_file_path = video_file_path
        self.fps = fps
        self.frame_size = frame_size
        self.video_writer = None
        self.recording = False
        self.lock = Lock()
        self.delay_counter = 0
        self.delay_seconds = 2
        self.api_handler = api_handler
        self.fourcc = cv2.VideoWriter_fourcc(*'x264')

    
    def start_recording(self, frame):
        with self.lock:
            if not self.recording:
                # print(frame.shape)
                self.video_writer = cv2.VideoWriter(self.video_file_path, self.fourcc, self.fps, (704, 576))
                self.recording = True
                print("Enregistrement vidéo démarré.")

    
    def record_frame(self, frame):
        with self.lock:
            if self.recording:
                self.video_writer.write(frame)

    def stop_recording(self):
        with self.lock:
            if self.recording:
                self.video_writer.release()
                self.video_writer = None
                self.recording = False
                # self.convert_video(self.video_file_path, f'new_{self.video_file_path}')
                # id_collection = uuid.uuid4()           
                # self.api_handler.add_video_to_collection(id_collection, self.video_file_path)
                print("Enregistrement vidéo arrêté.")


    
    def release(self):
        self.stop_recording()

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